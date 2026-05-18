import json
from unittest.mock import MagicMock, patch

import arrow
from note_timeline_restrictions.handlers.event_handlers import (
    CHECKSUM_KEY,
    RESTRICTION_EXPIRY_MINUTES,
    RESTRICTION_KEY,
    ExpireNoteRestrictionsCron,
    NoteAccessPermissionsHandler,
    PatientTimelineHandler,
    RestrictNoteOnConcurrentEdit,
    RestrictNoteOnLetterEdit,
    TrackNoteBodyChecksum,
    _clear_restriction_value,
    _restriction_value,
)

from canvas_sdk.effects import EffectType
from canvas_sdk.events import EventType

NOTE_UUID = "aaaaaaaa-0000-0000-0000-000000000001"
META_UUID = "bbbbbbbb-0000-0000-0000-000000000002"
LETTER_UUID = "cccccccc-0000-0000-0000-000000000003"


def _event(
    target_id: str = NOTE_UUID, actor_id: str = "user-1", context: dict | None = None
) -> MagicMock:
    event = MagicMock()
    event.target.id = target_id
    event.actor.id = actor_id
    event.context = context or {}
    return event


def _cron_event() -> MagicMock:
    event = MagicMock()
    event.target.id = arrow.utcnow().isoformat()
    return event


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def test_restriction_value_contains_required_fields() -> None:
    """_restriction_value produces a JSON string with all expected fields."""
    raw = _restriction_value(editor_staff_id="staff-1")
    data = json.loads(raw)
    assert data["active"] is True
    assert data["editor_staff_id"] == "staff-1"
    assert data["blur"] is True
    assert "message" in data
    assert "last_edited_at" in data


def test_restriction_value_accepts_custom_options() -> None:
    """_restriction_value respects blur=False and a custom message."""
    raw = _restriction_value(editor_staff_id="staff-1", blur=False, message="Custom msg")
    data = json.loads(raw)
    assert data["blur"] is False
    assert data["message"] == "Custom msg"


def test_restriction_value_allows_none_editor() -> None:
    """_restriction_value accepts None as editor_staff_id."""
    data = json.loads(_restriction_value(editor_staff_id=None))
    assert data["editor_staff_id"] is None


def test_clear_restriction_value_produces_empty_dict() -> None:
    """_clear_restriction_value produces a JSON string for an empty object."""
    assert json.loads(_clear_restriction_value()) == {}


# ---------------------------------------------------------------------------
# TrackNoteBodyChecksum
# ---------------------------------------------------------------------------


def test_track_note_body_checksum_responds_to_note_created() -> None:
    """Subscribes to NOTE_CREATED."""
    assert EventType.Name(EventType.NOTE_CREATED) == TrackNoteBodyChecksum.RESPONDS_TO


@patch("note_timeline_restrictions.handlers.event_handlers.Note.objects")
def test_track_note_body_checksum_upserts_on_note_created(mock_note: MagicMock) -> None:
    """Stores the body checksum when a note is created."""
    note = MagicMock()
    note.body_checksum.return_value = "abc123"
    mock_note.get.return_value = note

    with patch("note_timeline_restrictions.handlers.event_handlers.NoteEffect") as mock_effect:
        mock_effect.return_value.upsert_metadata.return_value = MagicMock(
            type=EffectType.UPSERT_NOTE_METADATA
        )
        effects = TrackNoteBodyChecksum(event=_event()).compute()

    assert len(effects) == 1
    mock_effect.return_value.upsert_metadata.assert_called_once_with(
        key=CHECKSUM_KEY, value="abc123"
    )


@patch("note_timeline_restrictions.handlers.event_handlers.Note.objects")
def test_track_note_body_checksum_returns_empty_when_note_missing(mock_note: MagicMock) -> None:
    """Returns no effects when the note does not exist."""
    from canvas_sdk.v1.data.note import Note

    mock_note.get.side_effect = Note.DoesNotExist

    assert TrackNoteBodyChecksum(event=_event()).compute() == []


# ---------------------------------------------------------------------------
# RestrictNoteOnConcurrentEdit
# ---------------------------------------------------------------------------


def test_note_restrictions_on_concurrent_edit_responds_to_note_updated() -> None:
    """Subscribes to NOTE_UPDATED."""
    assert EventType.Name(EventType.NOTE_UPDATED) == RestrictNoteOnConcurrentEdit.RESPONDS_TO


