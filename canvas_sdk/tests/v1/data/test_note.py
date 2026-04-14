import hashlib
import json

from canvas_sdk.v1.data.note import CurrentNoteStateEvent, Note, NoteStates


def _md5(body: object) -> str:
    return hashlib.md5(json.dumps(body, sort_keys=True).encode("utf-8")).hexdigest()


def test_body_checksum_returns_hex_string() -> None:
    """body_checksum returns a 32-character lowercase hex MD5 digest."""
    note = Note()
    note.body = [{"type": "text", "value": "hello"}]
    checksum = note.body_checksum()

    assert isinstance(checksum, str)
    assert len(checksum) == 32
    assert checksum == checksum.lower()


def test_body_checksum_is_deterministic() -> None:
    """Same body always produces the same checksum."""
    note = Note()
    note.body = [{"type": "text", "value": "hello"}]

    assert note.body_checksum() == note.body_checksum()


def test_body_checksum_differs_for_different_bodies() -> None:
    """Different body content produces different checksums."""
    note_a = Note()
    note_a.body = [{"type": "text", "value": "hello"}]

    note_b = Note()
    note_b.body = [{"type": "text", "value": "world"}]

    assert note_a.body_checksum() != note_b.body_checksum()


def test_body_checksum_key_order_independent() -> None:
    """Dict key order within a body element does not affect the checksum."""
    note_a = Note()
    note_a.body = [{"type": "text", "value": "hello"}]

    note_b = Note()
    note_b.body = [{"value": "hello", "type": "text"}]

    assert note_a.body_checksum() == note_b.body_checksum()


def test_body_checksum_nested_key_order_independent() -> None:
    """Dict key order inside nested objects does not affect the checksum."""
    note_a = Note()
    note_a.body = [
        {
            "data": {"id": 2, "commandUuid": "2f44f4d6-8b40-4bf0-be35-2afc253c0479"},
            "type": "command",
            "value": "diagnose",
        }
    ]

    note_b = Note()
    note_b.body = [
        {
            "value": "diagnose",
            "type": "command",
            "data": {"commandUuid": "2f44f4d6-8b40-4bf0-be35-2afc253c0479", "id": 2},
        }
    ]

    assert note_a.body_checksum() == note_b.body_checksum()


def test_body_checksum_nested_key_order_independent_multiple_items() -> None:
    """Key order independence holds across multiple body elements with nested dicts."""
    note_a = Note()
    note_a.body = [
        {"data": {"id": 1, "commandUuid": "aaa"}, "type": "command", "value": "diagnose"},
        {"type": "text", "value": ""},
        {"data": {"commandUuid": "bbb", "id": 2}, "type": "command", "value": "hpi"},
        {"type": "text", "value": "some notes"},
    ]

    note_b = Note()
    note_b.body = [
        {"value": "diagnose", "type": "command", "data": {"commandUuid": "aaa", "id": 1}},
        {"value": "", "type": "text"},
        {"type": "command", "data": {"id": 2, "commandUuid": "bbb"}, "value": "hpi"},
        {"value": "some notes", "type": "text"},
    ]

    assert note_a.body_checksum() == note_b.body_checksum()


def test_body_checksum_element_order_matters() -> None:
    """Array element order is significant — reordering body items produces a different checksum."""
    note_a = Note()
    note_a.body = [
        {"data": {"id": 1, "commandUuid": "aaa"}, "type": "command", "value": "diagnose"},
        {"type": "text", "value": ""},
        {"data": {"id": 2, "commandUuid": "bbb"}, "type": "command", "value": "hpi"},
        {"type": "text", "value": "some notes"},
    ]

    note_b = Note()
    note_b.body = [
        {"data": {"id": 2, "commandUuid": "bbb"}, "type": "command", "value": "hpi"},
        {"type": "text", "value": ""},
        {"data": {"id": 1, "commandUuid": "aaa"}, "type": "command", "value": "diagnose"},
        {"type": "text", "value": "some notes"},
    ]

    assert note_a.body_checksum() != note_b.body_checksum()


def test_body_checksum_empty_body() -> None:
    """body_checksum works on an empty list body."""
    note = Note()
    note.body = []

    assert note.body_checksum() == _md5([])


def test_body_checksum_matches_expected_md5() -> None:
    """body_checksum output matches a manually computed MD5."""
    body = [{"type": "command", "value": "hpi"}, {"type": "text", "value": ""}]
    note = Note()
    note.body = body

    assert note.body_checksum() == _md5(body)


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
