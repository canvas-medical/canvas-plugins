import hashlib
import json
import uuid

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


def test_body_returns_stored_body_for_legacy_notes() -> None:
    """For notes without version 2, body returns the stored _body unchanged."""
    body = [{"type": "text", "value": "hello"}]
    note = Note(_body=body)

    assert note._version is None
    assert note.body == body


def test_body_v2_empty_lines() -> None:
    """UUIDs in _body_order without a _body_content entry become empty text nodes."""
    uuid1 = uuid.uuid4()
    uuid2 = uuid.uuid4()
    note = Note(_version=2, _body_order=[uuid1, uuid2], _body_content={})

    assert note.body == [
        {"type": "text", "value": ""},
        {"type": "text", "value": ""},
    ]


def test_body_v2_text_lines() -> None:
    """Text entries in _body_content are converted to text nodes with their values."""
    uuid1 = uuid.uuid4()
    uuid2 = uuid.uuid4()
    note = Note(
        _version=2,
        _body_order=[uuid1, uuid2],
        _body_content={
            str(uuid1): {"type": "text", "value": "hello"},
            str(uuid2): {"type": "text", "value": "world"},
        },
    )

    assert note.body == [
        {"type": "text", "value": "hello"},
        {"type": "text", "value": "world"},
    ]


def test_body_v2_command_lines() -> None:
    """Command entries are converted to command nodes preserving their value."""
    line_uuid = uuid.uuid4()
    note = Note(
        _version=2,
        _body_order=[line_uuid],
        _body_content={str(line_uuid): {"type": "command", "value": "plan"}},
    )

    assert note.body == [{"type": "command", "value": "plan"}]


def test_body_v2_mixed_content_preserves_order() -> None:
    """Empty lines, commands, and text are converted maintaining _body_order."""
    empty_uuid = uuid.uuid4()
    command_uuid = uuid.uuid4()
    text_uuid = uuid.uuid4()
    note = Note(
        _version=2,
        _body_order=[empty_uuid, command_uuid, text_uuid],
        _body_content={
            str(command_uuid): {"type": "command", "value": "plan"},
            str(text_uuid): {"type": "text", "value": "some note text"},
        },
    )

    assert note.body == [
        {"type": "text", "value": ""},
        {"type": "command", "value": "plan"},
        {"type": "text", "value": "some note text"},
    ]


def test_body_v2_empty_order_returns_empty_list() -> None:
    """A version 2 note with no ordered lines produces an empty body."""
    note = Note(_version=2, _body_order=[], _body_content={})

    assert note.body == []


def test_body_checksum_returns_md5_of_body() -> None:
    """body_checksum produces an MD5 hex digest of the sorted JSON body."""
    body = [{"type": "text", "value": "hello"}]
    note = Note(_body=body)
    expected = hashlib.md5(json.dumps(body, sort_keys=True).encode("utf-8")).hexdigest()
    assert note.body_checksum() == expected


def test_body_checksum_is_stable_for_same_body() -> None:
    """The same body always produces the same checksum."""
    body = [{"type": "command", "data": {"id": 1}}]
    note = Note(_body=body)
    assert note.body_checksum() == note.body_checksum()


def test_body_checksum_differs_for_different_bodies() -> None:
    """Different body content produces different checksums."""
    note_a = Note(_body=[{"type": "text", "value": "a"}])
    note_b = Note(_body=[{"type": "text", "value": "b"}])
    assert note_a.body_checksum() != note_b.body_checksum()
