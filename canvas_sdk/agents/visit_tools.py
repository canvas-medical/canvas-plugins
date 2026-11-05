"""SDK-provided tools for a visit's own sections, registered on :data:`standard_tools`.

``originate_reason_for_visit`` and ``originate_hpi`` stage drafts of the Reason for Visit and
History of Present Illness commands on the patient's open note, never committing them. A
reason for visit can name one of the reasons the practice configured, found with
``find_reason_for_visit_codes``, the list the chart's own Reason for Visit command offers.
"""

from typing import Any
from uuid import UUID

from canvas_sdk.agents.standard_tools import _ORIGINATE_RETURNS, standard_tools
from canvas_sdk.agents.tool_registry import EffectField, FilterSpec
from canvas_sdk.commands import HistoryOfPresentIllnessCommand, ReasonForVisitCommand
from canvas_sdk.v1.data import ReasonForVisitSettingCoding


def _offered_reasons() -> Any:
    """The reasons for visit the chart's command offers: the ones the practice selected."""
    return ReasonForVisitSettingCoding.objects.filter(user_selected=True)


@standard_tools.filter_search_tool(
    name="find_reason_for_visit_codes",
    description=(
        "Search the reasons for visit the practice configured, the list the chart's Reason "
        "for Visit command offers. Returns each with `id` (pass it as `coding_id` to "
        "`originate_reason_for_visit`) and `display`. Practice-level config, not "
        "patient-scoped. Use a configured reason when one matches what the visit is for."
    ),
    queryset_factory=lambda args, pid: _offered_reasons(),
    filters={
        "display_contains": FilterSpec(
            type="string",
            description="Case-insensitive match on the reason's name (e.g. 'follow', 'physical').",
            apply=lambda qs, v: qs.filter(display__icontains=v),
        ),
    },
    ordering=("display",),
    limit_default=25,
    limit_max=100,
    limit_description="Maximum results. Defaults to 25.",
    categories=("config_reads",),
    model=ReasonForVisitSettingCoding,
    citable=False,
    returns_description="Array of objects with `id`, `display`, `code`, and `system`.",
    progress_label="Looking up reasons for visit",
)
def _serialize_reason(reason: Any) -> dict[str, Any]:
    """Per-row serializer for find_reason_for_visit_codes."""
    return {
        "id": str(reason.id),
        "display": reason.display,
        "code": reason.code,
        "system": reason.system,
    }


def _is_uuid(value: str) -> bool:
    try:
        UUID(value)
    except ValueError:
        return False
    return True


def _reason_pre_build(arguments: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    """Name the configured reason, or refuse a draft that says nothing."""
    coding_id = arguments.get("coding_id")
    if not coding_id:
        if not str(arguments.get("comment") or "").strip():
            raise ValueError(
                "Give a comment, a coding_id from find_reason_for_visit_codes, or both."
            )
        return {}
    if not _is_uuid(str(coding_id)) or not _offered_reasons().filter(id=coding_id).exists():
        raise ValueError(
            f"No configured reason for visit with id {coding_id!r}. Look one up with "
            "find_reason_for_visit_codes and pass its `id`."
        )
    return {"structured": True, "coding": str(coding_id)}


standard_tools.originate_command_tool(
    name="originate_reason_for_visit",
    description=(
        "Stage a draft Reason for Visit on the patient's open note. NEVER commits. Pass "
        "the reason in the clinician's or patient's words as `comment`, and, when one of "
        "the practice's configured reasons fits, its `coding_id` from "
        "`find_reason_for_visit_codes`. Without a comment the reason's name is used."
    ),
    command_class=ReasonForVisitCommand,
    fields={
        "comment": EffectField(
            type="string",
            description="Why the patient is being seen, in plain words.",
            editable=True,
        ),
        "coding_id": EffectField(
            type="string",
            description="A configured reason's `id` from find_reason_for_visit_codes.",
            pre_build_only=True,
        ),
    },
    pre_build=_reason_pre_build,
    categories=("clinical_writes",),
    returns_description=_ORIGINATE_RETURNS,
)


standard_tools.originate_command_tool(
    name="originate_hpi",
    description=(
        "Stage a draft History of Present Illness on the patient's open note. NEVER "
        "commits. Write the narrative from what the clinician or the visit said; never "
        "add findings the source does not contain."
    ),
    command_class=HistoryOfPresentIllnessCommand,
    fields={
        "narrative": EffectField(
            type="string",
            description="The history of present illness as plain text.",
            required=True,
            editable=True,
        ),
    },
    categories=("clinical_writes",),
    returns_description=_ORIGINATE_RETURNS,
)


standard_tools.set_progress_labels(
    {
        "originate_reason_for_visit": "Drafting the reason for visit",
        "originate_hpi": "Drafting the history of present illness",
    }
)


__exports__ = ()
