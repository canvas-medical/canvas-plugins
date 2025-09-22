"""Staff Status Change Event Handlers."""

import arrow
import io
from typing import Any

from canvas_sdk.caching.plugins import get_cache
from canvas_sdk.effects import Effect
from canvas_sdk.events import EventType
from canvas_sdk.handlers.base import BaseHandler
from canvas_sdk.v1.data.staff import Staff
from logger import log


def escape_csv_field(field: str) -> str:
    """Escape a field for CSV format."""
    if not field:
        return ""
    # If field contains comma, quote, or newline, wrap in quotes and escape quotes
    if "," in field or '"' in field or "\n" in field:
        return '"' + field.replace('"', '""') + '"'
    return field


def format_csv_row(fields: list) -> str:
    """Format a list of fields as a CSV row."""
    return ",".join(escape_csv_field(str(field)) for field in fields)


def parse_csv_row(row: str) -> list:
    """Parse a CSV row into fields."""
    fields = []
    current_field = ""
    in_quotes = False
    i = 0
    
    while i < len(row):
        char = row[i]
        
        if char == '"':
            if in_quotes and i + 1 < len(row) and row[i + 1] == '"':
                # Escaped quote
                current_field += '"'
                i += 1  # Skip next quote
            else:
                # Toggle quote state
                in_quotes = not in_quotes
        elif char == ',' and not in_quotes:
            # Field separator
            fields.append(current_field)
            current_field = ""
        else:
            current_field += char
        
        i += 1
    
    # Add the last field
    fields.append(current_field)
    return fields


class StaffActivatedHandler(BaseHandler):
    """
    Handler for STAFF_ACTIVATED events.
    """

    RESPONDS_TO = [
        EventType.Name(EventType.STAFF_ACTIVATED),
    ]

    def compute(self) -> list[Effect]:
        """
        Handle staff activation events.
        """
        try:
            staff_id = self.event.target.id
            log.info(f"Processing STAFF_ACTIVATED event for staff ID: {staff_id}")
            
            # Get staff object
            staff = Staff.objects.get(id=staff_id)
            
            # Update CSV with status change - determine previous status
            cache = get_cache()
            cache_key = "staff-status"
            existing_data = cache.get(cache_key, "")
            
            previous_status = self._get_previous_status_from_csv(existing_data, staff_id)
            if not previous_status:
                # New staff member
                previous_status = "null"
            
            self._update_csv_with_status_change(staff, "active", previous_status)
            
            return []
            
        except Exception as e:
            log.error(f"Error in StaffActivatedHandler: {e}")
            return []

    def _update_csv_with_status_change(self, staff: Staff, new_status: str, previous_status: str) -> None:
        """
        Update the cached CSV with the status change.
        """
        cache = get_cache()
        cache_key = "staff-status"
        
        # Get existing CSV data
        existing_data = cache.get(cache_key, "")
        
        # Generate timestamp
        timestamp = arrow.utcnow().isoformat()
        
        # Get email from user if available
        email = ""
        if staff.user and hasattr(staff.user, 'email'):
            email = staff.user.email
        
        # Create new row
        new_row = format_csv_row([
            timestamp,
            staff.id,
            staff.first_name,
            staff.last_name,
            email,
            new_status,
            previous_status
        ])
        
        # If no existing data, create header and add row
        if not existing_data:
            header = format_csv_row([
                "timestamp", 
                "staff_id", 
                "first_name", 
                "last_name", 
                "email", 
                "status", 
                "previous_status"
            ])
            updated_csv = header + "\n" + new_row
        else:
            # Append to existing CSV
            updated_csv = existing_data.rstrip() + "\n" + new_row
        
        # Store updated CSV (7 days = 604800 seconds)
        cache.set(cache_key, updated_csv, timeout_seconds=604800)
        
        log.info(f"Updated staff status CSV with {new_status} for staff {staff.id}")

    def _get_previous_status_from_csv(self, csv_data: str, staff_id: str) -> str:
        """
        Extract the most recent status for a staff member from the CSV data.
        """
        if not csv_data:
            return ""
        
        try:
            lines = csv_data.strip().split('\n')
            if len(lines) <= 1:  # Only header or empty
                return ""
            
            # Look for the most recent entry for this staff member
            for line in reversed(lines[1:]):  # Skip header, go in reverse for most recent
                row = parse_csv_row(line)
                if len(row) >= 6 and row[1] == staff_id:  # staff_id is in column 1
                    return row[5]  # status is in column 5
                    
        except Exception as e:
            log.error(f"Error parsing CSV for previous status: {e}")
        
        return ""


class StaffDeactivatedHandler(BaseHandler):
    """
    Handler for STAFF_DEACTIVATED events.
    """

    RESPONDS_TO = [
        EventType.Name(EventType.STAFF_DEACTIVATED),
    ]

    def compute(self) -> list[Effect]:
        """
        Handle staff deactivation events.
        """
        try:
            staff_id = self.event.target.id
            log.info(f"Processing STAFF_DEACTIVATED event for staff ID: {staff_id}")
            
            # Get staff object
            staff = Staff.objects.get(id=staff_id)
            
            # Update CSV with status change
            self._update_csv_with_status_change(staff, "inactive", "active")
            
            return []
            
        except Exception as e:
            log.error(f"Error in StaffDeactivatedHandler: {e}")
            return []

    def _update_csv_with_status_change(self, staff: Staff, new_status: str, previous_status: str) -> None:
        """
        Update the cached CSV with the status change.
        """
        cache = get_cache()
        cache_key = "staff-status"
        
        # Get existing CSV data
        existing_data = cache.get(cache_key, "")
        
        # Check if staff exists in previous data to determine previous status
        actual_previous_status = self._get_previous_status_from_csv(existing_data, staff.id)
        if actual_previous_status:
            previous_status = actual_previous_status
        elif not existing_data and new_status == "active":
            # New staff being activated for the first time
            previous_status = "null"
        
        # Generate timestamp
        timestamp = arrow.utcnow().isoformat()
        
        # Get email from user if available
        email = ""
        if staff.user and hasattr(staff.user, 'email'):
            email = staff.user.email
        
        # Create new row
        new_row = format_csv_row([
            timestamp,
            staff.id,
            staff.first_name,
            staff.last_name,
            email,
            new_status,
            previous_status
        ])
        
        # If no existing data, create header and add row
        if not existing_data:
            header = format_csv_row([
                "timestamp", 
                "staff_id", 
                "first_name", 
                "last_name", 
                "email", 
                "status", 
                "previous_status"
            ])
            updated_csv = header + "\n" + new_row
        else:
            # Append to existing CSV
            updated_csv = existing_data.rstrip() + "\n" + new_row
        
        # Store updated CSV (7 days = 604800 seconds)
        cache.set(cache_key, updated_csv, timeout_seconds=604800)
        
        log.info(f"Updated staff status CSV with {new_status} for staff {staff.id}")

    def _get_previous_status_from_csv(self, csv_data: str, staff_id: str) -> str:
        """
        Extract the most recent status for a staff member from the CSV data.
        """
        if not csv_data:
            return ""
        
        try:
            lines = csv_data.strip().split('\n')
            if len(lines) <= 1:  # Only header or empty
                return ""
            
            # Look for the most recent entry for this staff member
            for line in reversed(lines[1:]):  # Skip header, go in reverse for most recent
                row = parse_csv_row(line)
                if len(row) >= 6 and row[1] == staff_id:  # staff_id is in column 1
                    return row[5]  # status is in column 5
                    
        except Exception as e:
            log.error(f"Error parsing CSV for previous status: {e}")
        
        return ""