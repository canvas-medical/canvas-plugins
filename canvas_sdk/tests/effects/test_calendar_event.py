from datetime import datetime

import pytest
from pydantic_core import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.calendar import (
    DaysOfWeek,
    Event,
    EventRecurrence,
)


def test_create_event_minimal_required_fields() -> None:
    """Test Event with only required fields."""
    payload = Event(
        calendar_id="calendar-id",
        title="Patient Appointment",
        starts_at=datetime(2025, 1, 15, 10, 0, 0),
        ends_at=datetime(2025, 1, 15, 11, 0, 0),
    ).create()
    assert payload.type == EffectType.CALENDAR__EVENT__CREATE
    assert (
        payload.payload
        == '{"data": {"event_id": null, "calendar_id": "calendar-id", "title": "Patient Appointment", "starts_at": "2025-01-15T10:00:00", "ends_at": "2025-01-15T11:00:00", "recurrence": "", "recurrence_ends_at": null, "allowed_note_types": null}}'
    )


def test_create_event_with_daily_recurrence() -> None:
    """Test Event with daily recurrence."""
    payload = Event(
        calendar_id="calendar-id",
        title="Daily Standup",
        starts_at=datetime(2025, 1, 15, 9, 0, 0),
        ends_at=datetime(2025, 1, 15, 9, 30, 0),
        recurrence_frequency=EventRecurrence.Daily,
        recurrence_interval=1,
    ).create()
    assert payload.type == EffectType.CALENDAR__EVENT__CREATE
    assert (
        payload.payload
        == '{"data": {"event_id": null, "calendar_id": "calendar-id", "title": "Daily Standup", "starts_at": "2025-01-15T09:00:00", "ends_at": "2025-01-15T09:30:00", "recurrence": "FREQ=DAILY;INTERVAL=1", "recurrence_ends_at": null, "allowed_note_types": null}}'
    )


def test_create_event_with_weekly_recurrence_and_days() -> None:
    """Test Event with weekly recurrence on specific days."""
    payload = Event(
        calendar_id="calendar-id",
        title="Weekly Team Meeting",
        starts_at=datetime(2025, 1, 15, 14, 0, 0),
        ends_at=datetime(2025, 1, 15, 15, 0, 0),
        recurrence_frequency=EventRecurrence.Weekly,
        recurrence_interval=1,
        recurrence_days=[DaysOfWeek.Monday, DaysOfWeek.Wednesday, DaysOfWeek.Friday],
    ).create()
    assert payload.type == EffectType.CALENDAR__EVENT__CREATE
    assert (
        payload.payload
        == '{"data": {"event_id": null, "calendar_id": "calendar-id", "title": "Weekly Team Meeting", "starts_at": "2025-01-15T14:00:00", "ends_at": "2025-01-15T15:00:00", "recurrence": "FREQ=WEEKLY;INTERVAL=1;BYDAY=MO,WE,FR", "recurrence_ends_at": null, "allowed_note_types": null}}'
    )


def test_create_event_with_recurrence_end_date() -> None:
    """Test Event with recurrence that ends on a specific date."""
    payload = Event(
        calendar_id="calendar-id",
        title="Temporary Clinic Hours",
        starts_at=datetime(2025, 1, 15, 8, 0, 0),
        ends_at=datetime(2025, 1, 15, 12, 0, 0),
        recurrence_frequency=EventRecurrence.Daily,
        recurrence_interval=1,
        recurrence_ends_at=datetime(2025, 3, 31, 23, 59, 59),
    ).create()
    assert payload.type == EffectType.CALENDAR__EVENT__CREATE
    assert (
        payload.payload
        == '{"data": {"event_id": null, "calendar_id": "calendar-id", "title": "Temporary Clinic Hours", "starts_at": "2025-01-15T08:00:00", "ends_at": "2025-01-15T12:00:00", "recurrence": "FREQ=DAILY;INTERVAL=1", "recurrence_ends_at": "2025-03-31T23:59:59", "allowed_note_types": null}}'
    )


