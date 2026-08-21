"""Tests for `CommandAPI`, the HTTP endpoint base for writing a single command."""

import json
from base64 import b64encode
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from http import HTTPStatus
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ValidationError as DjangoValidationError

from canvas_sdk.commands import AssessCommand, HistoryOfPresentIllnessCommand, PrescribeCommand
from canvas_sdk.commands.api import CommandAPI
from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.handlers.simple_api import api
from canvas_sdk.v1.data.command import Command

NOTE_UUID = "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
COMMAND_UUID = "1b9d6bcd-bbfd-4b2d-9b5d-ab8dfbbd4bed"


class _HistoryOfPresentIllnessWithMetadata(HistoryOfPresentIllnessCommand):
    """A command extended with a metadata field, the way a plugin would."""

    metadata: dict[str, str] | None = None


class _HistoryOfPresentIllnessAPI(CommandAPI):
    """An endpoint exercising every method the base offers."""

    PREFIX = "/v1"
    model = _HistoryOfPresentIllnessWithMetadata
    path = "/hpi"

    @api.post(path)
    def insert(self) -> list[Response | Effect]:
        return self.originate(self.model)

    @api.patch(f"{path}/<command_uuid>")
    def update(self) -> list[Response | Effect]:
        return self.edit(self.model, self.request.path_params["command_uuid"])

    @api.delete(f"{path}/<command_uuid>")
    def delete(self) -> list[Response | Effect]:
        return self.action(self.model, self.request.path_params["command_uuid"], "delete")

    @api.post(f"{path}/<command_uuid>/commit")
    def commit(self) -> list[Response | Effect]:
        return self.action(self.model, self.request.path_params["command_uuid"], "commit")

    @api.post(f"{path}/<command_uuid>/enter-in-error")
    def enter_in_error(self) -> list[Response | Effect]:
        return self.action(self.model, self.request.path_params["command_uuid"], "enter_in_error")

    @api.post(f"{path}/<command_uuid>/review")
    def review(self) -> list[Response | Effect]:
        # This command is not reviewable, so the base reports that rather than raising.
        return self.action(self.model, self.request.path_params["command_uuid"], "review")


class _NarrativeRequiredCommand(HistoryOfPresentIllnessCommand):
    """A command with a rule its field types do not express, checked as the effect is built."""

    class Meta:
        key = "hpi"
        originate_required_fields = ("narrative",)


class _NarrativeRequiredAPI(CommandAPI):
    """An endpoint over a command whose rule the request cannot satisfy."""

    PREFIX = "/v1"
    model = _NarrativeRequiredCommand
    path = "/narrative-required"

    @api.post(path)
    def insert(self) -> list[Response | Effect]:
        return self.originate(self.model)


class _AssessAPI(CommandAPI):
    """An endpoint over a command with a date and an enum, which JSON carries as strings."""

    PREFIX = "/v1"
    model = AssessCommand
    path = "/assess"

    @api.post(path)
    def insert(self) -> list[Response | Effect]:
        return self.originate(self.model)


class _PrescribeAPI(CommandAPI):
    """An endpoint over the command with the numbers a body can misstate."""

    PREFIX = "/v1"
    model = PrescribeCommand
    path = "/prescribe-command"

    @api.post(path)
    def insert(self) -> list[Response | Effect]:
        return self.originate(self.model)


def _event(
    method: str,
    path: str,
    body: Any = None,
    raw: bytes | None = None,
    headers: Mapping[str, str] | None = None,
) -> Event:
    """A SIMPLE_API_REQUEST event for ``method path``, carrying ``raw`` or ``body`` as JSON."""
    if raw is None:
        raw = b"" if body is None else json.dumps(body).encode()

    return Event(
        EventRequest(
            type=EventType.SIMPLE_API_REQUEST,
            context=json.dumps(
                {
                    "method": method,
                    "path": path,
                    "query_string": "",
                    "body": b64encode(raw).decode(),
                    "headers": dict(headers or {}),
                }
            ),
        )
    )


