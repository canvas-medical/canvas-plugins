"""Tests for Calendar models and querysets."""

import pytest

from canvas_sdk.v1.data.calendar import Calendar, CalendarQuerySet


@pytest.fixture(autouse=True)
def setup_calendars(db: None) -> None:
    """Set up test data for calendar tests."""
    from canvas_sdk.test_utils.factories import CalendarFactory

    # Create test calendars with different naming patterns
    CalendarFactory.create(
        title="Dr. Smith: Office Visit", description="Office visits for Dr. Smith"
    )
    CalendarFactory.create(
        title="Dr. Smith: Office Visit: Room A", description="Office visits in Room A"
    )
    CalendarFactory.create(title="Dr. Jones: Telemedicine", description="Telemedicine appointments")
    CalendarFactory.create(
        title="Dr. Jones: Telemedicine: Virtual Room 1",
        description="Virtual appointments in room 1",
    )


@pytest.mark.django_db
def test_for_calendar_name_without_location() -> None:
    """Test filtering calendars by name without location."""
    # Query for Dr. Smith's Office Visit calendar without location
    result = Calendar.objects.for_calendar_name(
        provider_name="Dr. Smith", calendar_type="Office Visit", location=""
    )

    # Should return only the calendar without location specified
    assert result.count() == 1
    calendar = result.first()
    assert calendar is not None
    assert calendar.title == "Dr. Smith: Office Visit"


@pytest.mark.django_db
def test_for_calendar_name_with_location() -> None:
    """Test filtering calendars by name with location."""
    # Query for Dr. Smith's Office Visit calendar with Room A
    result = Calendar.objects.for_calendar_name(
        provider_name="Dr. Smith", calendar_type="Office Visit", location="Room A"
    )

    # Should return only the calendar with location specified
    assert result.count() == 1
    calendar = result.first()
    assert calendar is not None
    assert calendar.title == "Dr. Smith: Office Visit: Room A"


@pytest.mark.django_db
def test_for_calendar_name_no_match() -> None:
    """Test filtering calendars by name that doesn't exist."""
    # Query for a calendar that doesn't exist
    result = Calendar.objects.for_calendar_name(
        provider_name="Dr. Brown", calendar_type="Surgery", location=""
    )

    # Should return empty queryset
    assert result.count() == 0
    assert not result.exists()


@pytest.mark.django_db
def test_for_calendar_name_returns_queryset() -> None:
    """Test that for_calendar_name returns a CalendarQuerySet instance."""
    result = Calendar.objects.for_calendar_name(
        provider_name="Dr. Smith", calendar_type="Office Visit", location=""
    )

    # Verify it returns a CalendarQuerySet
    assert isinstance(result, CalendarQuerySet)


@pytest.mark.django_db
def test_for_calendar_name_with_empty_location_string() -> None:
    """Test that empty location string is handled correctly."""
    # Test with None
    result_none = Calendar.objects.for_calendar_name(
        provider_name="Dr. Smith", calendar_type="Office Visit", location=""
    )

    # Should match calendar without location in title
    assert result_none.count() == 1
    calendar = result_none.first()
    assert calendar is not None
    assert calendar.title == "Dr. Smith: Office Visit"


@pytest.mark.django_db
def test_for_calendar_name_title_format() -> None:
    """Test that the title format is constructed correctly."""
    # Test without location
    result_no_loc = Calendar.objects.for_calendar_name(
        provider_name="Dr. Jones", calendar_type="Telemedicine", location=""
    )
    # Should filter by "Dr. Jones: Telemedicine"
    assert result_no_loc.count() >= 1

    # Test with location
    result_with_loc = Calendar.objects.for_calendar_name(
        provider_name="Dr. Jones", calendar_type="Telemedicine", location="Virtual Room 1"
    )
    # Should filter by "Dr. Jones: Telemedicine: Virtual Room 1"
    assert result_with_loc.count() == 1
    calendar = result_with_loc.first()
    assert calendar is not None
    assert calendar.title == "Dr. Jones: Telemedicine: Virtual Room 1"


@pytest.mark.django_db
def test_for_calendar_name_multiple_results() -> None:
    """Test that for_calendar_name can return multiple calendars if titles match."""
    # Create duplicate calendar titles
    duplicate_calendar = Calendar(title="Dr. Smith: Office Visit", description="Duplicate calendar")
    duplicate_calendar.save()

    result = Calendar.objects.for_calendar_name(
        provider_name="Dr. Smith", calendar_type="Office Visit", location=""
    )

    # Should return multiple calendars with same title
    assert result.count() == 2
