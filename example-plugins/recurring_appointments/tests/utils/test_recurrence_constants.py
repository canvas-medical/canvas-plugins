"""Tests for recurring_appointments.utils.constants module."""

from recurring_appointments.utils.constants import (
    RecurrenceEnum,
    FIELD_RECURRENCE_INTERVAL_KEY,
    FIELD_RECURRENCE_TYPE_KEY,
    FIELD_RECURRENCE_STOP_AFTER_KEY,
)


class TestRecurrenceEnum:
    """Tests for RecurrenceEnum."""

    def test_enum_values(self):
        """Test that RecurrenceEnum has expected values."""
        assert RecurrenceEnum.DAYS.value == "Day(s)"
        assert RecurrenceEnum.WEEKS.value == "Week(s)"
        assert RecurrenceEnum.MONTHS.value == "Month(s)"
        assert RecurrenceEnum.NONE.value == "None"

    def test_enum_members(self):
        """Test that RecurrenceEnum has all expected members."""
        expected_members = {"DAYS", "WEEKS", "MONTHS", "NONE"}
        actual_members = {member.name for member in RecurrenceEnum}
        assert actual_members == expected_members


class TestConstants:
    """Tests for field key constants."""

    def test_field_keys(self):
        """Test that field key constants have correct values."""
        assert FIELD_RECURRENCE_INTERVAL_KEY == "recurrence_interval"
        assert FIELD_RECURRENCE_TYPE_KEY == "recurrence"
        assert FIELD_RECURRENCE_STOP_AFTER_KEY == "stop_after"