def _handler(
    method: str,
    path: str,
    body: Any = None,
    raw: bytes | None = None,
    headers: Mapping[str, str] | None = None,
) -> _HistoryOfPresentIllnessAPI:
    """An endpoint handling ``method path``; path params come from the real route match."""
    return _HistoryOfPresentIllnessAPI(_event(method, path, body, raw, headers))


def _split(result: list[Response | Effect]) -> tuple[list[Effect], list[Response]]:
    """Separate a handler's return value into its effects and its responses."""
    return (
        [item for item in result if isinstance(item, Effect)],
        [item for item in result if isinstance(item, Response)],
    )


def _payload(effect: Effect) -> dict[str, Any]:
    """An effect's decoded payload."""
    return json.loads(effect.payload)


def _content(response: Response) -> dict[str, Any]:
    """A response's decoded JSON body."""
    return json.loads(response.content or b"{}")


@contextmanager
def _stored(state: str | None) -> Iterator[MagicMock]:
    """Patch the command table so one command exists, in ``state``. ``None`` means none does.

    Two readers, told apart by what they call rather than by what they filter on: an addressed
    command's state, and whether a chosen id is taken at all.
    """

    def filter(**kwargs: Any) -> MagicMock:
        queryset = MagicMock()
        queryset.values_list.return_value.first.return_value = state
        queryset.exists.return_value = state is not None
        return queryset

    manager = MagicMock()
    manager.filter.side_effect = filter
    with patch.object(Command, "objects", manager):
        yield manager


# ---------------------------------------------------------------- insert


def test_insert_originates_the_command_and_reports_it_created() -> None:
    """A valid body yields an originate effect plus a 201 naming the new command."""
    handler = _handler(
        "POST", "/v1/hpi", {"note_id": NOTE_UUID, "values": {"narrative": "cough x3 days"}}
    )

    effects, responses = _split(handler.insert())

    assert [EffectType.Name(effect.type) for effect in effects] == ["ORIGINATE_HPI_COMMAND"]
    payload = _payload(effects[0])
    assert payload["note"] == NOTE_UUID
    assert payload["data"] == {"narrative": "cough x3 days"}
    assert payload["commit"] is False

    assert responses[0].status_code == HTTPStatus.CREATED
    body = _content(responses[0])
    assert body["command_uuid"] == payload["command"]
    assert body["committed"] is False


def test_insert_commits_when_the_body_asks_for_it() -> None:
    """``commit`` rides the originate effect and is reported back."""
    handler = _handler("POST", "/v1/hpi", {"note_id": NOTE_UUID, "commit": True})

    effects, responses = _split(handler.insert())

    assert _payload(effects[0])["commit"] is True
    assert _content(responses[0])["committed"] is True


def test_insert_keeps_the_envelope_out_of_the_command_data() -> None:
    """``note_uuid`` / ``command_uuid`` address the command; they are not part of its data."""
    handler = _handler(
        "POST", "/v1/hpi", {"note_id": NOTE_UUID, "values": {"narrative": "sore throat"}}
    )

    effects, _ = _split(handler.insert())

    assert _payload(effects[0])["data"] == {"narrative": "sore throat"}


def test_insert_emits_metadata_as_separate_effects() -> None:
    """A model that declares ``metadata`` gets one upsert effect per pair, after the originate."""
    handler = _handler(
        "POST",
        "/v1/hpi",
        {
            "note_id": NOTE_UUID,
            "values": {"narrative": "headache"},
            "metadata": {"source": "test", "channel": "api"},
        },
    )

    effects, _ = _split(handler.insert())

    assert [EffectType.Name(effect.type) for effect in effects] == [
        "ORIGINATE_HPI_COMMAND",
        "UPSERT_COMMAND_METADATA",
        "UPSERT_COMMAND_METADATA",
    ]
    assert _payload(effects[0])["data"] == {"narrative": "headache"}
    assert _payload(effects[1])["data"] == {
        "schema_key": "hpi",
        "command_id": _payload(effects[0])["command"],
        "key": "source",
        "value": "test",
    }