@patch("note_timeline_restrictions.handlers.event_handlers.Note.objects")
def test_note_restrictions_on_concurrent_edit_returns_empty_when_note_missing(
    mock_note: MagicMock,
) -> None:
    """Returns no effects when the note does not exist."""
    from canvas_sdk.v1.data.note import Note

    mock_note.get.side_effect = Note.DoesNotExist

    assert RestrictNoteOnConcurrentEdit(event=_event()).compute() == []


@patch("note_timeline_restrictions.handlers.event_handlers.NoteMetadata.objects")
@patch("note_timeline_restrictions.handlers.event_handlers.Note.objects")
def test_note_restrictions_on_concurrent_edit_no_change(
    mock_note: MagicMock, mock_meta: MagicMock
) -> None:
    """Returns only a checksum upsert when the body has not changed."""
    note = MagicMock()
    note.body_checksum.return_value = "same"
    mock_note.get.return_value = note
    mock_meta.filter.return_value.values_list.return_value.first.return_value = "same"

    with patch("note_timeline_restrictions.handlers.event_handlers.NoteEffect"):
        effects = RestrictNoteOnConcurrentEdit(event=_event()).compute()

    assert len(effects) == 1


@patch("note_timeline_restrictions.handlers.event_handlers.NoteMetadata.objects")
@patch("note_timeline_restrictions.handlers.event_handlers.Note.objects")
def test_note_restrictions_on_concurrent_edit_applies_restriction(
    mock_note: MagicMock, mock_meta: MagicMock
) -> None:
    """Returns checksum upsert + restriction upsert + restrictions-updated broadcast when body changed."""
    note = MagicMock()
    note.body_checksum.return_value = "new_checksum"
    mock_note.get.return_value = note
    mock_meta.filter.return_value.values_list.return_value.first.return_value = "old_checksum"

    with patch("note_timeline_restrictions.handlers.event_handlers.NoteEffect"):
        effects = RestrictNoteOnConcurrentEdit(
            event=_event(context={"user": {"id": "user-1"}})
        ).compute()

    assert len(effects) == 3
    assert effects[2].type == EffectType.NOTE_RESTRICTIONS_UPDATED


@patch("note_timeline_restrictions.handlers.event_handlers.NoteMetadata.objects")
@patch("note_timeline_restrictions.handlers.event_handlers.Note.objects")
def test_note_restrictions_on_concurrent_edit_no_baseline_stores_checksum_only(
    mock_note: MagicMock, mock_meta: MagicMock
) -> None:
    """Returns only a checksum upsert when no baseline exists (first save after plugin install)."""
    note = MagicMock()
    note.body_checksum.return_value = "first"
    mock_note.get.return_value = note
    mock_meta.filter.return_value.values_list.return_value.first.return_value = None

    with patch("note_timeline_restrictions.handlers.event_handlers.NoteEffect"):
        effects = RestrictNoteOnConcurrentEdit(event=_event()).compute()

    assert len(effects) == 1


@patch("note_timeline_restrictions.handlers.event_handlers.NoteMetadata.objects")
@patch("note_timeline_restrictions.handlers.event_handlers.Note.objects")
def test_note_restrictions_on_concurrent_edit_uses_user_from_context(
    mock_note: MagicMock, mock_meta: MagicMock
) -> None:
    """The restriction records the editor_staff_id from the event context."""
    note = MagicMock()
    note.body_checksum.return_value = "new"
    mock_note.get.return_value = note
    mock_meta.filter.return_value.values_list.return_value.first.return_value = "old"

    captured_calls: list[tuple[str, str]] = []
    mock_note_effect = MagicMock()

    def _capture_upsert(key: str, value: str) -> MagicMock:
        captured_calls.append((key, value))
        return MagicMock()

    mock_note_effect.upsert_metadata.side_effect = _capture_upsert

    with patch(
        "note_timeline_restrictions.handlers.event_handlers.NoteEffect",
        return_value=mock_note_effect,
    ):
        RestrictNoteOnConcurrentEdit(
            event=_event(context={"user": {"id": "staff-uuid-99"}})
        ).compute()

    restriction_call = next(c for c in captured_calls if c[0] == RESTRICTION_KEY)
    data = json.loads(restriction_call[1])
    assert data["editor_staff_id"] == "staff-uuid-99"