def test_create_event_with_allowed_note_types() -> None:
    """Test Event with allowed note types."""
    payload = Event(
        calendar_id="calendar-id",
        title="Specialist Consultation",
        starts_at=datetime(2025, 1, 15, 10, 0, 0),
        ends_at=datetime(2025, 1, 15, 11, 0, 0),
        allowed_note_types=["100", "101"],
    ).create()
    assert payload.type == EffectType.CALENDAR__EVENT__CREATE
    assert (
        payload.payload
        == '{"data": {"event_id": null, "calendar_id": "calendar-id", "title": "Specialist Consultation", "starts_at": "2025-01-15T10:00:00", "ends_at": "2025-01-15T11:00:00", "recurrence": "", "recurrence_ends_at": null, "allowed_note_types": ["100", "101"]}}'
    )


def test_create_event_with_all_fields() -> None:
    """Test Event with all fields populated."""
    payload = Event(
        calendar_id="calendar-id",
        title="Recurring Appointment",
        starts_at=datetime(2025, 1, 15, 13, 0, 0),
        ends_at=datetime(2025, 1, 15, 14, 0, 0),
        recurrence_frequency=EventRecurrence.Weekly,
        recurrence_interval=2,
        recurrence_days=[DaysOfWeek.Tuesday, DaysOfWeek.Thursday],
        recurrence_ends_at=datetime(2025, 12, 31, 23, 59, 59),
        allowed_note_types=["100"],
    ).create()
    assert payload.type == EffectType.CALENDAR__EVENT__CREATE
    assert (
        payload.payload
        == '{"data": {"event_id": null, "calendar_id": "calendar-id", "title": "Recurring Appointment", "starts_at": "2025-01-15T13:00:00", "ends_at": "2025-01-15T14:00:00", "recurrence": "FREQ=WEEKLY;INTERVAL=2;BYDAY=TU,TH", "recurrence_ends_at": "2025-12-31T23:59:59", "allowed_note_types": ["100"]}}'
    )


def test_create_event_with_uuid_calendar_id() -> None:
    """Test Event with UUID string for calendar_id."""
    payload = Event(
        calendar_id="12345678-1234-5678-1234-567812345678",
        title="Appointment",
        starts_at=datetime(2025, 1, 15, 10, 0, 0),
        ends_at=datetime(2025, 1, 15, 11, 0, 0),
    ).create()
    assert payload.type == EffectType.CALENDAR__EVENT__CREATE
    assert (
        payload.payload
        == '{"data": {"event_id": null, "calendar_id": "12345678-1234-5678-1234-567812345678", "title": "Appointment", "starts_at": "2025-01-15T10:00:00", "ends_at": "2025-01-15T11:00:00", "recurrence": "", "recurrence_ends_at": null, "allowed_note_types": null}}'
    )


def test_update_event_minimal_required_fields() -> None:
    """Test Event with only required fields."""
    payload = Event(
        event_id="event-id",
        title="Updated Appointment",
        starts_at=datetime(2025, 1, 15, 11, 0, 0),
        ends_at=datetime(2025, 1, 15, 12, 0, 0),
    ).update()
    assert payload.type == EffectType.CALENDAR__EVENT__UPDATE
    assert (
        payload.payload
        == '{"data": {"event_id": "event-id", "calendar_id": null, "title": "Updated Appointment", "starts_at": "2025-01-15T11:00:00", "ends_at": "2025-01-15T12:00:00", "recurrence": "", "recurrence_ends_at": null, "allowed_note_types": null}}'
    )