def test_insert_names_the_note_only_as_note_id() -> None:
    """``note_id`` is the endpoint's contract, and the error names it — not the SDK's spelling."""
    handler = _handler(
        "POST", "/v1/hpi", {"note_uuid": NOTE_UUID, "values": {"narrative": "wrong key"}}
    )

    effects, responses = _split(handler.insert())

    assert effects == []
    assert responses[0].status_code == HTTPStatus.BAD_REQUEST
    assert _content(responses[0])["validation_errors"] == [
        {"field": "note_id", "message": "Field required"}
    ]


def test_insert_ignores_a_caller_supplied_command_id_field() -> None:
    """The command is addressed by ``command_id``, not by the model's own field."""
    handler = _handler(
        "POST",
        "/v1/hpi",
        {"note_id": NOTE_UUID, "command_id": COMMAND_UUID, "command_uuid": "ignored"},
    )

    # No command holds the chosen id, so it is free to use.
    with _stored(None):
        effects, responses = _split(handler.insert())

    assert _payload(effects[0])["command"] == COMMAND_UUID
    assert _content(responses[0])["command_uuid"] == COMMAND_UUID


def test_insert_refuses_a_chosen_id_that_is_already_a_commands() -> None:
    """``Command.uuid`` is unique, so reusing an id would fail when the effect is applied.

    Refused here instead, as a conflict the caller can act on: use another id, or recognise that
    the write being retried already landed.
    """
    handler = _handler("POST", "/v1/hpi", {"note_id": NOTE_UUID, "command_id": COMMAND_UUID})

    with _stored("staged"):
        effects, responses = _split(handler.insert())

    assert effects == []
    assert responses[0].status_code == HTTPStatus.CONFLICT
    assert _content(responses[0]) == {
        "error": "a command already has that id",
        "command_uuid": COMMAND_UUID,
        "validation_errors": [],
    }


def test_the_id_check_is_not_scoped_to_the_endpoints_command_type() -> None:
    """An id belonging to a command of another type is still unusable.

    Unlike the lookup the addressed-command routes make, this one filters on the id alone, because
    the uniqueness it is protecting spans the whole table.
    """
    handler = _handler("POST", "/v1/hpi", {"note_id": NOTE_UUID, "command_id": COMMAND_UUID})

    with _stored("staged") as manager:
        handler.insert()

    manager.filter.assert_called_once_with(id=COMMAND_UUID)


def test_insert_refuses_a_chosen_id_that_is_not_a_uuid() -> None:
    """The chosen id becomes the command's identifier, so it has to be able to be one."""
    handler = _handler("POST", "/v1/hpi", {"note_id": NOTE_UUID, "command_id": "not-a-uuid"})

    effects, responses = _split(handler.insert())

    assert effects == []
    assert responses[0].status_code == HTTPStatus.BAD_REQUEST
    assert [error["field"] for error in _content(responses[0])["validation_errors"]] == [
        "command_id"
    ]


def test_insert_without_a_chosen_id_reads_nothing() -> None:
    """The ordinary path does not pay for the check: with no id chosen, there is nothing to check."""
    handler = _handler("POST", "/v1/hpi", {"note_id": NOTE_UUID, "values": {"narrative": "x"}})

    with _stored(None) as manager:
        effects, _responses = _split(handler.insert())

    assert effects
    manager.filter.assert_not_called()


def test_insert_ignores_keys_that_are_not_command_fields() -> None:
    """A key outside the body model is ignored, so a caller can keep display-only data there."""
    handler = _handler(
        "POST",
        "/v1/hpi",
        {
            "note_id": NOTE_UUID,
            "values": {"narrative": "rash"},
            "narrative_label": "Rash (display only)",
        },
    )

    effects, responses = _split(handler.insert())

    assert _payload(effects[0])["data"] == {"narrative": "rash"}
    assert responses[0].status_code == HTTPStatus.CREATED


