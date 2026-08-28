from abc import ABC
from http import HTTPStatus
from json import JSONDecodeError, loads
from typing import Any, TypeVar
from uuid import UUID, uuid4

from django.core.exceptions import ValidationError as DjangoValidationError
from pydantic import BaseModel, Field, ValidationError
from pydantic_core import InitErrorDetails, PydanticCustomError

from canvas_sdk.commands.base import _BaseCommand
from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api import SimpleAPI
from canvas_sdk.v1.data.command import Command

_REQUIRED_STATE_BY_ACTION = {
    "edit": "staged",
    "delete": "staged",
    "commit": "staged",
    "enter_in_error": "committed",
}

#: For the refusal message, so it reads as a sentence about the command.
_PAST_TENSE = {
    "edit": "edited",
    "delete": "deleted",
    "commit": "committed",
    "enter_in_error": "entered in error",
}


class _CommandBody(BaseModel):
    """A request body that describes a command, for the routes that address one by path."""

    metadata: dict[str, str] = Field(default_factory=dict)
    values: dict[str, Any] = Field(default_factory=dict)


class _OriginateBody(_CommandBody):
    """A request body that creates a command, which has no path to address it by."""

    note_id: UUID = Field(strict=False)
    command_id: UUID | None = Field(default=None, strict=False)
    commit: bool = False


_Body = TypeVar("_Body", bound=_CommandBody)


def _field_errors(error: ValidationError) -> list[dict[str, str]]:
    """Render a validation error as a JSON-serializable list.

    Args:
        error: The error to render.

    Returns:
        One ``{"field", "message"}`` entry per underlying error. ``field`` is empty for errors about
        the command as a whole.
    """
    return [
        {"field": ".".join(str(part) for part in item["loc"]), "message": item["msg"]}
        for item in error.errors()
    ]


def _error_detail(type: str, message: str, field: str, value: Any) -> InitErrorDetails:
    """Describe one thing wrong with a value the caller sent under ``values``.

    Args:
        type: The error's machine-readable kind.
        message: The error, in words.
        field: The field it concerns.
        value: What the caller sent for it.

    Returns:
        The error, reported against ``values.<field>``.
    """
    return InitErrorDetails(
        # The message is passed as context, not as the template, so one containing braces is not
        # read as a placeholder.
        type=PydanticCustomError(type, "{message}", {"message": message}),
        loc=("values", field),
        input=value,
    )


