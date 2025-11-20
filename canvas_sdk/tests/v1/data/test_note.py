from canvas_sdk.v1.data.note import CurrentNoteStateEvent, NoteStates


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
