from canvas_sdk.effects import EffectType
from canvas_sdk.effects.calendar import Calendar, CalendarType


def test_create_calendar_minimal_required_fields() -> None:
    """Test Calendar with only required fields."""
    calendar = Calendar(provider="provider-id", type=CalendarType.Clinic)
    payload = calendar.create()
    assert payload.type == EffectType.CALENDAR__CREATE
    assert (
        payload.payload
        == '{"data": {"id": null, "provider": "provider-id", "type": "Clinic", "location": null, "description": null}}'
    )


def test_create_calendar_with_all_fields() -> None:
    """Test Calendar with all fields populated."""
    calendar = Calendar(
        id="calendar-id",
        provider="provider-id",
        type=CalendarType.Clinic,
        location="Building A, Room 101",
        description="Primary care clinic calendar",
    )
    payload = calendar.create()
    assert payload.type == EffectType.CALENDAR__CREATE
    assert (
        payload.payload
        == '{"data": {"id": "calendar-id", "provider": "provider-id", "type": "Clinic", "location": "Building A, Room 101", "description": "Primary care clinic calendar"}}'
    )


def test_create_calendar_with_uuid_provider() -> None:
    """Test Calendar with UUID for provider."""
    provider_uuid = "12345678-1234-5678-1234-567812345678"
    calendar = Calendar(provider=provider_uuid, type=CalendarType.Administrative)
    payload = calendar.create()
    assert payload.type == EffectType.CALENDAR__CREATE
    assert (
        payload.payload
        == '{"data": {"id": null, "provider": "12345678-1234-5678-1234-567812345678", "type": "Admin", "location": null, "description": null}}'
    )


def test_create_calendar_with_uuid_id() -> None:
    """Test Calendar with UUID for id."""
    calendar_uuid = "87654321-4321-8765-4321-876543218765"
    calendar = Calendar(
        id=calendar_uuid,
        provider="provider-id",
        type=CalendarType.Clinic,
    )
    payload = calendar.create()
    assert payload.type == EffectType.CALENDAR__CREATE
    assert (
        payload.payload
        == '{"data": {"id": "87654321-4321-8765-4321-876543218765", "provider": "provider-id", "type": "Clinic", "location": null, "description": null}}'
    )


def test_create_calendar_administrative_type() -> None:
    """Test Calendar with Administrative calendar type."""
    calendar = Calendar(
        provider="provider-id",
        type=CalendarType.Administrative,
        description="Administrative meetings calendar",
    )
    payload = calendar.create()
    assert payload.type == EffectType.CALENDAR__CREATE
    assert (
        payload.payload
        == '{"data": {"id": null, "provider": "provider-id", "type": "Admin", "location": null, "description": "Administrative meetings calendar"}}'
    )


def test_create_calendar_with_location_only() -> None:
    """Test Calendar with location but no description."""
    calendar = Calendar(
        provider="provider-id",
        type=CalendarType.Clinic,
        location="Telehealth",
    )
    payload = calendar.create()
    assert payload.type == EffectType.CALENDAR__CREATE
    assert (
        payload.payload
        == '{"data": {"id": null, "provider": "provider-id", "type": "Clinic", "location": "Telehealth", "description": null}}'
    )


def test_create_calendar_with_description_only() -> None:
    """Test Calendar with description but no location."""
    calendar = Calendar(
        provider="provider-id",
        type=CalendarType.Clinic,
        description="Evening clinic hours",
    )
    payload = calendar.create()
    assert payload.type == EffectType.CALENDAR__CREATE
    assert (
        payload.payload
        == '{"data": {"id": null, "provider": "provider-id", "type": "Clinic", "location": null, "description": "Evening clinic hours"}}'
    )