def test_update_event_with_all_fields() -> None:
    """Test Event with all fields populated."""
    payload = Event(
        event_id="event-id",
        title="Updated Recurring Meeting",
        starts_at=datetime(2025, 1, 15, 15, 0, 0),
        ends_at=datetime(2025, 1, 15, 16, 0, 0),
        recurrence_frequency=EventRecurrence.Weekly,
        recurrence_interval=1,
        recurrence_days=[DaysOfWeek.Monday, DaysOfWeek.Friday],
        recurrence_ends_at=datetime(2025, 6, 30, 23, 59, 59),
        allowed_note_types=["Clinical Note", "Progress Note"],
    ).update()
    assert payload.type == EffectType.CALENDAR__EVENT__UPDATE
    assert (
        payload.payload
        == '{"data": {"event_id": "event-id", "calendar_id": null, "title": "Updated Recurring Meeting", "starts_at": "2025-01-15T15:00:00", "ends_at": "2025-01-15T16:00:00", "recurrence": "FREQ=WEEKLY;INTERVAL=1;BYDAY=MO,FR", "recurrence_ends_at": "2025-06-30T23:59:59", "allowed_note_types": ["Clinical Note", "Progress Note"]}}'
    )


def test_update_event_with_uuid_event_id() -> None:
    """Test Event with UUID string for event_id."""
    payload = Event(
        event_id="87654321-4321-8765-4321-876543218765",
        title="Updated Event",
        starts_at=datetime(2025, 1, 15, 9, 0, 0),
        ends_at=datetime(2025, 1, 15, 10, 0, 0),
    ).update()
    assert payload.type == EffectType.CALENDAR__EVENT__UPDATE
    assert (
        payload.payload
        == '{"data": {"event_id": "87654321-4321-8765-4321-876543218765", "calendar_id": null, "title": "Updated Event", "starts_at": "2025-01-15T09:00:00", "ends_at": "2025-01-15T10:00:00", "recurrence": "", "recurrence_ends_at": null, "allowed_note_types": null}}'
    )


def test_delete_event_with_uuid() -> None:
    """Test DeleteEvent with UUID string for event_id."""
    payload = Event(event_id="87654321-4321-8765-4321-876543218765").delete()
    assert payload.type == EffectType.CALENDAR__EVENT__DELETE
    assert (
        payload.payload
        == '{"data": {"event_id": "87654321-4321-8765-4321-876543218765", "calendar_id": null, "title": null, "starts_at": null, "ends_at": null, "recurrence": "", "recurrence_ends_at": null, "allowed_note_types": null}}'
    )


def test_create_event_missing_calendar_id() -> None:
    """Test that creating an event without calendar_id raises ValidationError."""
    event = Event(
        title="Appointment",
        starts_at=datetime(2025, 1, 15, 10, 0, 0),
        ends_at=datetime(2025, 1, 15, 11, 0, 0),
    )
    with pytest.raises(ValidationError) as exc_info:
        event.create()

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["type"] == "missing"
    assert "calendar_id" in errors[0]["msg"]
    assert "required to create an event" in errors[0]["msg"]


def test_create_event_missing_title() -> None:
    """Test that creating an event without title raises ValidationError."""
    event = Event(
        calendar_id="calendar-id",
        starts_at=datetime(2025, 1, 15, 10, 0, 0),
        ends_at=datetime(2025, 1, 15, 11, 0, 0),
    )
    with pytest.raises(ValidationError) as exc_info:
        event.create()

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["type"] == "missing"
    assert "title" in errors[0]["msg"]
    assert "required to create an event" in errors[0]["msg"]


def test_create_event_missing_starts_at() -> None:
    """Test that creating an event without starts_at raises ValidationError."""
    event = Event(
        calendar_id="calendar-id",
        title="Appointment",
        ends_at=datetime(2025, 1, 15, 11, 0, 0),
    )
    with pytest.raises(ValidationError) as exc_info:
        event.create()

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["type"] == "missing"
    assert "starts_at" in errors[0]["msg"]
    assert "required to create an event" in errors[0]["msg"]


