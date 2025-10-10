"""
Raw Response Component.

Displays raw XML response in a collapsible section for debugging.
"""

from logger import log
from pdmp_bamboo.lib.ui.components.base_component import BaseComponent


class RawResponseComponent(BaseComponent):
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

        # Escape XML for HTML display (same as BaseXMLBuilder._escape_xml)
        escaped_response = (
            raw_response.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

        return self._render_template(
            "templates/components/raw_response.html", {"escaped_response": escaped_response}
        )
