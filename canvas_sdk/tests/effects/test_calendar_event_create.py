from datetime import datetime

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.calendar import (
    CreateEvent,
    DaysOfWeek,
    DeleteEvent,
    EventRecurrence,
    UpdateEvent,
)


def test_create_event_minimal_required_fields() -> None:
    """Test CreateEvent with only required fields."""
    create = CreateEvent(
        calendar_id="calendar-id",
        title="Patient Appointment",
        starts_at=datetime(2025, 1, 15, 10, 0, 0),
        ends_at=datetime(2025, 1, 15, 11, 0, 0),
    )
    payload = create.apply()
    assert payload.type == EffectType.CALENDAR__EVENT__CREATE
    assert (
        payload.payload
        == '{"data": {"calendar_id": "calendar-id", "title": "Patient Appointment", "starts_at": "2025-01-15T10:00:00", "ends_at": "2025-01-15T11:00:00", "recurrence": "", "recurrence_ends_at": null, "allowed_note_types": null}}'
    )


def test_create_event_with_daily_recurrence() -> None:
    """Test CreateEvent with daily recurrence."""
    create = CreateEvent(
        calendar_id="calendar-id",
        title="Daily Standup",
        starts_at=datetime(2025, 1, 15, 9, 0, 0),
        ends_at=datetime(2025, 1, 15, 9, 30, 0),
        recurrence_frequency=EventRecurrence.Daily,
        recurrence_interval=1,
    )
    payload = create.apply()
    assert payload.type == EffectType.CALENDAR__EVENT__CREATE
    assert (
        payload.payload
        == '{"data": {"calendar_id": "calendar-id", "title": "Daily Standup", "starts_at": "2025-01-15T09:00:00", "ends_at": "2025-01-15T09:30:00", "recurrence": "FREQ=DAILY;INTERVAL=1", "recurrence_ends_at": null, "allowed_note_types": null}}'
    )


def test_create_event_with_weekly_recurrence_and_days() -> None:
    """Test CreateEvent with weekly recurrence on specific days."""
    create = CreateEvent(
        calendar_id="calendar-id",
        title="Weekly Team Meeting",
        starts_at=datetime(2025, 1, 15, 14, 0, 0),
        ends_at=datetime(2025, 1, 15, 15, 0, 0),
        recurrence_frequency=EventRecurrence.Weekly,
        recurrence_interval=1,
        recurrence_days=[DaysOfWeek.Monday, DaysOfWeek.Wednesday, DaysOfWeek.Friday],
    )
    payload = create.apply()
    assert payload.type == EffectType.CALENDAR__EVENT__CREATE
    assert (
        payload.payload
        == '{"data": {"calendar_id": "calendar-id", "title": "Weekly Team Meeting", "starts_at": "2025-01-15T14:00:00", "ends_at": "2025-01-15T15:00:00", "recurrence": "FREQ=WEEKLY;INTERVAL=1;BYDAY=MO,WE,FR", "recurrence_ends_at": null, "allowed_note_types": null}}'
    )


def test_create_event_with_recurrence_end_date() -> None:
    """Test CreateEvent with recurrence that ends on a specific date."""
    create = CreateEvent(
        calendar_id="calendar-id",
        title="Temporary Clinic Hours",
        starts_at=datetime(2025, 1, 15, 8, 0, 0),
        ends_at=datetime(2025, 1, 15, 12, 0, 0),
        recurrence_frequency=EventRecurrence.Daily,
        recurrence_interval=1,
        recurrence_ends_at=datetime(2025, 3, 31, 23, 59, 59),
    )
    payload = create.apply()
    assert payload.type == EffectType.CALENDAR__EVENT__CREATE
    assert (
        payload.payload
        == '{"data": {"calendar_id": "calendar-id", "title": "Temporary Clinic Hours", "starts_at": "2025-01-15T08:00:00", "ends_at": "2025-01-15T12:00:00", "recurrence": "FREQ=DAILY;INTERVAL=1", "recurrence_ends_at": "2025-03-31T23:59:59", "allowed_note_types": null}}'
    )


def test_create_event_with_allowed_note_types() -> None:
    """Test CreateEvent with allowed note types."""
    create = CreateEvent(
        calendar_id="calendar-id",
        title="Specialist Consultation",
        starts_at=datetime(2025, 1, 15, 10, 0, 0),
        ends_at=datetime(2025, 1, 15, 11, 0, 0),
        allowed_note_types=["Progress Note", "SOAP Note"],
    )
    payload = create.apply()
    assert payload.type == EffectType.CALENDAR__EVENT__CREATE
    assert (
        payload.payload
        == '{"data": {"calendar_id": "calendar-id", "title": "Specialist Consultation", "starts_at": "2025-01-15T10:00:00", "ends_at": "2025-01-15T11:00:00", "recurrence": "", "recurrence_ends_at": null, "allowed_note_types": ["Progress Note", "SOAP Note"]}}'
    )