# ---------------------------------------------------------------------------
# RestrictNoteOnLetterEdit
# ---------------------------------------------------------------------------


def test_note_restrictions_on_letter_edit_responds_to_letter_updated() -> None:
    """Subscribes to LETTER_UPDATED."""
    assert EventType.Name(EventType.LETTER_UPDATED) == RestrictNoteOnLetterEdit.RESPONDS_TO


@patch("note_timeline_restrictions.handlers.event_handlers.Letter.objects")
def test_note_restrictions_on_letter_edit_upserts_restriction(mock_letter: MagicMock) -> None:
    """Upserts a restriction on the parent note when a letter is updated."""
    mock_letter.filter.return_value.values_list.return_value.first.return_value = NOTE_UUID

    with patch("note_timeline_restrictions.handlers.event_handlers.NoteEffect"):
        effects = RestrictNoteOnLetterEdit(
            event=_event(target_id=LETTER_UUID, context={"user": {"id": "user-1"}})
        ).compute()

    assert len(effects) == 2
    assert effects[1].type == EffectType.NOTE_RESTRICTIONS_UPDATED


@patch("note_timeline_restrictions.handlers.event_handlers.Letter.objects")
def test_note_restrictions_on_letter_edit_returns_empty_when_letter_missing(
    mock_letter: MagicMock,
) -> None:
    """Returns no effects when the letter's note cannot be found."""
    mock_letter.filter.return_value.values_list.return_value.first.return_value = None

    assert RestrictNoteOnLetterEdit(event=_event(target_id=LETTER_UUID)).compute() == []


@patch("note_timeline_restrictions.handlers.event_handlers.Letter.objects")
def test_note_restrictions_on_letter_edit_works_without_user_context(
    mock_letter: MagicMock,
) -> None:
    """Applies restriction even when no user is in the event context (editor_staff_id is None)."""
    mock_letter.filter.return_value.values_list.return_value.first.return_value = NOTE_UUID

    captured: list[str] = []
    mock_note_effect = MagicMock()

    def _capture_value(key: str, value: str) -> MagicMock:
        captured.append(value)
        return MagicMock()

    mock_note_effect.upsert_metadata.side_effect = _capture_value

    with patch(
        "note_timeline_restrictions.handlers.event_handlers.NoteEffect",
        return_value=mock_note_effect,
    ):
        effects = RestrictNoteOnLetterEdit(
            event=_event(target_id=LETTER_UUID, context={})
        ).compute()

    assert len(effects) == 2
    assert effects[1].type == EffectType.NOTE_RESTRICTIONS_UPDATED
    assert json.loads(captured[0])["editor_staff_id"] is None


# ---------------------------------------------------------------------------
# NoteAccessPermissionsHandler
# ---------------------------------------------------------------------------


def test_access_permissions_responds_to_get_note_restrictions() -> None:
    """Subscribes to GET_NOTE_RESTRICTIONS."""
    assert (
        EventType.Name(EventType.GET_NOTE_RESTRICTIONS) == NoteAccessPermissionsHandler.RESPONDS_TO
    )


@patch("note_timeline_restrictions.handlers.event_handlers.Staff.objects")
@patch("note_timeline_restrictions.handlers.event_handlers.NoteTypeAccessConfig.objects")
@patch("note_timeline_restrictions.handlers.event_handlers.Note.objects")
@patch("note_timeline_restrictions.handlers.event_handlers.NoteMetadata.objects")
def test_access_permissions_restricted_by_note_type_config(
    mock_meta: MagicMock, mock_note: MagicMock, mock_config: MagicMock, mock_staff: MagicMock
) -> None:
    """Returns restricted when the actor's staff ID is not in the note type's allow-list."""
    mock_note.filter.return_value.values_list.return_value.first.return_value = "note-type-uuid-1"
    mock_config.filter.return_value.values_list.return_value.first.return_value = [
        "staff-uuid-allowed"
    ]
    mock_staff.filter.return_value.values_list.return_value.first.return_value = "staff-uuid-other"

    data = json.loads(
        NoteAccessPermissionsHandler(event=_event(actor_id="99")).compute()[0].payload
    )["data"]

    assert data["restrict_access"] is True
    assert data["blur_content"] is True


