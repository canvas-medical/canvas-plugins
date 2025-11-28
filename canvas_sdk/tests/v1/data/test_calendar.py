"""Tests for Calendar models and querysets."""

from django.test import TestCase

from canvas_sdk.v1.data.calendar import Calendar, CalendarQuerySet


class TestCalendarQuerySet(TestCase):
    """Test suite for CalendarQuerySet methods."""

    def setUp(self) -> None:
        """Set up test data for calendar tests."""
        # Create test calendars with different naming patterns
        calendar1 = Calendar(
            title="Dr. Smith: Office Visit", description="Office visits for Dr. Smith"
        )
        calendar1.save()

        calendar2 = Calendar(
            title="Dr. Smith: Office Visit: Room A", description="Office visits in Room A"
        )
        calendar2.save()

        calendar3 = Calendar(
            title="Dr. Jones: Telemedicine", description="Telemedicine appointments"
        )
        calendar3.save()

        calendar4 = Calendar(
            title="Dr. Jones: Telemedicine: Virtual Room 1",
            description="Virtual appointments in room 1",
        )
        calendar4.save()

    def test_for_calendar_name_without_location(self) -> None:
        """Test filtering calendars by name without location."""
        # Query for Dr. Smith's Office Visit calendar without location
        result = Calendar.objects.for_calendar_name(
            provider_name="Dr. Smith", calendar_type="Office Visit", location=""
        )

        # Should return only the calendar without location specified
        self.assertEqual(result.count(), 1)
        calendar = result.first()
        assert calendar is not None
        self.assertEqual(calendar.title, "Dr. Smith: Office Visit")

    def test_for_calendar_name_with_location(self) -> None:
        """Test filtering calendars by name with location."""
        # Query for Dr. Smith's Office Visit calendar with Room A
        result = Calendar.objects.for_calendar_name(
            provider_name="Dr. Smith", calendar_type="Office Visit", location="Room A"
        )

        # Should return only the calendar with location specified
        self.assertEqual(result.count(), 1)
        calendar = result.first()
        assert calendar is not None
        self.assertEqual(calendar.title, "Dr. Smith: Office Visit: Room A")

    def test_for_calendar_name_no_match(self) -> None:
        """Test filtering calendars by name that doesn't exist."""
        # Query for a calendar that doesn't exist
        result = Calendar.objects.for_calendar_name(
            provider_name="Dr. Brown", calendar_type="Surgery", location=""
        )

        # Should return empty queryset
        self.assertEqual(result.count(), 0)
        self.assertFalse(result.exists())

    def test_for_calendar_name_returns_queryset(self) -> None:
        """Test that for_calendar_name returns a CalendarQuerySet instance."""
        result = Calendar.objects.for_calendar_name(
            provider_name="Dr. Smith", calendar_type="Office Visit", location=""
        )

        # Verify it returns a CalendarQuerySet
        self.assertIsInstance(result, CalendarQuerySet)

    def test_for_calendar_name_with_empty_location_string(self) -> None:
        """Test that empty location string is handled correctly."""
        # Test with None
        result_none = Calendar.objects.for_calendar_name(
            provider_name="Dr. Smith", calendar_type="Office Visit", location=""
        )

        # Should match calendar without location in title
        self.assertEqual(result_none.count(), 1)
        calendar = result_none.first()
        assert calendar is not None
        self.assertEqual(calendar.title, "Dr. Smith: Office Visit")

    def test_for_calendar_name_title_format(self) -> None:
        """Test that the title format is constructed correctly."""
        # Test without location
        result_no_loc = Calendar.objects.for_calendar_name(
            provider_name="Dr. Jones", calendar_type="Telemedicine", location=""
        )
        # Should filter by "Dr. Jones: Telemedicine"
        self.assertGreaterEqual(result_no_loc.count(), 1)

        # Test with location
        result_with_loc = Calendar.objects.for_calendar_name(
            provider_name="Dr. Jones", calendar_type="Telemedicine", location="Virtual Room 1"
        )
        # Should filter by "Dr. Jones: Telemedicine: Virtual Room 1"
        self.assertEqual(result_with_loc.count(), 1)
        calendar = result_with_loc.first()
        assert calendar is not None
        self.assertEqual(calendar.title, "Dr. Jones: Telemedicine: Virtual Room 1")

    def test_for_calendar_name_multiple_results(self) -> None:
        """Test that for_calendar_name can return multiple calendars if titles match."""
        # Create duplicate calendar titles
        duplicate_calendar = Calendar(
            title="Dr. Smith: Office Visit", description="Duplicate calendar"
        )
        duplicate_calendar.save()

        result = Calendar.objects.for_calendar_name(
            provider_name="Dr. Smith", calendar_type="Office Visit", location=""
        )

        # Should return multiple calendars with same title
        self.assertEqual(result.count(), 2)
