"""
Alerts Component.

Displays clinical alerts, red flags, and care notes from PDMP responses.
"""

from typing import Any

from logger import log
from pdmp_bamboo.lib.ui.components.base_component import BaseComponent


class AlertsComponent(BaseComponent):
    """Component for displaying clinical alerts and flags."""

    def create_component(self, parsed_data: dict[str, Any]) -> str | None:
        """
        Create alerts component.

        Args:
            parsed_data: Parsed PDMP response data

        Returns:
            HTML string for alerts display, or None if no alerts
        """
        if not parsed_data.get("parsed"):
            return None

        # Extract different types of alerts
        red_flags = parsed_data.get("red_flags", [])
        alerts = parsed_data.get("alerts", [])
        care_notes = parsed_data.get("care_notes", [])

        # Only show if we have at least one type of alert
        if not red_flags and not alerts and not care_notes:
            return None

        log.info(
            f"AlertsComponent: Creating alerts component with {len(red_flags)} red flags, {len(alerts)} alerts, {len(care_notes)} care notes"
        )

        return self._render_template(
            "templates/components/alerts.html",
            {"red_flags": red_flags, "alerts": alerts, "care_notes": care_notes},
        )
