"""SDK-provided tools for changing a draft command, registered on :data:`standard_tools`.

``edit_staged_command`` and ``delete_staged_command`` act on a staged, uncommitted
command in the run's own note, of a kind one of the standard ``originate_*`` tools
stages. An edit sets only the fields that tool marks ``editable``, so it never sets a
code or a chart id the tool would have checked before staging; to change one of those,
the draft is deleted and staged again.

They change a kind only when the run is granted a tool that stages it, and only with
approval when that tool needs approval: an agent cannot change what it could not stage,
or change without approval what it could stage only with it.
"""

import json
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from canvas_sdk.agents import history_tools  # noqa: F401  (its originate tools register first)
from canvas_sdk.agents.standard_tools import standard_tools
from canvas_sdk.agents.tool_registry import EffectField, require_patient_id
from canvas_sdk.commands.base import _BaseCommand
from canvas_sdk.v1.data import Command


@dataclass
class DraftKind:
    """A command kind the standard originate tools stage.

    Attributes:
        command_class: The SDK command class.
        editable: The fields an edit may set, by the originate tool's argument names.
        originators: The originate tools that stage it.
    """

    command_class: type[_BaseCommand]
    editable: dict[str, EffectField] = field(default_factory=dict)
    originators: set[str] = field(default_factory=set)


def _draft_kinds() -> dict[str, DraftKind]:
    """Each command key a standard originate tool stages, by key."""
    kinds: dict[str, DraftKind] = {}
    for definition in standard_tools.definitions():
        metadata = standard_tools.metadata_for(definition["name"])
        if metadata.get("kind") != "originate_command":
            continue
        command_class = metadata["command_class"]
        kind = kinds.setdefault(command_class.Meta.key, DraftKind(command_class))
        kind.editable.update(metadata["editable_fields"])
        kind.originators.add(definition["name"])
    return kinds


# Read once every originate tool has registered, which the imports above ensure.
DRAFT_KINDS = _draft_kinds()


def _effect_types(action: str) -> tuple[str, ...]:
    return tuple(
        sorted(
            f"{action}_{kind.command_class.constantized_key()}_COMMAND"
            for kind in DRAFT_KINDS.values()
        )
    )


def _run_staged(command_id: str, ctx: dict[str, Any]) -> int | None:
    """The index in ``ctx["effects"]`` of this run's originate effect for ``command_id``."""
    for index, effect in enumerate(ctx.get("effects") or []):
        if not effect.payload:
            continue
        payload = json.loads(effect.payload)
        if isinstance(payload, dict) and payload.get("command") == command_id and "note" in payload:
            return index
    return None


def _require_grant(key: str, tool: str, ctx: dict[str, Any]) -> None:
    """Raise unless the run may change a ``key`` draft with ``tool``.

    The run's tools (``ctx["parent_tools"]``, the agent's granted registry) must include
    a tool that stages the kind, and when one of those needs approval, ``tool`` must too.
    """
    tools = ctx.get("parent_tools")
    if tools is None:
        raise ValueError("Changing a draft needs the agent's granted tools in the run.")
    granted = {definition["name"] for definition in tools.definitions()}
    originators = DRAFT_KINDS[key].originators & granted
    if not originators:
        raise ValueError(
            f"This agent does not stage {key} commands, so it cannot change them; the "
            "clinician changes it in the note."
        )
    if not tools.requires_approval(tool) and any(
        tools.requires_approval(name) for name in originators
    ):
        raise ValueError(
            f"This agent stages {key} commands only with the clinician's approval, so "
            "it cannot change one without it; the clinician changes it in the note."
        )


def _staged_draft(command_id: str, tool: str, ctx: dict[str, Any]) -> tuple[str, DraftKind]:
    """The key and kind of a staged draft in the run's note that ``tool`` may change.

    Raises when ``command_id`` is not a staged command of the run's patient in the
    run's note, is of a kind no originate tool stages, or is of a kind the run may not
    change with ``tool`` (see :func:`_require_grant`).
    """
    patient_id = require_patient_id(ctx)
    note_id = ctx.get("note_id")
    try:
        UUID(command_id)
    except ValueError:
        raise ValueError(f"{command_id!r} is not a command id.") from None
    command = (
        Command.objects.filter(id=command_id, patient__id=patient_id, note__id=note_id)
        .only("state", "schema_key")
        .first()
        if note_id
        else None
    )
    if command is None:
        raise ValueError("No command with that id in this patient's open note.")
    if command.schema_key not in DRAFT_KINDS:
        raise ValueError(
            f"A {command.schema_key} command is not one these tools change; the "
            "clinician changes it in the note."
        )
    if command.state != "staged":
        raise ValueError(
            f"Only a staged draft can be changed, and this one is {command.state}; the "
            "clinician changes it in the note."
        )
    _require_grant(command.schema_key, tool, ctx)
    return command.schema_key, DRAFT_KINDS[command.schema_key]


