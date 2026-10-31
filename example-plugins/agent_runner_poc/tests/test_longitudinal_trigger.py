import json

import pytest
from agent_runner_poc.handlers.longitudinal_trigger import LongitudinalCareAdvisorTrigger

from canvas_sdk.effects import EffectType
from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.test_utils.factories import NoteFactory, PatientFactory
from canvas_sdk.v1.data.note import CurrentNoteStateEvent, NoteStates


def _state_change(state: NoteStates, **context: object) -> Event:
    """A note state change event; the current-state view is a plain table in tests."""
    note = NoteFactory.create(patient=PatientFactory.create())
    current = CurrentNoteStateEvent.objects.create(note=note, state=state)
    return Event(
        EventRequest(
            type=EventType.NOTE_STATE_CHANGE_EVENT_CREATED,
            target=str(current.id),
            context=json.dumps({"note_id": str(note.id), "patient_id": note.patient.id, **context}),
        )
    )


@pytest.mark.django_db
def test_a_locked_note_starts_the_advisor_on_its_patient() -> None:
    """The advisor reviews a finished encounter, across the patient's visits."""
    event = _state_change(NoteStates.LOCKED)

    [effect] = LongitudinalCareAdvisorTrigger(event).compute()

    assert effect.type == EffectType.RUN_AGENT
    data = json.loads(effect.payload)["data"]
    assert data["agent_id"].endswith(":LongitudinalCareAdvisor")
    assert data["scope"] == "patient"
    assert (data["patient_id"], data["note_id"]) == (
        event.context["patient_id"],
        event.context["note_id"],
    )


@pytest.mark.django_db
@pytest.mark.parametrize("state", [NoteStates.NEW, NoteStates.UNLOCKED])
def test_other_note_states_start_nothing(state: NoteStates) -> None:
    """Only a locked note has a finished encounter to review."""
    assert LongitudinalCareAdvisorTrigger(_state_change(state)).compute() == []


@pytest.mark.django_db
def test_an_event_without_its_note_or_patient_starts_nothing() -> None:
    """The run needs a subject; a malformed event is skipped."""
    event = _state_change(NoteStates.LOCKED, patient_id=None)

    assert LongitudinalCareAdvisorTrigger(event).compute() == []