@patch("note_timeline_restrictions.handlers.event_handlers.Staff.objects")
@patch("note_timeline_restrictions.handlers.event_handlers.NoteTypeAccessConfig.objects")
@patch("note_timeline_restrictions.handlers.event_handlers.Note.objects")
@patch("note_timeline_restrictions.handlers.event_handlers.NoteMetadata.objects")
def test_access_permissions_allowed_by_note_type_config(
    mock_meta: MagicMock, mock_note: MagicMock, mock_config: MagicMock, mock_staff: MagicMock
) -> None:
    """Returns no restriction when the actor's staff ID is in the note type's allow-list."""
    mock_note.filter.return_value.values_list.return_value.first.return_value = "note-type-uuid-1"
    mock_config.filter.return_value.values_list.return_value.first.return_value = [
        "staff-uuid-allowed"
    ]
    mock_meta.filter.return_value.values_list.return_value.first.return_value = None
    mock_staff.filter.return_value.values_list.return_value.first.return_value = (
        "staff-uuid-allowed"
    )

    assert NoteAccessPermissionsHandler(event=_event(actor_id="99")).compute() == []


@patch("note_timeline_restrictions.handlers.event_handlers.NoteTypeAccessConfig.objects")
@patch("note_timeline_restrictions.handlers.event_handlers.Note.objects")
@patch("note_timeline_restrictions.handlers.event_handlers.NoteMetadata.objects")
def test_access_permissions_unrestricted_when_no_config(
    mock_meta: MagicMock, mock_note: MagicMock, mock_config: MagicMock
) -> None:
    """Returns no effects when the note type has no access config and no edit lock."""
    mock_note.filter.return_value.values_list.return_value.first.return_value = "note-type-uuid-2"
    mock_config.filter.return_value.values_list.return_value.first.return_value = None
    mock_meta.filter.return_value.values_list.return_value.first.return_value = None

    assert NoteAccessPermissionsHandler(event=_event(actor_id="99")).compute() == []


@patch("note_timeline_restrictions.handlers.event_handlers.Staff.objects")
@patch("note_timeline_restrictions.handlers.event_handlers.NoteTypeAccessConfig.objects")
@patch("note_timeline_restrictions.handlers.event_handlers.Note.objects")
@patch("note_timeline_restrictions.handlers.event_handlers.NoteMetadata.objects")
def test_access_permissions_restricted_for_other_user(
    mock_meta: MagicMock, mock_note: MagicMock, mock_config: MagicMock, mock_staff: MagicMock
) -> None:
    """Reports note as restricted when the editor is a different staff member."""
    mock_note.filter.return_value.values_list.return_value.first.return_value = "note-type-uuid-2"
    mock_config.filter.return_value.values_list.return_value.first.return_value = (
        None  # no note-type access config
    )
    mock_meta.filter.return_value.values_list.return_value.first.return_value = json.dumps(
        {
            "active": True,
            "editor_staff_id": "staff-uuid-2",
            "blur": True,
            "message": "Editing.",
            "last_edited_at": "...",
        }
    )
    mock_staff.filter.return_value.values_list.return_value.first.return_value = "staff-uuid-1"

    data = json.loads(
        NoteAccessPermissionsHandler(event=_event(actor_id="42")).compute()[0].payload
    )["data"]

    assert data["restrict_access"] is True
    assert data["blur_content"] is True
    assert data["banner_message"] == "Editing."


@patch("note_timeline_restrictions.handlers.event_handlers.Staff.objects")
@patch("note_timeline_restrictions.handlers.event_handlers.NoteTypeAccessConfig.objects")
@patch("note_timeline_restrictions.handlers.event_handlers.Note.objects")
@patch("note_timeline_restrictions.handlers.event_handlers.NoteMetadata.objects")
def test_access_permissions_not_restricted_for_editor(
    mock_meta: MagicMock, mock_note: MagicMock, mock_config: MagicMock, mock_staff: MagicMock
) -> None:
    """The staff member who applied the restriction is not restricted themselves."""
    mock_note.filter.return_value.values_list.return_value.first.return_value = "note-type-uuid-2"
    mock_config.filter.return_value.values_list.return_value.first.return_value = None
    mock_meta.filter.return_value.values_list.return_value.first.return_value = json.dumps(
        {"active": True, "editor_staff_id": "staff-uuid-1", "blur": True, "last_edited_at": "..."}
    )
    mock_staff.filter.return_value.values_list.return_value.first.return_value = "staff-uuid-1"

    data = json.loads(
        NoteAccessPermissionsHandler(event=_event(actor_id="42")).compute()[0].payload
    )["data"]

    assert data["restrict_access"] is False
    assert data["blur_content"] is False
    assert data["banner_message"] is None