class CommandAPI(SimpleAPI, ABC):
    """A ``SimpleAPI`` that writes commands, for an endpoint to declare its routes on.

    A route handler may not reuse a name this class defines — ``originate``, ``edit`` and ``action``
    """

    def originate(self, model: type[_BaseCommand]) -> list[Response | Effect]:
        """Originate a new command from the request body.

        The body carries the command's fields under ``values``, the note as ``note_id``, and
        optionally ``command_id`` and ``commit``.

        Args:
            model: The command to write.

        Returns:
            The originate effect, one metadata effect per pair, and a ``201`` carrying
            ``command_uuid`` and ``committed``; a ``409`` when the chosen id is taken; or a lone
            ``400``.
        """
        try:
            if (request := self._request(_OriginateBody)) is None:
                return [self._bad_request("Request body must be a JSON object")]

            if request.command_id is not None:
                if self._taken(str(request.command_id)):
                    return [self._id_taken_error_response(str(request.command_id))]
                command_uuid = str(request.command_id)
            else:
                command_uuid = str(uuid4())
            command = self._command(
                model, request.values, command_uuid, note_id=str(request.note_id)
            )
            effects = [
                command.originate(commit=request.commit),
                *self._metadata_effects(command, request.metadata),
            ]
        except ValidationError as error:
            return [self._bad_request(error)]

        return [
            *effects,
            JSONResponse(
                {"command_uuid": command_uuid, "committed": request.commit},
                status_code=HTTPStatus.CREATED,
            ),
        ]

    def edit(self, model: type[_BaseCommand], command_id: str) -> list[Response | Effect]:
        """Edit a staged command.

        The body carries the command's field values as a whole, and is re-validated in full. A
        committed command cannot be edited: enter it in error and originate its replacement.

        Args:
            model: The command to write.
            command_id: The command to edit.

        Returns:
            The edit effect, one metadata effect per pair, and a ``200``; or a lone ``400`` when the
            body or command is invalid, or ``404`` when no command of this type has that id.
        """
        try:
            if (request := self._request(_CommandBody)) is None:
                return [self._bad_request("Request body must be a JSON object")]
            state = self._state(model, command_id)
            if state is None:
                return [self._not_found(model)]
            if state != _REQUIRED_STATE_BY_ACTION["edit"]:
                return [self._wrong_state("edit", state, _REQUIRED_STATE_BY_ACTION["edit"])]

            command = self._command(model, request.values, command_id)
            effects = [command.edit(), *self._metadata_effects(command, request.metadata)]
        except ValidationError as error:
            return [self._bad_request(error)]

        return [*effects, self._ok(command_id, "edit")]

    def action(
        self, model: type[_BaseCommand], command_id: str, action: str
    ) -> list[Response | Effect]:
        """Apply an id-only action to a command.

        ``delete``, ``commit``, ``enter_in_error``, and ``review`` / ``send`` on the commands whose
        classes support them. Whether the command's state allows the action is its own rule, applied
        as it builds the effect.

        Args:
            model: The command to act on.
            command_id: The command to apply it to.
            action: The effect-building method to call.

        Returns:
            The action's effect and a ``200``; or a lone ``404`` when no command of this type has
            that id, or ``400`` when the action is unsupported or the command's rules refuse it.
        """
        state = self._state(model, command_id)
        if state is None:
            return [self._not_found(model)]
        required = _REQUIRED_STATE_BY_ACTION.get(action)
        if required is not None and state != required:
            return [self._wrong_state(action, state, required)]

        try:
            command = model(command_uuid=command_id)
            build_effect = getattr(command, action, None)
            if not callable(build_effect):
                return [
                    self._bad_request(f"{model.__name__} does not support the '{action}' action")
                ]
            effect = build_effect()
        except ValidationError as error:
            return [self._bad_request(error)]

        return [effect, self._ok(command_id, action)]

    def _request(self, body_model: type[_Body]) -> _Body | None:
        """Read the request body as the shape this route accepts.

        Args:
            body_model: The body shape this route accepts.

        Returns:
            The parsed body, or None when the request body is not a JSON object.

        Raises:
            ValidationError: If an envelope key is missing or holds the wrong kind of value.
        """
        try:
            body = loads(self.request.body)
        except (JSONDecodeError, ValueError):
            return None

        if not isinstance(body, dict):
            return None

        return body_model.model_validate(body)

    def _check_errors(self, model: type[_BaseCommand], values: dict[str, Any]) -> None:
        """Check the command's field values, reporting anything wrong with them at once.

        A value must name a field the command has: silently dropping an unknown one would write a
        blank command over a typo.

        Args:
            model: The command the values describe.
            values: The command's field values, as sent under ``values``.

        Raises:
            ValidationError: If a value names a field the command does not have, or holds the wrong
                kind of value for one. Each is reported against ``values.<field>``.
        """
        details = [
            _error_detail("unexpected_field", "Unexpected field", field, values[field])
            for field in sorted(set(values) - set(model.model_fields))
        ]

        if not details:
            try:
                model.model_validate(values)
            except ValidationError as error:
                details = [
                    _error_detail(
                        item["type"],
                        item["msg"],
                        ".".join(map(str, item["loc"])),
                        item.get("input"),
                    )
                    for item in error.errors()
                ]

        if details:
            raise ValidationError.from_exception_data(model.__name__, details)

    def _command(
        self,
        model: type[_BaseCommand],
        values: dict[str, Any],
        command_uuid: str,
        note_id: str | None = None,
    ) -> _BaseCommand:
        """Build a validated command from a parsed body's field values.

        Args:
            model: The command to build.
            values: The command's field values.
            command_uuid: The id to assign to the command.
            note_id: The note to write into. Only origination needs it, since an edit addresses a
                command that already has one.

        Returns:
            The validated command, with the addressing fields kept out of the emitted data.

        Raises:
            ValidationError: If the values do not satisfy the command model.
        """
        self._check_errors(model, values)
        command = model.model_validate(
            {**values, "note_uuid": note_id, "command_uuid": command_uuid}
        )

        for field in ("note_uuid", "command_uuid"):
            command._dirty_keys.discard(field)

        return command

    def _metadata_effects(self, command: _BaseCommand, metadata: dict[str, str]) -> list[Effect]:
        """Build the upsert effects that attach metadata to a command.

        Args:
            command: The command the metadata belongs to.
            metadata: The pairs to attach.

        Returns:
            One upsert effect per pair. Effects apply in order, so these follow the effect that
            creates the command.
        """
        return [command.upsert_metadata(key, value) for key, value in metadata.items()]

    def _state(self, model: type[_BaseCommand], command_id: str) -> str | None:
        """The state of the command this endpoint's type has under this id.

        One query answers both questions the routes ask — whether such a command exists at all, and
        whether it is in a state the requested action is allowed from.

        Args:
            model: The command whose type the id must belong to.
            command_id: The id to look up.

        Returns:
            The command's state, or None when no command of this type has that id. A malformed id
            is None rather than an error: ``Command.id`` is a ``UUIDField``, and filtering one on a
            value that will not parse raises before any query is sent.
        """
        try:
            return (
                Command.objects.filter(id=command_id, schema_key=model.Meta.key)
                .values_list("state", flat=True)
                .first()
            )
        except DjangoValidationError:
            return None

    def _taken(self, command_id: str) -> bool:
        """Whether any command already has this id.

        Args:
            command_id: The id the caller chose.

        Returns:
            True when a command already has it.
        """
        return Command.objects.filter(id=command_id).exists()

    def _id_taken_error_response(self, command_id: str) -> Response:
        """Return a ``409`` for a chosen id that already belongs to a command.

        A conflict rather than a validation error: nothing about the request is malformed, and the
        caller's move is to use a different id — or to recognise that the write it is retrying
        already landed.
        """
        return JSONResponse(
            {
                "error": "a command already has that id",
                "command_uuid": command_id,
                "validation_errors": [],
            },
            status_code=HTTPStatus.CONFLICT,
        )

    def _wrong_state(self, action: str, state: str, required: str) -> Response:
        """Return a ``400`` for an action the command's current state does not allow."""
        return JSONResponse(
            {
                "error": f"a {state} command cannot be {_PAST_TENSE.get(action, action)}",
                "state": state,
                "required_state": required,
                "validation_errors": [],
            },
            status_code=HTTPStatus.BAD_REQUEST,
        )

    def _ok(self, command_id: str, mode: str) -> Response:
        """Return a ``200`` naming the command that was acted on and the action taken."""
        return JSONResponse({"command_uuid": command_id, "mode": mode})

    def _not_found(self, model: type[_BaseCommand]) -> Response:
        """Return a ``404`` for an id matching no command of ``model``'s type."""
        return JSONResponse(
            {"error": f"No {model.Meta.key} command with that id"},
            status_code=HTTPStatus.NOT_FOUND,
        )

    def _bad_request(self, error: str | ValidationError) -> Response:
        """Return a ``400`` for a request the endpoint will not act on.

        Args:
            error: A validation error, or a message describing what was not accepted.

        Returns:
            A ``400`` carrying a summary in ``error`` and a ``validation_errors`` list, empty when
            nothing field-specific was at fault, so every rejection reads the same way.
        """
        field_errors = _field_errors(error) if isinstance(error, ValidationError) else []

        return JSONResponse(
            {
                "error": "Validation failed" if field_errors else str(error),
                "validation_errors": field_errors,
            },
            status_code=HTTPStatus.BAD_REQUEST,
        )


__exports__ = ("CommandAPI",)
