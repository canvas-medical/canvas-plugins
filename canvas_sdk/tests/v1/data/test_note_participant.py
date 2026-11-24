import pytest

from canvas_sdk.test_utils.factories import NoteFactory, NoteParticipantFactory
from canvas_sdk.v1.data import NoteParticipant


@pytest.mark.django_db
def test_note_participant_links_a_note_to_a_patient_contact() -> None:
    """A note lists its participants, and a contact lists the notes it took part in."""
    note = NoteFactory.create()
    participant = NoteParticipantFactory.create(note=note)
    NoteParticipantFactory.create()

    fetched = NoteParticipant.objects.get(note=note)
    contact = fetched.patient_contact_person

    assert fetched.id == participant.id
    assert contact.patient == note.patient
    assert list(note.participants.all()) == [fetched]
    assert list(contact.noteparticipant_set.all()) == [fetched]