def test_create_event_missing_ends_at() -> None:
    """Test that creating an event without ends_at raises ValidationError."""
    event = Event(
        calendar_id="calendar-id",
        title="Appointment",
        starts_at=datetime(2025, 1, 15, 10, 0, 0),
    )
    with pytest.raises(ValidationError) as exc_info:
        event.create()

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["type"] == "missing"
    assert "ends_at" in errors[0]["msg"]
    assert "required to create an event" in errors[0]["msg"]


def test_create_event_missing_multiple_fields() -> None:
    """Test that creating an event with multiple missing fields raises ValidationError with all errors."""
    event = Event(calendar_id="calendar-id")
    with pytest.raises(ValidationError) as exc_info:
        event.create()

    errors = exc_info.value.errors()
    # Should have errors for: title, starts_at, ends_at
    assert len(errors) == 3
    error_messages = [error["msg"] for error in errors]
    assert any("title" in msg for msg in error_messages)
    assert any("starts_at" in msg for msg in error_messages)
    assert any("ends_at" in msg for msg in error_messages)


def test_update_event_missing_event_id() -> None:
    """Test that updating an event without event_id raises ValidationError."""
    event = Event(
        title="Updated Appointment",
        starts_at=datetime(2025, 1, 15, 11, 0, 0),
        ends_at=datetime(2025, 1, 15, 12, 0, 0),
    )
    with pytest.raises(ValidationError) as exc_info:
        event.update()

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["type"] == "missing"
    assert "event_id" in errors[0]["msg"]
    assert "required to update an event" in errors[0]["msg"]


def test_update_event_missing_title() -> None:
    """Test that updating an event without title raises ValidationError."""
    event = Event(
        event_id="event-id",
        starts_at=datetime(2025, 1, 15, 11, 0, 0),
        ends_at=datetime(2025, 1, 15, 12, 0, 0),
    )
    with pytest.raises(ValidationError) as exc_info:
        event.update()

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["type"] == "missing"
    assert "title" in errors[0]["msg"]
    assert "required to update an event" in errors[0]["msg"]


def test_update_event_missing_starts_at() -> None:
    """Test that updating an event without starts_at raises ValidationError."""
    event = Event(
        event_id="event-id",
        title="Updated Appointment",
        ends_at=datetime(2025, 1, 15, 12, 0, 0),
    )
    with pytest.raises(ValidationError) as exc_info:
        event.update()

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["type"] == "missing"
    assert "starts_at" in errors[0]["msg"]
    assert "required to update an event" in errors[0]["msg"]


def test_update_event_missing_ends_at() -> None:
    """Test that updating an event without ends_at raises ValidationError."""
    event = Event(
        event_id="event-id",
        title="Updated Appointment",
        starts_at=datetime(2025, 1, 15, 11, 0, 0),
    )
    with pytest.raises(ValidationError) as exc_info:
        event.update()

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["type"] == "missing"
    assert "ends_at" in errors[0]["msg"]
    assert "required to update an event" in errors[0]["msg"]


def test_update_event_missing_multiple_fields() -> None:
    """Test that updating an event with multiple missing fields raises ValidationError with all errors."""
    event = Event(event_id="event-id")
    with pytest.raises(ValidationError) as exc_info:
        event.update()

    errors = exc_info.value.errors()
    # Should have errors for: title, starts_at, ends_at
    assert len(errors) == 3
    error_messages = [error["msg"] for error in errors]
    assert any("title" in msg for msg in error_messages)
    assert any("starts_at" in msg for msg in error_messages)
    assert any("ends_at" in msg for msg in error_messages)


def test_delete_event_missing_event_id() -> None:
    """Test that deleting an event without event_id raises ValidationError."""
    event = Event()
    with pytest.raises(ValidationError) as exc_info:
        event.delete()

    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["type"] == "missing"
    assert "event_id" in errors[0]["msg"]
    assert "required to delete an event" in errors[0]["msg"]