def test_create_event_with_all_fields() -> None:
    """Test CreateEvent with all fields populated."""
    create = CreateEvent(
        calendar_id="calendar-id",
        title="Recurring Appointment",
        starts_at=datetime(2025, 1, 15, 13, 0, 0),
        ends_at=datetime(2025, 1, 15, 14, 0, 0),
        recurrence_frequency=EventRecurrence.Weekly,
        recurrence_interval=2,
        recurrence_days=[DaysOfWeek.Tuesday, DaysOfWeek.Thursday],
        recurrence_ends_at=datetime(2025, 12, 31, 23, 59, 59),
        allowed_note_types=["Follow-up Note"],
    )
    payload = create.apply()
    assert payload.type == EffectType.CALENDAR__EVENT__CREATE
    assert (
        payload.payload
        == '{"data": {"calendar_id": "calendar-id", "title": "Recurring Appointment", "starts_at": "2025-01-15T13:00:00", "ends_at": "2025-01-15T14:00:00", "recurrence": "FREQ=WEEKLY;INTERVAL=2;BYDAY=TU,TH", "recurrence_ends_at": "2025-12-31T23:59:59", "allowed_note_types": ["Follow-up Note"]}}'
    )


def test_create_event_with_uuid_calendar_id() -> None:
    """Test CreateEvent with UUID string for calendar_id."""
    create = CreateEvent(
        calendar_id="12345678-1234-5678-1234-567812345678",
        title="Appointment",
        starts_at=datetime(2025, 1, 15, 10, 0, 0),
        ends_at=datetime(2025, 1, 15, 11, 0, 0),
    )
    payload = create.apply()
    assert payload.type == EffectType.CALENDAR__EVENT__CREATE
    assert (
        payload.payload
        == '{"data": {"calendar_id": "12345678-1234-5678-1234-567812345678", "title": "Appointment", "starts_at": "2025-01-15T10:00:00", "ends_at": "2025-01-15T11:00:00", "recurrence": "", "recurrence_ends_at": null, "allowed_note_types": null}}'
    )


def test_update_event_minimal_required_fields() -> None:
    """Test UpdateEvent with only required fields."""
    update = UpdateEvent(
        event_id="event-id",
        title="Updated Appointment",
        starts_at=datetime(2025, 1, 15, 11, 0, 0),
        ends_at=datetime(2025, 1, 15, 12, 0, 0),
    )
    payload = update.apply()
    assert payload.type == EffectType.CALENDAR__EVENT__UPDATE
    assert (
        payload.payload
        == '{"data": {"event_id": "event-id", "title": "Updated Appointment", "starts_at": "2025-01-15T11:00:00", "ends_at": "2025-01-15T12:00:00", "recurrence": "", "recurrence_ends_at": null, "allowed_note_types": null}}'
    )


def test_update_event_with_all_fields() -> None:
    """Test UpdateEvent with all fields populated."""
    update = UpdateEvent(
        event_id="event-id",
        title="Updated Recurring Meeting",
        starts_at=datetime(2025, 1, 15, 15, 0, 0),
        ends_at=datetime(2025, 1, 15, 16, 0, 0),
        recurrence_frequency=EventRecurrence.Weekly,
        recurrence_interval=1,
        recurrence_days=[DaysOfWeek.Monday, DaysOfWeek.Friday],
        recurrence_ends_at=datetime(2025, 6, 30, 23, 59, 59),
        allowed_note_types=["Clinical Note", "Progress Note"],
    )
    payload = update.apply()
    assert payload.type == EffectType.CALENDAR__EVENT__UPDATE
    assert (
        payload.payload
        == '{"data": {"event_id": "event-id", "title": "Updated Recurring Meeting", "starts_at": "2025-01-15T15:00:00", "ends_at": "2025-01-15T16:00:00", "recurrence": "FREQ=WEEKLY;INTERVAL=1;BYDAY=MO,FR", "recurrence_ends_at": "2025-06-30T23:59:59", "allowed_note_types": ["Clinical Note", "Progress Note"]}}'
    )


def test_update_event_with_uuid_event_id() -> None:
    """Test UpdateEvent with UUID string for event_id."""
    update = UpdateEvent(
        event_id="87654321-4321-8765-4321-876543218765",
        title="Updated Event",
        starts_at=datetime(2025, 1, 15, 9, 0, 0),
        ends_at=datetime(2025, 1, 15, 10, 0, 0),
    )
    payload = update.apply()
    assert payload.type == EffectType.CALENDAR__EVENT__UPDATE
    assert (
        payload.payload
        == '{"data": {"event_id": "87654321-4321-8765-4321-876543218765", "title": "Updated Event", "starts_at": "2025-01-15T09:00:00", "ends_at": "2025-01-15T10:00:00", "recurrence": "", "recurrence_ends_at": null, "allowed_note_types": null}}'
    )


def test_delete_event_with_uuid() -> None:
    """Test DeleteEvent with UUID string for event_id."""
    delete = DeleteEvent(event_id="87654321-4321-8765-4321-876543218765")
    payload = delete.apply()
    assert payload.type == EffectType.CALENDAR__EVENT__DELETE
    assert payload.payload == '{"data": {"event_id": "87654321-4321-8765-4321-876543218765"}}'
