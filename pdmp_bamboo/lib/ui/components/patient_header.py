"""
Patient Header Component.

Displays patient demographic information in a persistent header.
"""

from datetime import datetime
from typing import Any

from canvas_sdk.templates import render_to_string
from logger import log


class PatientHeaderComponent:
    """Component for displaying patient demographic header."""

    def create_component(self, patient_data: dict[str, Any]) -> str | None:
        """
        Create patient header component.

        Args:
            patient_data: Patient data dictionary containing demographic information

        Returns:
            HTML string for patient header, or None if no patient data
        """
        if not patient_data:
            return None

        # Extract patient information
        first_name = patient_data.get("first_name", "")
        last_name = patient_data.get("last_name", "")
        date_of_birth = patient_data.get("birth_date", "")
        sex = patient_data.get("sex", "")

        # Build full name
        full_name = f"{first_name} {last_name}".strip()
        if not full_name:
            return None

        log.info(f"PatientHeaderComponent: Creating header for patient: {full_name}")

        # Format date of birth
        formatted_dob = self._format_date(date_of_birth)

        # Format sex
        formatted_sex = sex.title() if sex else "—"

        # Render using template
        try:
            return render_to_string("templates/components/patient_header.html", {
                "full_name": full_name,
                "formatted_dob": formatted_dob if formatted_dob else "—",
                "formatted_sex": formatted_sex,
            })
        except Exception as e:
            log.error(f"PatientHeaderComponent: Error rendering template: {e}")
            return None

    def _format_date(self, date_of_birth: str) -> str:
        """Format date of birth to readable format."""
        if not date_of_birth:
            return ""

        try:
            # Handle different date formats
            date_part = date_of_birth.split("T")[0] if "T" in date_of_birth else date_of_birth

            # Parse and format date
            parsed_date = datetime.strptime(date_part, "%Y-%m-%d")
            return parsed_date.strftime("%B %d, %Y")
        except (ValueError, TypeError):
            return date_of_birth
