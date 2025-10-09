"""
Data Validation Modal Component.

Builds modals for data validation errors with detailed information about missing data.
"""

from typing import Any

from canvas_sdk.effects import Effect
from logger import log
from pdmp_bamboo.lib.ui.modals.base_modal import BaseModal


class DataValidationModal(BaseModal):
    """Builds data validation modals for missing or incomplete data."""

    def create_data_validation_modal(
        self, missing_data: list[str], available_data: dict[str, Any] | None = None
    ) -> Effect:
        """
        Create a data validation modal for missing or incomplete data.

        Args:
            missing_data: List of missing data field descriptions
            available_data: Dictionary of available data for context

        Returns:
            LaunchModalEffect for the data validation modal
        """
        log.info("DataValidationModal: Creating data validation modal")

        # Build modal content
        content = self._build_modal_content(missing_data, available_data)

        # Create modal title
        title = "⚠️ PDMP Data Validation"

        return self.create_modal(title, content)

    def _build_modal_content(
        self, missing_data: list[str], available_data: dict[str, Any] | None
    ) -> str:
        """Build the complete modal content."""
        from canvas_sdk.templates import render_to_string

        # Build available data summary
        available_summary = self._build_available_data_summary(available_data) if available_data else ""

        # Build next steps section
        next_steps = self._build_next_steps()

        # Render template with all components
        return render_to_string("templates/modals/data_validation_modal_content.html", {
            "missing_data": missing_data,
            "available_data_summary": available_summary,
            "next_steps_section": next_steps
        })

    def _build_available_data_summary(self, available_data: dict[str, Any]) -> str:
        """Build available data summary section via template."""
        from canvas_sdk.templates import render_to_string

        summary_items = []

        patient_data = available_data.get("patient", {})
        if patient_data:
            patient_name = f"{patient_data.get('first_name', '')} {patient_data.get('last_name', '')}".strip() or "Name not available"
            summary_items.append({"label": "Patient", "value": patient_name})

        practitioner_data = available_data.get("practitioner", {})
        if practitioner_data:
            practitioner_name = f"{practitioner_data.get('first_name', '')} {practitioner_data.get('last_name', '')}".strip() or "Name not available"
            summary_items.append({"label": "Practitioner", "value": practitioner_name})

        organization_data = available_data.get("organization", {})
        if organization_data:
            org_name = organization_data.get("name", "Organization name not available")
            summary_items.append({"label": "Organization", "value": org_name})

        if summary_items:
            return render_to_string("templates/components/available_data_summary.html", {
                "items": summary_items,
            })

        return ""

    def _build_next_steps(self) -> str:
        """Build next steps section via template."""
        from canvas_sdk.templates import render_to_string
        next_steps = [
            "Complete missing patient information in Canvas EMR",
            "Ensure practitioner has required NPI or DEA numbers",
            "Verify organization and practice location data",
            "Try the PDMP request again after verifying data",
            "Contact your system administrator if errors persist",
        ]
        return render_to_string("templates/components/help_section.html", {
            "items": next_steps,
        })