def _checked(key: str, editable: dict[str, EffectField], fields: Any) -> dict[str, Any]:
    """``fields`` as Command keyword arguments, refusing any the kind does not allow."""
    if not isinstance(fields, dict) or not fields:
        raise ValueError("Pass `fields` with at least one field to change.")
    if unknown := sorted(set(fields) - set(editable)):
        allowed = ", ".join(editable) or "nothing"
        raise ValueError(
            f"A {key} draft can change only {allowed}, not {', '.join(unknown)}. To "
            "change anything else, delete the draft and stage it again."
        )
    kwargs: dict[str, Any] = {}
    for name, value in fields.items():
        spec = editable[name]
        if value is None:
            raise ValueError(f"Pass a value for {name}.")
        if spec.enum is not None and value not in spec.enum:
            raise ValueError(f"{name} must be one of {', '.join(spec.enum)}.")
        if isinstance(value, int | float) and not isinstance(value, bool):
            if spec.minimum is not None and value < spec.minimum:
                raise ValueError(f"{name} must be at least {spec.minimum}.")
            if spec.maximum is not None and value > spec.maximum:
                raise ValueError(f"{name} must be at most {spec.maximum}.")
        kwargs[spec.command_field or name] = value
    return kwargs


_KINDS_DESCRIPTION = "; ".join(
    f"{key}: {', '.join(kind.editable)}" for key, kind in DRAFT_KINDS.items() if kind.editable
)


@standard_tools.tool(
    name="edit_staged_command",
    description=(
        "Change fields on a staged (uncommitted) draft command in the patient's open "
        "note. NEVER commits. `command_id` is the `command_id` an `originate_*` tool "
        "returned in an earlier run, or a command's `uuid` from `get_note_content`. "
        "Pass `fields` with the new values, named as the matching `originate_*` tool "
        "names its arguments. Only these fields can change, by command: "
        f"{_KINDS_DESCRIPTION}. To change anything else (the medication, condition, "
        "code, or allergen itself), use `delete_staged_command` and stage a new draft. "
        "A draft this run staged cannot be edited; delete it and stage it again."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "command_id": {"type": "string", "description": "The draft command's id."},
            "fields": {
                "type": "object",
                "description": "The fields to change and their new values.",
            },
        },
        "required": ["command_id", "fields"],
    },
    categories=("clinical_writes",),
    effect_types=_effect_types("EDIT"),
    returns_description=(
        "`{ok: true, command_id: <uuid>, command: '<command_key>', changed: [<field>], "
        "committed: false}`."
    ),
    progress_label="Changing a draft",
)
def _edit_staged_command(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """An edit of a staged draft's editable fields."""
    command_id = str(arguments.get("command_id") or "")
    if _run_staged(command_id, ctx) is not None:
        raise ValueError(
            "This run staged that draft, so it cannot be edited yet; delete it with "
            "delete_staged_command and stage it again with the right values."
        )
    key, kind = _staged_draft(command_id, "edit_staged_command", ctx)
    fields = arguments.get("fields")
    kwargs = _checked(key, kind.editable, fields)
    ctx["effects"].append(kind.command_class(command_uuid=command_id, **kwargs).edit())
    return {
        "ok": True,
        "command_id": command_id,
        "command": key,
        "changed": sorted(fields or ()),
        "committed": False,
    }


@standard_tools.tool(
    name="delete_staged_command",
    description=(
        "Delete a staged (uncommitted) draft command from the patient's open note. "
        "`command_id` is the `command_id` an `originate_*` tool returned, in this run "
        "or an earlier one, or a command's `uuid` from `get_note_content`. A committed "
        "command, or one on another note, cannot be deleted. Use it to replace a draft "
        "staged with the wrong item: delete it, then stage the right one."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "command_id": {"type": "string", "description": "The draft command's id."},
        },
        "required": ["command_id"],
    },
    categories=("clinical_writes",),
    effect_types=_effect_types("DELETE"),
    returns_description="`{ok: true, command_id: <uuid>, command: '<command_key>', deleted: true}`.",
    progress_label="Removing a draft",
)
def _delete_staged_command(arguments: dict[str, Any], *, ctx: dict[str, Any]) -> dict[str, Any]:
    """A delete of a staged draft, or of this run's own draft before it is staged."""
    command_id = str(arguments.get("command_id") or "")
    effects: list[Any] = ctx["effects"]
    if (index := _run_staged(command_id, ctx)) is not None:
        # The draft has not reached the note yet, so it is simply not staged.
        effects.pop(index)
        return {"ok": True, "command_id": command_id, "command": None, "deleted": True}
    key, kind = _staged_draft(command_id, "delete_staged_command", ctx)
    effects.append(kind.command_class(command_uuid=command_id).delete())
    return {"ok": True, "command_id": command_id, "command": key, "deleted": True}


__exports__ = ()
