"""
Raw Response Component.

Displays raw XML response in a collapsible section for debugging.
"""

from canvas_sdk.templates import render_to_string
from logger import log


class RawResponseComponent:
    """Component for displaying raw XML response."""

    def create_component(self, raw_response: str) -> str | None:
        """
        Create raw response component.

        Args:
            raw_response: Raw XML response string

        Returns:
            HTML string for raw response display, or None if no response
        """
        if not raw_response:
            return None

        log.info(
            f"RawResponseComponent: Creating raw response component ({len(raw_response)} characters)"
        )

        # Escape XML for HTML display
        escaped_response = (
            raw_response.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

        try:
            return render_to_string("templates/components/raw_response.html", {
                "escaped_response": escaped_response
            })
        except Exception as e:
            log.error(f"RawResponseComponent: Error rendering template: {e}")
            return None
