"""SimpleAPI endpoint to trigger staff status collection for testing."""

import arrow
from typing import Any

from canvas_sdk.caching.plugins import get_cache
from canvas_sdk.effects.simple_api import JSONResponse
from canvas_sdk.handlers.simple_api import APIKeyAuthMixin, SimpleAPIRoute
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


class StaffStatusTriggerAPI(APIKeyAuthMixin, SimpleAPIRoute):
    """API endpoint that triggers the weekly staff status collection job."""

    PATH = "/trigger-staff-status-collection"

    def get(self) -> list[JSONResponse]:
        """Trigger the staff status collection manually."""
        try:
            log.info("Manually triggering staff status collection via API")

            # Execute the same logic that would run on Monday at midnight
            self._collect_staff_status()

            # Count staff members for response
            staff_count = Staff.objects.count()

            log.info(f"Staff status collection completed via API. Processed {staff_count} staff members.")

            return [JSONResponse({
                "message": "Staff status collection triggered successfully",
                "staff_count": staff_count,
                "status": "completed"
            })]
        except Exception as e:
            log.error(f"Error triggering staff status collection via API: {e}")
            return [JSONResponse({
                "error": f"Failed to trigger staff status collection: {str(e)}",
                "status": "failed"
            }, status_code=500)]

    def _collect_staff_status(self) -> None:
        """
        Collect all staff data and generate CSV, store in cache.
        """
        # Get all staff members
        staff_members = Staff.objects.all()
        
        # Generate timestamp
        timestamp = arrow.utcnow().isoformat()
        
        # Generate CSV data
        csv_data = self._generate_csv_data(staff_members, timestamp)
        
        # Get cache and store for 7 days (7 * 24 * 60 * 60 = 604800 seconds)
        cache = get_cache()
        cache_key = "staff-status"
        
        # Check if previous cache exists and log it
        existing_data = cache.get(cache_key)
        if existing_data:
            log.info(f"Previous staff status data found: {existing_data[:500]}...")
        
        # Store new CSV data
        cache.set(cache_key, csv_data, timeout_seconds=604800)  # 7 days
        
        log.info(f"Staff status data collected and cached: {csv_data[:500]}...")

    def _generate_csv_data(self, staff_members: Any, timestamp: str) -> str:
        """
        Generate CSV format data for staff members.
        """
        lines = []
        
        # Write header
        header = format_csv_row([
            "timestamp", 
            "staff_id", 
            "first_name", 
            "last_name", 
            "email", 
            "status", 
            "previous_status"
        ])
        lines.append(header)
        
        # Write staff data
        for staff in staff_members:
            # Get email from user if available
            email = ""
            if staff.user and hasattr(staff.user, 'email'):
                email = staff.user.email
            
            status = "active" if staff.active else "inactive"
            
            row = format_csv_row([
                timestamp,
                staff.id,
                staff.first_name,
                staff.last_name,
                email,
                status,
                ""  # previous_status empty for initial collection
            ])
            lines.append(row)
        
        return "\n".join(lines)