@patch("note_timeline_restrictions.handlers.event_handlers.Staff.objects")
@patch("note_timeline_restrictions.handlers.event_handlers.NoteTypeAccessConfig.objects")
@patch("note_timeline_restrictions.handlers.event_handlers.Note.objects")
@patch("note_timeline_restrictions.handlers.event_handlers.NoteMetadata.objects")
def test_access_permissions_inactive_restriction_is_unrestricted(
    mock_meta: MagicMock, mock_note: MagicMock, mock_config: MagicMock, mock_staff: MagicMock
) -> None:
    """Returns unrestricted when restriction metadata has active=False."""
    mock_note.filter.return_value.values_list.return_value.first.return_value = "note-type-uuid-2"
    mock_config.filter.return_value.values_list.return_value.first.return_value = None
    mock_meta.filter.return_value.values_list.return_value.first.return_value = json.dumps(
        {"active": False, "editor_staff_id": "staff-uuid-2", "last_edited_at": "..."}
    )
    mock_staff.filter.return_value.values_list.return_value.first.return_value = "staff-uuid-1"

    data = json.loads(
        NoteAccessPermissionsHandler(event=_event(actor_id="42")).compute()[0].payload
    )["data"]

    assert data["restrict_access"] is False


# ---------------------------------------------------------------------------
# ExpireNoteRestrictionsCron
# ---------------------------------------------------------------------------


def test_expire_note_restrictions_cron_schedule() -> None:
    """Cron runs every minute."""
    assert ExpireNoteRestrictionsCron.SCHEDULE == "* * * * *"


def test_expire_note_restrictions_cron_expiry_minutes() -> None:
    """RESTRICTION_EXPIRY_MINUTES is a positive integer."""
    assert isinstance(RESTRICTION_EXPIRY_MINUTES, int)
    assert RESTRICTION_EXPIRY_MINUTES > 0


@patch("note_timeline_restrictions.handlers.event_handlers.NoteMetadata.objects")
def test_expire_note_restrictions_cron_clears_expired(mock_meta: MagicMock) -> None:
    """Clears restriction and emits NoteRestrictionsUpdatedEffect for an expired restriction."""
    old_t = arrow.utcnow().shift(minutes=-(RESTRICTION_EXPIRY_MINUTES + 1)).isoformat()
    mock_meta.filter.return_value.values_list.return_value = [
        (NOTE_UUID, json.dumps({"active": True, "last_edited_at": old_t})),
    ]

    with patch("note_timeline_restrictions.handlers.event_handlers.NoteEffect") as mock_effect:
        mock_effect.return_value.upsert_metadata.return_value = MagicMock()
        effects = ExpireNoteRestrictionsCron(event=_cron_event()).execute()

    assert len(effects) == 2
    assert effects[1].type == EffectType.NOTE_RESTRICTIONS_UPDATED
    mock_effect.return_value.upsert_metadata.assert_called_once_with(
        key=RESTRICTION_KEY, value=json.dumps({})
    )


@patch("note_timeline_restrictions.handlers.event_handlers.NoteMetadata.objects")
def test_expire_note_restrictions_cron_skips_fresh(mock_meta: MagicMock) -> None:
    """Does not touch restrictions that are still within the expiry window."""
    fresh_t = arrow.utcnow().shift(seconds=-30).isoformat()
    mock_meta.filter.return_value.values_list.return_value = [
        (NOTE_UUID, json.dumps({"active": True, "last_edited_at": fresh_t})),
    ]

    with patch("note_timeline_restrictions.handlers.event_handlers.NoteEffect"):
        effects = ExpireNoteRestrictionsCron(event=_cron_event()).execute()

    assert effects == []