def test_insert_rejects_a_value_the_command_has_no_field_for() -> None:
    """A misspelled or unknown field is a 400, not a blank command reported as created."""
    handler = _handler(
        "POST", "/v1/hpi", {"note_id": NOTE_UUID, "values": {"narrativ": "typo", "nope": 1}}
    )

    effects, responses = _split(handler.insert())

    assert effects == []
    assert responses[0].status_code == HTTPStatus.BAD_REQUEST
    assert _content(responses[0])["validation_errors"] == [
        {"field": "values.narrativ", "message": "Unexpected field"},
        {"field": "values.nope", "message": "Unexpected field"},
    ]


def test_insert_reports_a_bad_value_against_the_key_the_caller_sent() -> None:
    """A field error names the path the caller used, so it points back into ``values``."""
    handler = _handler("POST", "/v1/hpi", {"note_id": NOTE_UUID, "values": {"narrative": 123}})

    effects, responses = _split(handler.insert())

    assert effects == []
    assert responses[0].status_code == HTTPStatus.BAD_REQUEST
    assert _content(responses[0])["validation_errors"] == [
        {"field": "values.narrative", "message": "Input should be a valid string"}
    ]


@pytest.mark.parametrize(
    argnames="body",
    argvalues=[b"{not json", b'["a", "list"]', b'"a string"'],
    ids=["malformed", "json-array", "json-scalar"],
)
def test_insert_rejects_a_body_that_is_not_a_json_object(body: bytes) -> None:
    """Anything but a JSON object is a 400, and emits nothing. Pins the shared rejection shape."""
    effects, responses = _split(_handler("POST", "/v1/hpi", raw=body).insert())

    assert effects == []
    assert responses[0].status_code == HTTPStatus.BAD_REQUEST
    assert _content(responses[0]) == {
        "error": "Request body must be a JSON object",
        "validation_errors": [],
    }


def test_insert_reports_field_errors_from_the_command_model() -> None:
    """A value the model rejects is a 400 listing the offending field, and emits nothing."""
    handler = _handler(
        "POST", "/v1/hpi", {"note_id": NOTE_UUID, "metadata": {"source": ["not", "a", "string"]}}
    )

    effects, responses = _split(handler.insert())

    assert effects == []
    assert responses[0].status_code == HTTPStatus.BAD_REQUEST
    body = _content(responses[0])
    assert body["error"] == "Validation failed"
    assert body["validation_errors"][0]["field"] == "metadata.source"


def test_insert_reports_errors_raised_when_the_effect_is_built() -> None:
    """A rule checked as the effect is built surfaces as a 400, not an unhandled error."""
    handler = _NarrativeRequiredAPI(
        _event("POST", "/v1/narrative-required", {"note_id": NOTE_UUID})
    )

    effects, responses = _split(handler.insert())

    assert effects == []
    assert responses[0].status_code == HTTPStatus.BAD_REQUEST
    body = _content(responses[0])
    assert body["error"] == "Validation failed"
    assert "'narrative' is required" in body["validation_errors"][0]["message"]


# ---------------------------------------------------------------- update


def test_update_edits_the_command() -> None:
    """A valid body yields an edit effect for the addressed command plus a 200."""
    handler = _handler(
        "PATCH",
        f"/v1/hpi/{COMMAND_UUID}",
        {"note_id": NOTE_UUID, "values": {"narrative": "revised"}},
    )

    with _stored("staged"):
        effects, responses = _split(handler.update())

    assert EffectType.Name(effects[0].type) == "EDIT_HPI_COMMAND"
    payload = _payload(effects[0])
    assert payload["command"] == COMMAND_UUID
    assert payload["data"] == {"narrative": "revised"}
    assert _content(responses[0]) == {"command_uuid": COMMAND_UUID, "mode": "edit"}


def test_update_needs_no_note_because_it_addresses_an_existing_command() -> None:
    """Only origination takes ``note_id``; an edit is addressed by its path and omits it."""
    handler = _handler("PATCH", f"/v1/hpi/{COMMAND_UUID}", {"values": {"narrative": "revised"}})

    with _stored("staged"):
        effects, responses = _split(handler.update())

    assert EffectType.Name(effects[0].type) == "EDIT_HPI_COMMAND"
    assert _payload(effects[0])["data"] == {"narrative": "revised"}
    assert responses[0].status_code == HTTPStatus.OK


