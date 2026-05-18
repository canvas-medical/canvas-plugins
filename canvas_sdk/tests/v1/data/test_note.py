import hashlib
import json

from canvas_sdk.v1.data.note import CurrentNoteStateEvent, Note, NoteStates


def test_current_note_state_event_editable() -> None:
    """
    The first assertion ensures all note states are accounted for in this test.
    The second assertion specifies whether a given note state should be considered editable.
    """
    note_state_editability = {
        NoteStates.NEW: True,
        NoteStates.PUSHED: True,
        NoteStates.LOCKED: False,
        NoteStates.UNLOCKED: True,
        NoteStates.DELETED: False,
        NoteStates.RELOCKED: False,
        NoteStates.RESTORED: True,
        NoteStates.RECALLED: False,
        NoteStates.UNDELETED: True,
        NoteStates.DISCHARGED: False,
        NoteStates.SCHEDULING: False,
        NoteStates.BOOKED: False,
        NoteStates.CONVERTED: True,
        NoteStates.CANCELLED: False,
        NoteStates.NOSHOW: False,
        NoteStates.REVERTED: False,
        NoteStates.CONFIRM_IMPORT: False,
        NoteStates.SIGNED: False,
    }

    assert len(NoteStates) == len(note_state_editability), (
        "There are note states defined in NoteStates which are not included in this test! Are they editable?"
    )

    current_note_state_event = CurrentNoteStateEvent()
    for state, should_be_considered_editable in note_state_editability.items():
        current_note_state_event.state = state
        assert current_note_state_event.editable() == should_be_considered_editable


def test_body_checksum_returns_md5_of_body() -> None:
    """body_checksum produces an MD5 hex digest of the sorted JSON body."""
    body = [{"type": "text", "value": "hello"}]
    note = Note(body=body)
    expected = hashlib.md5(json.dumps(body, sort_keys=True).encode("utf-8")).hexdigest()
    assert note.body_checksum() == expected


def test_body_checksum_is_stable_for_same_body() -> None:
    """The same body always produces the same checksum."""
    body = [{"type": "command", "data": {"id": 1}}]
    note = Note(body=body)
    assert note.body_checksum() == note.body_checksum()


def test_body_checksum_differs_for_different_bodies() -> None:
    """Different body content produces different checksums."""
    note_a = Note(body=[{"type": "text", "value": "a"}])
    note_b = Note(body=[{"type": "text", "value": "b"}])
    assert note_a.body_checksum() != note_b.body_checksum()
