"""
Report Button Component.

Creates the PDMP report button with Canvas context.
"""

from typing import Any

from pdmp_bamboo.lib.ui.components.base_component import BaseComponent


class ReportButtonComponent(BaseComponent):
    """Component for creating PDMP report access button with interactive functionality."""

    def create_component(
        self,
        parsed_data: dict[str, Any],
        patient_id: str | None = None,
        practitioner_id: str | None = None,
        organization_id: str | None = None,
        staff_id: str | None = None,
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

        return self._render_template(
            "templates/components/report_button.html",
            {
                "report_url": report_url,
                "expiration_date": expiration_date,
                "patient_id": patient_id or "",
                "practitioner_id": practitioner_id or "",
                "organization_id": organization_id or "",
                "staff_id": staff_id or (practitioner_id or ""),
            },
        )