@patch("note_timeline_restrictions.handlers.event_handlers.NoteMetadata.objects")
def test_expire_note_restrictions_cron_skips_already_cleared(mock_meta: MagicMock) -> None:
    """Skips entries that have no last_edited_at (already cleared)."""
    mock_meta.filter.return_value.values_list.return_value = [
        (NOTE_UUID, json.dumps({})),
    ]

    with patch("note_timeline_restrictions.handlers.event_handlers.NoteEffect"):
        assert ExpireNoteRestrictionsCron(event=_cron_event()).execute() == []


@patch("note_timeline_restrictions.handlers.event_handlers.NoteMetadata.objects")
def test_expire_note_restrictions_cron_skips_malformed_json(mock_meta: MagicMock) -> None:
    """Skips entries whose value is not valid JSON."""
    mock_meta.filter.return_value.values_list.return_value = [
        (NOTE_UUID, "not-json"),
    ]

    with patch("note_timeline_restrictions.handlers.event_handlers.NoteEffect"):
        assert ExpireNoteRestrictionsCron(event=_cron_event()).execute() == []


@patch("note_timeline_restrictions.handlers.event_handlers.NoteMetadata.objects")
def test_expire_note_restrictions_cron_handles_multiple_notes(mock_meta: MagicMock) -> None:
    """Processes multiple notes, clearing only the expired ones."""
    expired = arrow.utcnow().shift(minutes=-(RESTRICTION_EXPIRY_MINUTES + 1)).isoformat()
    fresh = arrow.utcnow().shift(seconds=-10).isoformat()
    second_uuid = "dddddddd-0000-0000-0000-000000000004"

    mock_meta.filter.return_value.values_list.return_value = [
        (NOTE_UUID, json.dumps({"active": True, "last_edited_at": expired})),
        (second_uuid, json.dumps({"active": True, "last_edited_at": fresh})),
    ]

    with patch("note_timeline_restrictions.handlers.event_handlers.NoteEffect"):
        effects = ExpireNoteRestrictionsCron(event=_cron_event()).execute()

    # Only the expired note produces effects (upsert + broadcast)
    assert len(effects) == 2
    assert effects[1].type == EffectType.NOTE_RESTRICTIONS_UPDATED
    assert json.loads(effects[1].payload)["data"]["note_id"] == NOTE_UUID


# ---------------------------------------------------------------------------
# PatientTimelineHandler
# ---------------------------------------------------------------------------


def test_patient_timeline_handler_responds_to_configuration_event() -> None:
    """Subscribes to PATIENT_TIMELINE__GET_CONFIGURATION."""
    assert (
        EventType.Name(EventType.PATIENT_TIMELINE__GET_CONFIGURATION)
        == PatientTimelineHandler.RESPONDS_TO
    )


@patch("note_timeline_restrictions.handlers.event_handlers.NoteType.objects")
def test_patient_timeline_handler_excludes_message_note_types(mock_nt: MagicMock) -> None:
    """Message note types are excluded from the timeline for all actors."""
    message_type = MagicMock()
    message_type.unique_identifier = "msg-type-uuid"
    mock_nt.filter.return_value = [message_type]

    with patch(
        "note_timeline_restrictions.handlers.event_handlers.PatientTimelineEffect"
    ) as mock_effect:
        mock_effect.return_value.apply.return_value = MagicMock(
            type=EffectType.PATIENT_TIMELINE__CONFIGURATION
        )
        effects = PatientTimelineHandler(event=_event(actor_id="99")).compute()

    assert len(effects) == 1
    mock_effect.assert_called_once_with(excluded_note_types=["msg-type-uuid"])


@patch("note_timeline_restrictions.handlers.event_handlers.NoteType.objects")
def test_patient_timeline_handler_returns_empty_effect_when_no_message_types(
    mock_nt: MagicMock,
) -> None:
    """Passes an empty exclusion list to PatientTimelineEffect when no Message types found."""
    mock_nt.filter.return_value = []

    with patch(
        "note_timeline_restrictions.handlers.event_handlers.PatientTimelineEffect"
    ) as mock_effect:
        mock_effect.return_value.apply.return_value = MagicMock()
        effects = PatientTimelineHandler(event=_event(actor_id="99")).compute()

    mock_effect.assert_called_once_with(excluded_note_types=[])
    assert len(effects) == 1
