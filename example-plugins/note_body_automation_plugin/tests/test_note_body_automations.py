import json
from unittest.mock import MagicMock, PropertyMock, patch

from note_body_automation_plugin.handlers.note_body_automations import (
    FollowUpPlanAutomation,
    PatientSummaryAutomation,
)

from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.v1.data.note import NoteTypeCategories


def _selected_event(key: str) -> Event:
    """Build the event Canvas fires when the user selects an automation."""
    return Event(
        EventRequest(
            type=EventType.NOTE_BODY_AUTOMATION_SELECTED,
            context=json.dumps({"key": key, "note_id": 1234}),
        )
    )


def _note(category: str) -> MagicMock:
    """Build a note whose type version has the given category."""
    note = MagicMock()
    note.id = "6a1b0d0e-0000-4000-8000-000000000000"
    note.note_type_version.category = category
    return note


def test_patient_summary_configuration() -> None:
    """The summary automation declares its key, title and keywords."""
    assert PatientSummaryAutomation.AUTOMATION_KEY == "patient_summary"
    assert PatientSummaryAutomation.AUTOMATION_TITLE == "Patient summary"
    assert PatientSummaryAutomation.KEYWORDS == ["summary", "overview", "recap"]
    assert PatientSummaryAutomation.PRIORITY == 1


def test_patient_summary_opens_a_modal() -> None:
    """Selecting the summary automation returns one modal effect."""
    automation = PatientSummaryAutomation(_selected_event("patient_summary"))

    effects = automation.compute()

    assert len(effects) == 1
    payload = json.loads(effects[0].payload)
    assert payload["data"]["target"] == "right_chart_pane"
    assert payload["data"]["title"] == "Patient summary"


def test_follow_up_plan_is_visible_for_encounter_notes() -> None:
    """The follow-up automation shows in encounter notes."""
    automation = FollowUpPlanAutomation(_selected_event("follow_up_plan"))
    with patch.object(
        type(automation),
        "note",
        new_callable=PropertyMock,
        return_value=_note(NoteTypeCategories.ENCOUNTER),
    ):
        assert automation.visible() is True


def test_follow_up_plan_is_hidden_for_other_note_types() -> None:
    """The follow-up automation stays hidden in letters."""
    automation = FollowUpPlanAutomation(_selected_event("follow_up_plan"))
    with patch.object(
        type(automation),
        "note",
        new_callable=PropertyMock,
        return_value=_note(NoteTypeCategories.LETTER),
    ):
        assert automation.visible() is False


def test_follow_up_plan_is_hidden_without_a_note() -> None:
    """The follow-up automation stays hidden when the note is missing."""
    automation = FollowUpPlanAutomation(_selected_event("follow_up_plan"))
    with patch.object(type(automation), "note", new_callable=PropertyMock, return_value=None):
        assert automation.visible() is False


def test_follow_up_plan_originates_without_a_line_number() -> None:
    """The Plan command carries line_number -1, so Canvas positions it."""
    note = _note(NoteTypeCategories.ENCOUNTER)
    automation = FollowUpPlanAutomation(_selected_event("follow_up_plan"))
    with patch.object(type(automation), "note", new_callable=PropertyMock, return_value=note):
        effects = automation.compute()

    assert len(effects) == 1
    payload = json.loads(effects[0].payload)
    assert payload["note"] == note.id
    assert payload["data"]["narrative"] == "Follow up in 2 weeks."
    assert payload["line_number"] == -1


def test_follow_up_plan_returns_nothing_without_a_note() -> None:
    """A missing note produces no effects rather than an error."""
    automation = FollowUpPlanAutomation(_selected_event("follow_up_plan"))
    with patch.object(type(automation), "note", new_callable=PropertyMock, return_value=None):
        assert automation.compute() == []
