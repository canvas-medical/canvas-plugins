from abc import ABC
from http import HTTPStatus
from json import JSONDecodeError, loads
from typing import Any, ClassVar, TypeVar
from uuid import UUID, uuid4

from django.core.exceptions import ValidationError as DjangoValidationError
from pydantic import BaseModel, Field, ValidationError

from canvas_sdk.commands.base import _BaseCommand
from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api import MixedAuthMixin, SimpleAPI
from canvas_sdk.v1.data.command import Command


class _CommandBody(BaseModel):
    """A request body that describes a command, for the routes that address one by path."""

    metadata: dict[str, str] = Field(default_factory=dict)
    values: dict[str, Any] = Field(default_factory=dict)


class _OriginateBody(_CommandBody):
    """A request body that creates a command, which has no path to address it by."""

    note_id: UUID = Field(strict=False)
    command_id: str | None = None
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


class CommandAPI(MixedAuthMixin, SimpleAPI, ABC):
    """Base for an HTTP endpoint that writes one command type.

    Subclasses set :attr:`model` and :attr:`path`, then declare their own routes: route collection
    scans each class's own ``__dict__``, so an inherited decorated method is never registered, and a
    route handler may not reuse a name defined here.
    """

    model: ClassVar[type[_BaseCommand]]
    path: ClassVar[str]

    def originate(self) -> list[Response | Effect]:
        """Originate a new command from the request body.

        The body carries the command's fields, ``note_id``, and optionally ``command_id`` and
        ``commit``. Keys that are not fields of :attr:`model` are ignored.

        Returns:
            The originate effect, one metadata effect per pair, and a ``201`` carrying
            ``command_uuid`` and ``committed``; or a lone ``400``.
        """
        try:
            if (request := self._request(_OriginateBody)) is None:
                return [self._bad_request("Request body must be a JSON object")]

            command_uuid = request.command_id or str(uuid4())
            command = self._command(request.values, command_uuid, note_id=str(request.note_id))
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

    def edit(self) -> list[Response | Effect]:
        """Edit the staged command named by the ``command_uuid`` path parameter.

        The body carries the command's field values as a whole, and is re-validated in full. A
        committed command cannot be edited: enter it in error and originate its replacement.

        Returns:
            The edit effect, one metadata effect per pair, and a ``200``; or a lone ``400`` when the
            body or command is invalid, or ``404`` when no command of this type has that id.
        """
        command_uuid = self._command_uuid()

        try:
            if (request := self._request(_CommandBody)) is None:
                return [self._bad_request("Request body must be a JSON object")]
            if not self._exists(command_uuid):
                return [self._not_found()]

            command = self._command(request.values, command_uuid)
            effects = [command.edit(), *self._metadata_effects(command, request.metadata)]
        except ValidationError as error:
            return [self._bad_request(error)]

        return [*effects, self._ok(command_uuid, "edit")]

    def action(self, action: str) -> list[Response | Effect]:
        """Apply an id-only action to the command named by the ``command_uuid`` path parameter.

        ``delete``, ``commit``, ``enter_in_error``, and ``review`` / ``send`` on the commands whose
        classes support them. Whether the command's state allows the action is its own rule, applied
        as it builds the effect.

        Args:
            action: The effect-building method to call. Each route names its own, so this never
                comes from the request.

        Returns:
            The action's effect and a ``200``; or a lone ``404`` when no command of this type has
            that id, or ``400`` when the action is unsupported or the command's rules refuse it.
        """
        command_uuid = self._command_uuid()
        if not self._exists(command_uuid):
            return [self._not_found()]

        try:
            command = self.model(command_uuid=command_uuid)
            build_effect = getattr(command, action, None)
            if not callable(build_effect):
                return [
                    self._bad_request(
                        f"{self.model.__name__} does not support the '{action}' action"
                    )
                ]
            effect = build_effect()
        except ValidationError as error:
            return [self._bad_request(error)]

        return [effect, self._ok(command_uuid, action)]

    def _request(self, body_model: type[_Body]) -> _Body | None:
        """Split the request body into the envelope ``body_model`` declares and the command's values.

        What remains once the envelope keys are removed is filtered to :attr:`model`'s fields, so a
        display-only key, or one the route does not honor, is ignored rather than reaching the
        command.

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

        remaining: dict[str, Any] = dict(body)
        envelope = {
            key: remaining.pop(key)
            for key in body_model.model_fields
            if key != "values" and key in remaining
        }
        fields = set(self.model.model_fields)

        return body_model.model_validate(
            {
                **envelope,
                "values": {key: value for key, value in remaining.items() if key in fields},
            }
        )

    def _command_uuid(self) -> str:
        """Return the ``command_uuid`` path parameter, or an empty string when the route has none."""
        return (self.request.path_params.get("command_uuid") or "").strip()

    def _command(
        self, values: dict[str, Any], command_uuid: str, note_id: str | None = None
    ) -> _BaseCommand:
        """Build a validated command from a parsed body's field values.

        Args:
            values: The command's field values.
            command_uuid: The id to assign to the command.
            note_id: The note to write into. Only origination needs it, since an edit addresses a
                command that already has one.

        Returns:
            The validated command, with the addressing fields kept out of the emitted data.

        Raises:
            ValidationError: If the values do not satisfy the command model.
        """
        command = self.model.model_validate(
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

    def _exists(self, command_uuid: str) -> bool:
        """Report whether a command of this endpoint's type has this id.

        State is not read here — whether it allows an action is the command's own rule.

        Args:
            command_uuid: The id to look up.

        Returns:
            True when such a command exists, otherwise False.
        """
        try:
            return Command.objects.filter(id=command_uuid, schema_key=self.model.Meta.key).exists()
        except DjangoValidationError:
            return False

    def _ok(self, command_uuid: str, mode: str) -> Response:
        """Return a ``200`` naming the command that was acted on and the action taken."""
        return JSONResponse({"command_uuid": command_uuid, "mode": mode})

    def _not_found(self) -> Response:
        """Return a ``404`` for an id matching no command of this endpoint's type."""
        return JSONResponse(
            {"error": f"No {self.model.Meta.key} command with that id"},
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
