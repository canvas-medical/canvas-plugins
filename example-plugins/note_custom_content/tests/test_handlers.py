import json
from http import HTTPStatus
from unittest.mock import MagicMock, patch

from note_custom_content.handlers.api import NoteContentAPI
from note_custom_content.handlers.refresh import BroadcastCounts
from note_custom_content.handlers.websocket import NoteContentSocket
from note_custom_content.sections import channel_for, counts_for

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.note_custom_content import NoteCustomContent

NOTE_ID = "6d3f5b0e-2c4a-4f8b-9a1d-7e0c5b2f8a31"
COMMAND_ID = "0b1e2f3a-4c5d-4e6f-8a9b-0c1d2e3f4a5b"

SCHEMA_KEYS = ["hpi", "allergy", "vitals", "plan", "diagnose", "clipboard", "unknownKey"]


def _commands(schema_keys: list[str]) -> MagicMock:
    """A stand-in for `Command.objects` whose query yields the given schema keys."""
    objects = MagicMock()
    objects.filter.return_value.values_list.return_value = schema_keys
    return objects


def _api(query_params: dict | None = None, body: dict | None = None) -> NoteContentAPI:
    handler = NoteContentAPI(event=MagicMock())
    handler.request = MagicMock()
    handler.request.query_params = query_params or {}
    handler.request.json.return_value = body or {}
    return handler


def test_counts_for_tallies_each_section_and_the_total() -> None:
    """Every counted command lands in the total; only mapped ones land in a section."""
    with patch("note_custom_content.sections.Command.objects", _commands(SCHEMA_KEYS)):
        counts = counts_for(NOTE_ID)

    assert counts == {
        NoteCustomContent.Section.HISTORY.value: 2,
        NoteCustomContent.Section.EXAM.value: 1,
        NoteCustomContent.Section.ASSESSMENT_PLAN.value: 2,
        NoteCustomContent.Section.INTERNAL.value: 1,
        "total": 7,
    }


def test_counts_for_only_counts_staged_and_committed_commands() -> None:
    """Deleted and entered-in-error commands no longer belong to the note."""
    objects = _commands([])

    with patch("note_custom_content.sections.Command.objects", objects):
        counts_for(NOTE_ID)

    objects.filter.assert_called_once_with(note__id=NOTE_ID, state__in=("staged", "committed"))


def test_banner_is_not_found_for_an_unknown_note() -> None:
    """A banner for a note that does not exist has nothing to show."""
    notes = MagicMock()
    notes.select_related.return_value.filter.return_value.first.return_value = None

    with patch("note_custom_content.handlers.api.Note.objects", notes):
        result = _api({"note_id": NOTE_ID}).banner()

    assert len(result) == 1
    assert result[0].status_code == HTTPStatus.NOT_FOUND


def test_banner_renders_the_patient_provider_and_total() -> None:
    """The banner names the patient and provider and carries the note's total."""
    note = MagicMock()
    note.patient.first_name = "Pat"
    note.patient.last_name = "Example"
    note.provider.first_name = "Doc"
    note.provider.last_name = "Example"
    notes = MagicMock()
    notes.select_related.return_value.filter.return_value.first.return_value = note

    with (
        patch("note_custom_content.handlers.api.Note.objects", notes),
        patch("note_custom_content.handlers.api.counts_for", return_value={"total": 3}),
        patch("note_custom_content.handlers.api.render_to_string", return_value="<p/>") as render,
    ):
        result = _api({"note_id": NOTE_ID}).banner()

    assert result[0].status_code == HTTPStatus.OK
    template, context = render.call_args.args
    assert template == "templates/note_banner.html"
    assert context["patient_name"] == "Pat Example"
    assert context["provider_name"] == "Doc Example"
    assert context["total"] == 3
    assert context["channel"] == channel_for(NOTE_ID)


def test_banner_marks_a_note_without_a_provider_as_unassigned() -> None:
    """A note with no provider still renders, labelled unassigned."""
    note = MagicMock()
    note.provider = None
    notes = MagicMock()
    notes.select_related.return_value.filter.return_value.first.return_value = note

    with (
        patch("note_custom_content.handlers.api.Note.objects", notes),
        patch("note_custom_content.handlers.api.counts_for", return_value={"total": 0}),
        patch("note_custom_content.handlers.api.render_to_string", return_value="<p/>") as render,
    ):
        _api({"note_id": NOTE_ID}).banner()

    assert render.call_args.args[1]["provider_name"] == "Unassigned"