def test_update_does_not_honor_a_commit_flag() -> None:
    """``commit`` is not part of the edit body, so it is ignored rather than acted on."""
    handler = _handler(
        "PATCH", f"/v1/hpi/{COMMAND_UUID}", {"values": {"narrative": "revised"}, "commit": True}
    )

    with _stored("staged"):
        effects, responses = _split(handler.update())

    assert [EffectType.Name(effect.type) for effect in effects] == ["EDIT_HPI_COMMAND"]
    assert "commit" not in _payload(effects[0])
    assert _payload(effects[0])["data"] == {"narrative": "revised"}
    assert responses[0].status_code == HTTPStatus.OK


def test_update_is_not_found_when_no_such_command_exists() -> None:
    """An unknown id is a 404 and emits nothing."""
    handler = _handler("PATCH", f"/v1/hpi/{COMMAND_UUID}", {"values": {"narrative": "revised"}})

    with _stored(None):
        effects, responses = _split(handler.update())

    assert effects == []
    assert responses[0].status_code == HTTPStatus.NOT_FOUND


# ---------------------------------------------------------------- delete


def test_delete_removes_a_staged_command() -> None:
    """A staged command yields a delete effect plus a 200."""
    handler = _handler("DELETE", f"/v1/hpi/{COMMAND_UUID}")

    with _stored("staged"):
        effects, responses = _split(handler.delete())

    assert EffectType.Name(effects[0].type) == "DELETE_HPI_COMMAND"
    assert _payload(effects[0]) == {"command": COMMAND_UUID}
    assert _content(responses[0]) == {"command_uuid": COMMAND_UUID, "mode": "delete"}


def test_delete_is_refused_once_the_command_is_committed() -> None:
    """A committed command cannot be deleted; it is entered in error instead."""
    handler = _handler("DELETE", f"/v1/hpi/{COMMAND_UUID}")

    with _stored("committed"):
        effects, responses = _split(handler.delete())

    assert effects == []
    assert responses[0].status_code == HTTPStatus.BAD_REQUEST
    assert _content(responses[0]) == {
        "error": "a committed command cannot be deleted",
        "state": "committed",
        "required_state": "staged",
        "validation_errors": [],
    }


def test_delete_is_not_found_when_no_such_command_exists() -> None:
    """An unknown id is a 404 and emits nothing."""
    handler = _handler("DELETE", f"/v1/hpi/{COMMAND_UUID}")

    with _stored(None):
        effects, responses = _split(handler.delete())

    assert effects == []
    assert responses[0].status_code == HTTPStatus.NOT_FOUND


# ---------------------------------------------------------------- actions


def test_an_action_is_applied_to_the_command() -> None:
    """``commit`` yields the matching id-only effect plus a 200."""
    handler = _handler("POST", f"/v1/hpi/{COMMAND_UUID}/commit")

    with _stored("staged"):
        effects, responses = _split(handler.commit())

    assert EffectType.Name(effects[0].type) == "COMMIT_HPI_COMMAND"
    assert _payload(effects[0]) == {"command": COMMAND_UUID}
    assert _content(responses[0]) == {"command_uuid": COMMAND_UUID, "mode": "commit"}


def test_enter_in_error_voids_the_command() -> None:
    """Enter-in-error yields the matching id-only effect plus a 200."""
    handler = _handler("POST", f"/v1/hpi/{COMMAND_UUID}/enter-in-error")

    with _stored("committed"):
        effects, responses = _split(handler.enter_in_error())

    assert EffectType.Name(effects[0].type) == "ENTER_IN_ERROR_HPI_COMMAND"
    assert _content(responses[0])["mode"] == "enter_in_error"


def test_an_action_the_command_does_not_support_is_rejected() -> None:
    """Only some commands are reviewable; asking the others is a 400, not an unhandled error."""
    handler = _handler("POST", f"/v1/hpi/{COMMAND_UUID}/review")

    with _stored("staged"):
        effects, responses = _split(handler.review())

    assert effects == []
    assert responses[0].status_code == HTTPStatus.BAD_REQUEST
    assert "does not support the 'review' action" in _content(responses[0])["error"]


