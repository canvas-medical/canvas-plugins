"""
Data Validation Modal Component

Builds modals for data validation errors with detailed information about missing data.
"""

from typing import Dict, Any, List, Optional
from canvas_sdk.effects import Effect
from logger import log

from pdmp_bamboo.ui.modals.base_modal import BaseModal


class DataValidationModal(BaseModal):
    """Builds data validation modals for missing or incomplete data."""
    
    def create_data_validation_modal(self,
                                   missing_data: List[str],
                                   available_data: Optional[Dict[str, Any]] = None) -> Effect:
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

    def _build_modal_content(self,
                           missing_data: List[str],
                           available_data: Optional[Dict[str, Any]]) -> str:
        """Build the complete modal content."""

        # Main title
        content = self.create_title("⚠️ PDMP Data Validation", level=3, color="#f57c00")

        # Description
        content += '<p style="color: #666; margin-bottom: 20px;">The following data is missing or incomplete for the PDMP request:</p>'

        # Missing data section
        if missing_data:
            content += self.create_error_box("Missing Required Data", missing_data, "⚠️")

        # Available data summary if provided
        if available_data:
            available_summary = self._build_available_data_summary(available_data)
            content += available_summary

        # Next steps section
        next_steps = self._build_next_steps()
        content += next_steps

        return f'<div style="{self.default_styles["container"]}">{content}</div>'

    def _build_available_data_summary(self, available_data: Dict[str, Any]) -> str:
        """Build available data summary section."""
        summary_items = []

        # Patient data
        patient_data = available_data.get("patient", {})
        if patient_data:
            patient_name = f"{patient_data.get('first_name', '')} {patient_data.get('last_name', '')}"
            summary_items.append(f"<strong>Patient:</strong> {patient_name.strip() or 'Name not available'}")

        # Practitioner data
        practitioner_data = available_data.get("practitioner", {})
        if practitioner_data:
            practitioner_name = f"{practitioner_data.get('first_name', '')} {practitioner_data.get('last_name', '')}"
            summary_items.append(f"<strong>Practitioner:</strong> {practitioner_name.strip() or 'Name not available'}")

        # Organization data
        organization_data = available_data.get("organization", {})
        if organization_data:
            org_name = organization_data.get("name", "Organization name not available")
            summary_items.append(f"<strong>Organization:</strong> {org_name}")

        if summary_items:
            return self.create_info_box("Available Data Summary", summary_items, "ℹ️")

        return ""

    def _build_next_steps(self) -> str:
        """Build next steps section."""
        next_steps = [
            "Complete missing patient information in Canvas EMR",
            "Ensure practitioner has required NPI or DEA numbers",
            "Verify organization and practice location data",
            "Try the PDMP request again after verifying data",
            "Contact your system administrator if errors persist"
        ]

        return self.create_info_box("Next Steps", next_steps, "💡")