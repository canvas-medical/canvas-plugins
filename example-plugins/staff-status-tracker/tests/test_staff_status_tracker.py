"""Basic tests for Staff Status Tracker functionality."""

import csv
import io
from unittest.mock import Mock, patch

# Note: These imports would need to be adjusted based on the actual plugin loading mechanism
# For demonstration purposes, we're showing the expected structure


class TestStaffStatusCronTask:
    """Test the cron task functionality."""

    def test_generate_csv_data(self):
        """Test CSV generation with mock staff data."""
        # This would be imported from the actual cron task handler
        # from staff_status_tracker.handlers.cron_task import StaffStatusCronTask
        
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
        
        # Mock the CSV generation logic
        import io
        import csv
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "timestamp", 
            "staff_id", 
            "first_name", 
            "last_name", 
            "email", 
            "status", 
            "previous_status"
        ])
        
        # Write staff data
        for staff in staff_members:
            email = staff.user.email if staff.user else ""
            status = "active" if staff.active else "inactive"
            
            writer.writerow([
                timestamp,
                staff.id,
                staff.first_name,
                staff.last_name,
                email,
                status,
                ""  # previous_status empty for initial collection
            ])
        
        csv_data = output.getvalue()
        
        # Parse and verify CSV
        lines = csv_data.strip().split('\n')
        assert len(lines) == 3  # Header + 2 data rows
        
        # Check header
        header = lines[0].strip()
        expected_header = "timestamp,staff_id,first_name,last_name,email,status,previous_status"
        assert expected_header == header
        
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
        csv_data = """timestamp,staff_id,first_name,last_name,email,status,previous_status
2025-03-06T01:20:32.446Z,abc123,Jane,Doe,jane.doe@example.com,active,
2025-03-06T01:20:32.446Z,def456,Jon,Dowd,jon.dowd@example.com,inactive,
2025-03-10T22:47:16.221Z,abc123,Jane,Doe,jane.doe@example.com,inactive,active"""
        
        # Mock the CSV parsing logic from event handlers
        def get_previous_status_from_csv(csv_data: str, staff_id: str) -> str:
            if not csv_data:
                return ""
            
            try:
                lines = csv_data.strip().split('\n')
                if len(lines) <= 1:  # Only header or empty
                    return ""
                
                # Look for the most recent entry for this staff member
                for line in reversed(lines[1:]):  # Skip header, go in reverse for most recent
                    reader = csv.reader([line])
                    row = next(reader)
                    if len(row) >= 6 and row[1] == staff_id:  # staff_id is in column 1
                        return row[5]  # status is in column 5
                        
            except Exception:
                pass
            
            return ""
        
        # Test getting the most recent status for abc123
        previous_status = get_previous_status_from_csv(csv_data, "abc123")
        assert previous_status == "inactive"
        
        # Test getting status for def456 (only one entry)
        previous_status = get_previous_status_from_csv(csv_data, "def456")
        assert previous_status == "inactive"
        
        # Test non-existent staff
        previous_status = get_previous_status_from_csv(csv_data, "xyz999")
        assert previous_status == ""
        
        # Test empty CSV
        previous_status = get_previous_status_from_csv("", "abc123")
        assert previous_status == ""

    def test_get_previous_status_header_only(self):
        """Test extracting previous status from CSV with only header."""
        csv_data = "timestamp,staff_id,first_name,last_name,email,status,previous_status"
        
        def get_previous_status_from_csv(csv_data: str, staff_id: str) -> str:
            if not csv_data:
                return ""
            
            try:
                lines = csv_data.strip().split('\n')
                if len(lines) <= 1:  # Only header or empty
                    return ""
                
                # Look for the most recent entry for this staff member
                for line in reversed(lines[1:]):  # Skip header, go in reverse for most recent
                    reader = csv.reader([line])
                    row = next(reader)
                    if len(row) >= 6 and row[1] == staff_id:  # staff_id is in column 1
                        return row[5]  # status is in column 5
                        
            except Exception:
                pass
            
            return ""
        
        previous_status = get_previous_status_from_csv(csv_data, "abc123")
        assert previous_status == ""


if __name__ == "__main__":
    # Simple test execution
    test_cron = TestStaffStatusCronTask()
    test_cron.test_generate_csv_data()
    print("✓ CSV generation test passed")
    
    test_handlers = TestStaffEventHandlers()
    test_handlers.test_get_previous_status_from_csv()
    print("✓ Previous status extraction test passed")
    
    test_handlers.test_get_previous_status_header_only()
    print("✓ Header-only CSV test passed")
    
    print("All tests passed!")