def test_an_action_is_not_found_when_no_such_command_exists() -> None:
    """An unknown id is a 404 and emits nothing."""
    handler = _handler("POST", f"/v1/hpi/{COMMAND_UUID}/commit")

    with _stored(None):
        effects, responses = _split(handler.commit())

    assert effects == []
    assert responses[0].status_code == HTTPStatus.NOT_FOUND


# ---------------------------------------------------------------- state rules, as 400 responses
#
# The endpoint refuses an action the command's current state does not allow, and says which state it
# found and which one the action needs. The *command* does not check this while building its effect:
# a plugin chaining effects builds a commit before the originate ahead of it has been applied, so
# there is legitimately no row to read yet. An id arriving over HTTP is the opposite case.


def test_committing_an_already_committed_command_is_rejected() -> None:
    """Only a staged command can be committed."""
    handler = _handler("POST", f"/v1/hpi/{COMMAND_UUID}/commit")

    with _stored("committed"):
        effects, responses = _split(handler.commit())

    assert effects == []
    assert responses[0].status_code == HTTPStatus.BAD_REQUEST
    assert _content(responses[0]) == {
        "error": "a committed command cannot be committed",
        "state": "committed",
        "required_state": "staged",
        "validation_errors": [],
    }


def test_entering_a_staged_command_in_error_is_rejected() -> None:
    """Only a committed command can be entered in error; a staged one is deleted instead."""
    handler = _handler("POST", f"/v1/hpi/{COMMAND_UUID}/enter-in-error")

    with _stored("staged"):
        effects, responses = _split(handler.enter_in_error())

    assert effects == []
    assert responses[0].status_code == HTTPStatus.BAD_REQUEST
    assert _content(responses[0]) == {
        "error": "a staged command cannot be entered in error",
        "state": "staged",
        "required_state": "committed",
        "validation_errors": [],
    }


def test_editing_a_committed_command_is_rejected() -> None:
    """Only a staged command can be edited."""
    handler = _handler("PATCH", f"/v1/hpi/{COMMAND_UUID}", {"values": {"narrative": "revised"}})

    with _stored("committed"):
        effects, responses = _split(handler.update())

    assert effects == []
    assert responses[0].status_code == HTTPStatus.BAD_REQUEST
    assert _content(responses[0]) == {
        "error": "a committed command cannot be edited",
        "state": "committed",
        "required_state": "staged",
        "validation_errors": [],
    }


def test_an_action_the_state_allows_still_succeeds() -> None:
    """The state checks reject only what they should — the permitted actions still go through."""
    with _stored("staged"):
        effects, _ = _split(_handler("POST", f"/v1/hpi/{COMMAND_UUID}/commit").commit())
        assert EffectType.Name(effects[0].type) == "COMMIT_HPI_COMMAND"

        effects, _ = _split(_handler("DELETE", f"/v1/hpi/{COMMAND_UUID}").delete())
        assert EffectType.Name(effects[0].type) == "DELETE_HPI_COMMAND"

    with _stored("committed"):
        result = _handler("POST", f"/v1/hpi/{COMMAND_UUID}/enter-in-error").enter_in_error()
        effects, _ = _split(result)
        assert EffectType.Name(effects[0].type) == "ENTER_IN_ERROR_HPI_COMMAND"


# ---------------------------------------------------------------- command-type scoping


def test_lookup_is_scoped_to_the_endpoints_command_type() -> None:
    """The lookup filters on the command type, so an id of another type is simply not found."""
    handler = _handler("DELETE", f"/v1/hpi/{COMMAND_UUID}")

    with _stored("staged") as manager:
        handler.delete()

    manager.filter.assert_called_once_with(id=COMMAND_UUID, schema_key="hpi")


