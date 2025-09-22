"""Basic tests for Staff Status Tracker functionality."""

import csv
import io
from unittest.mock import Mock, patch

import pytest

from staff_status_tracker.handlers.cron_task import StaffStatusCronTask
from staff_status_tracker.handlers.event_handlers import StaffActivatedHandler, StaffDeactivatedHandler


class TestStaffStatusCronTask:
    """Test the cron task functionality."""

    def test_generate_csv_data(self):
        """Test CSV generation with mock staff data."""
        cron_task = StaffStatusCronTask()
        
        # Create mock staff objects
        mock_staff1 = Mock()
        mock_staff1.id = "abc123"
        mock_staff1.first_name = "Jane"
        mock_staff1.last_name = "Doe"
        mock_staff1.active = True
        mock_staff1.user = Mock()
        mock_staff1.user.email = "jane.doe@example.com"
        
        mock_staff2 = Mock()
        mock_staff2.id = "def456"
        mock_staff2.first_name = "Jon"
        mock_staff2.last_name = "Dowd"
        mock_staff2.active = False
        mock_staff2.user = Mock()
        mock_staff2.user.email = "jon.dowd@example.com"
        
        staff_members = [mock_staff1, mock_staff2]
        timestamp = "2025-03-06T01:20:32.446Z"
        
        # Generate CSV
        csv_data = cron_task._generate_csv_data(staff_members, timestamp)
        
        # Parse and verify CSV
        lines = csv_data.strip().split('\n')
        assert len(lines) == 3  # Header + 2 data rows
        
        # Check header
        header = lines[0]
        assert "timestamp,staff_id,first_name,last_name,email,status,previous_status" == header
        
        # Check data rows
        reader = csv.reader(io.StringIO(csv_data))
        rows = list(reader)
        
        # First staff member (active)
        assert rows[1][0] == timestamp
        assert rows[1][1] == "abc123"
        assert rows[1][2] == "Jane"
        assert rows[1][3] == "Doe"
        assert rows[1][4] == "jane.doe@example.com"
        assert rows[1][5] == "active"
        assert rows[1][6] == ""  # previous_status empty for initial collection
        
        # Second staff member (inactive)
        assert rows[2][0] == timestamp
        assert rows[2][1] == "def456"
        assert rows[2][2] == "Jon"
        assert rows[2][3] == "Dowd"
        assert rows[2][4] == "jon.dowd@example.com"
        assert rows[2][5] == "inactive"
        assert rows[2][6] == ""  # previous_status empty for initial collection


class TestStaffEventHandlers:
    """Test the staff event handlers."""

    def test_get_previous_status_from_csv(self):
        """Test extracting previous status from CSV data."""
        handler = StaffActivatedHandler()
        
        csv_data = """timestamp,staff_id,first_name,last_name,email,status,previous_status
2025-03-06T01:20:32.446Z,abc123,Jane,Doe,jane.doe@example.com,active,
2025-03-06T01:20:32.446Z,def456,Jon,Dowd,jon.dowd@example.com,inactive,
2025-03-10T22:47:16.221Z,abc123,Jane,Doe,jane.doe@example.com,inactive,active"""
        
        # Test getting the most recent status for abc123
        previous_status = handler._get_previous_status_from_csv(csv_data, "abc123")
        assert previous_status == "inactive"
        
        # Test getting status for def456 (only one entry)
        previous_status = handler._get_previous_status_from_csv(csv_data, "def456")
        assert previous_status == "inactive"
        
        # Test non-existent staff
        previous_status = handler._get_previous_status_from_csv(csv_data, "xyz999")
        assert previous_status == ""
        
        # Test empty CSV
        previous_status = handler._get_previous_status_from_csv("", "abc123")
        assert previous_status == ""

    def test_get_previous_status_header_only(self):
        """Test extracting previous status from CSV with only header."""
        handler = StaffActivatedHandler()
        
        csv_data = "timestamp,staff_id,first_name,last_name,email,status,previous_status"
        
        previous_status = handler._get_previous_status_from_csv(csv_data, "abc123")
        assert previous_status == ""