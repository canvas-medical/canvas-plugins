"""SimpleAPI endpoint to trigger staff status collection for testing."""

from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import JSONResponse
from canvas_sdk.handlers.simple_api import SimpleAPIRoute, StaffSessionAuthMixin
from canvas_sdk.v1.data.staff import Staff
from logger import log

# Import the cron task class to reuse its logic
from staff_status_tracker.handlers import StaffStatusCronTask


class StaffStatusTriggerAPI(StaffSessionAuthMixin, SimpleAPIRoute):
    """API endpoint that triggers the weekly staff status collection job."""

    PATH = "/trigger-staff-status-collection"

    def get(self) -> list[JSONResponse]:
        """Trigger the staff status collection manually."""
        try:
            log.info("Manually triggering staff status collection via API")

            # Create an instance of the cron task and execute its logic
            cron_task = StaffStatusCronTask()

            # Execute the same logic that would run on Monday at midnight
            effects = cron_task.execute()

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