def test_section_is_not_found_without_a_note() -> None:
    """A card cannot count anything without the note it belongs to."""
    result = _api({"section": NoteCustomContent.Section.EXAM.value}).section()

    assert result[0].status_code == HTTPStatus.NOT_FOUND


def test_section_is_not_found_for_an_unknown_section() -> None:
    """A section Canvas does not render has no card."""
    result = _api({"note_id": NOTE_ID, "section": "nope"}).section()

    assert result[0].status_code == HTTPStatus.NOT_FOUND


def test_section_renders_its_label_count_and_button() -> None:
    """The card shows its section's label, count, and the command its button adds."""
    section = NoteCustomContent.Section.EXAM

    with (
        patch("note_custom_content.handlers.api.counts_for", return_value={section.value: 4}),
        patch("note_custom_content.handlers.api.render_to_string", return_value="<p/>") as render,
    ):
        result = _api({"note_id": NOTE_ID, "section": section.value}).section()

    assert result[0].status_code == HTTPStatus.OK
    template, context = render.call_args.args
    assert template == "templates/section_card.html"
    assert context["label"] == "Exam"
    assert context["count"] == 4
    assert context["add_label"] == "Vitals"
    assert context["section"] == section.value
    assert context["channel"] == channel_for(NOTE_ID)


def test_originate_rejects_a_section_it_cannot_add_to() -> None:
    """A section with no button cannot have a command added to it."""
    body = {"note_id": NOTE_ID, "section": NoteCustomContent.Section.INTERNAL.value}

    result = _api(body=body).originate()

    assert len(result) == 1
    assert result[0].status_code == HTTPStatus.BAD_REQUEST


def test_originate_rejects_a_request_without_a_note() -> None:
    """A command cannot be added without the note to add it to."""
    body = {"section": NoteCustomContent.Section.EXAM.value}

    result = _api(body=body).originate()

    assert result[0].status_code == HTTPStatus.BAD_REQUEST


def test_originate_adds_the_sections_command() -> None:
    """The button adds its section's command to the note and reports which."""
    body = {"note_id": NOTE_ID, "section": NoteCustomContent.Section.ASSESSMENT_PLAN.value}

    effect, response = _api(body=body).originate()

    assert effect.type == EffectType.ORIGINATE_PLAN_COMMAND
    assert json.loads(effect.payload)["note"] == NOTE_ID
    assert json.loads(response.content) == {"added": "plan"}


def _socket(logged_in_user: dict | None) -> NoteContentSocket:
    handler = NoteContentSocket(event=MagicMock())
    handler.websocket = MagicMock(logged_in_user=logged_in_user)
    return handler


def test_socket_accepts_staff() -> None:
    """A signed-in staff member may listen for counts."""
    assert _socket({"id": "1", "type": "Staff"}).authenticate() is True


def test_socket_rejects_patients() -> None:
    """A patient may not listen on a note's channel."""
    assert _socket({"id": "1", "type": "Patient"}).authenticate() is False


def test_socket_rejects_anonymous_connections() -> None:
    """A connection with no signed-in user is refused."""
    assert _socket(None).authenticate() is False


def _broadcast(note_id: str | None) -> list:
    handler = BroadcastCounts(event=MagicMock())
    handler.event.target.id = COMMAND_ID
    commands = MagicMock()
    commands.filter.return_value.values_list.return_value.first.return_value = note_id

    with (
        patch("note_custom_content.handlers.refresh.Command.objects", commands),
        patch("note_custom_content.handlers.refresh.counts_for", return_value={"total": 2}),
    ):
        return handler.compute()


def test_broadcasts_the_notes_counts_on_its_channel() -> None:
    """A command change pushes the note's counts out on the note's channel."""
    (effect,) = _broadcast(NOTE_ID)

    assert effect.type == EffectType.SIMPLE_API_WEBSOCKET_BROADCAST
    payload = json.loads(effect.payload)["data"]
    assert payload["channel"] == channel_for(NOTE_ID)
    assert payload["message"] == {"event_type": "counts", "counts": {"total": 2}}


def test_broadcasts_nothing_for_a_command_without_a_note() -> None:
    """A command that belongs to no note has no channel to broadcast on."""
    assert _broadcast(None) == []
