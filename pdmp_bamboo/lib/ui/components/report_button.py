"""
Report Button Component.

Creates the PDMP report button with Canvas context.
"""

from typing import Any

from canvas_sdk.templates import render_to_string
from logger import log


class ReportButtonComponent:
    """Component for creating PDMP report access button with interactive functionality."""

    def create_component(
        self,
        parsed_data: dict[str, Any],
        use_test_env: bool = False,
        patient_id: str | None = None,
        practitioner_id: str | None = None,
        organization_id: str | None = None,
    ) -> str | None:
        """
        Create report button component.

        Args:
            parsed_data: Parsed PDMP response data
            use_test_env: Whether this is a test environment request
            patient_id: Canvas patient ID
            practitioner_id: Canvas practitioner ID
            organization_id: Canvas organization ID

        Returns:
            HTML string for report button, or None if no report URL
        """
        if not parsed_data.get("parsed") or not parsed_data.get("report_url"):
            return None

        report_url = parsed_data["report_url"]
        expiration_date = parsed_data.get("report_expiration", "Unknown")
        env = "test" if use_test_env else "prod"

        try:
            return render_to_string("templates/components/report_button.html", {
                "report_url": report_url,
                "expiration_date": expiration_date,
                "env": env,
                "patient_id": patient_id or "",
                "practitioner_id": practitioner_id or "",
                "organization_id": organization_id or ""
            })
        except Exception as e:
            log.error(f"ReportButtonComponent: Error rendering template: {e}")
            return None