def test_a_malformed_id_is_not_found_rather_than_a_query_error() -> None:
    """An id that cannot be a command's is a 404, not an unhandled error.

    Filtering a ``UUIDField`` with an unparseable value raises Django's ``ValidationError``, which
    the lookup has to absorb. Run against the real manager, since that is the behavior relied on.
    """
    with pytest.raises(DjangoValidationError):
        Command.objects.filter(id="not-a-uuid")

    for result in (
        _handler("DELETE", "/v1/hpi/not-a-uuid").delete(),
        _handler("POST", "/v1/hpi/not-a-uuid/commit").commit(),
        _handler("PATCH", "/v1/hpi/not-a-uuid", {"values": {"narrative": "x"}}).update(),
    ):
        effects, responses = _split(result)

        assert effects == []
        assert responses[0].status_code == HTTPStatus.NOT_FOUND


# --------------------------------------------------------------- what the base leaves out


def test_the_base_leaves_authentication_to_the_endpoint() -> None:
    """`CommandAPI` authenticates nothing: who may write is the plugin's decision, not its own.

    Asserted rather than described because the failure is silent in the wrong direction — a base
    that grew an `authenticate` would quietly take the choice away from every endpoint that mixes
    it in, and the endpoint would still appear to work. Which schemes exist, and what each one
    accepts, is `tests/handlers/simple_api`'s subject rather than this file's.
    """
    assert "authenticate" not in vars(CommandAPI)


# ------------------------------------------------------- what the command class decides for it


def test_a_reviewable_command_supports_review() -> None:
    """The action check reflects the command class, so reviewable commands do expose review."""

    class _PrescribeAPI(CommandAPI):
        PREFIX = "/v1"
        model = PrescribeCommand
        path = "/prescribe"

        @api.post(f"{path}/<command_uuid>/review")
        def review(self) -> list[Response | Effect]:
            return self.action(self.model, self.request.path_params["command_uuid"], "review")

    handler = _PrescribeAPI(_event("POST", f"/v1/prescribe/{COMMAND_UUID}/review"))

    with _stored("staged"):
        effects, responses = _split(handler.review())

    assert EffectType.Name(effects[0].type) == "REVIEW_PRESCRIBE_COMMAND"
    assert isinstance(responses[0], JSONResponse)


def test_a_command_coerces_the_strings_a_body_carries() -> None:
    """A command reads a JSON body directly: an enum arrives as its value, a date as text."""
    handler = _AssessAPI(
        _event(
            "POST",
            "/v1/assess",
            {"note_id": NOTE_UUID, "values": {"status": "improved", "narrative": "better"}},
        )
    )

    effects, responses = _split(handler.insert())

    assert _payload(effects[0])["data"] == {"status": "improved", "narrative": "better"}
    assert responses[0].status_code == HTTPStatus.CREATED


def test_a_command_parses_leniently_so_an_endpoint_needs_no_subclass() -> None:
    """The reason this endpoint can name the command itself.

    Commands are populated from wire formats, so they are the one part of the SDK that parses
    leniently (``_BaseCommand.model_config``). An endpoint once needed a lax subclass per command
    to accept a JSON body; asserted here because deleting that line would bring them all back.
    """
    assert AssessCommand.model_config.get("strict") is False
    assert (
        AssessCommand.model_validate({"status": "improved"}).status is AssessCommand.Status.IMPROVED
    )


def test_a_boolean_sent_for_a_number_is_read_as_one() -> None:
    """The sharp edge of that leniency, pinned rather than assumed.

    Commands parse leniently, and pydantic's lax `int` accepts a boolean: `true` becomes 1. On a
    refill count that is a clinically meaningful coercion of a caller's mistake, so it is asserted
    here — if the SDK ever decides to refuse it (a per-field `strict`, or a validator that rejects
    `bool` for a number), this test is where that decision becomes visible.
    """
    handler = _PrescribeAPI(
        _event("POST", "/v1/prescribe-command", {"note_id": NOTE_UUID, "values": {"refills": True}})
    )

    effects, responses = _split(handler.insert())

    assert _payload(effects[0])["data"] == {"refills": 1}
    assert responses[0].status_code == HTTPStatus.CREATED
