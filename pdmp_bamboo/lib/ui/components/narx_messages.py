"""
NarxCare Messages Component.

Displays clinical alert messages from PDMP responses.
"""

from typing import Any

from logger import log
from pdmp_bamboo.lib.ui.components.base_component import BaseComponent


class NarxMessagesComponent(BaseComponent):
    """Component for displaying NarxCare clinical alert messages."""

    def create_component(self, parsed_data: dict[str, Any]) -> str | None:
        """
        Create clinical messages component.

        Args:
            parsed_data: Parsed PDMP response data

        Returns:
            HTML string for messages display, or None if no messages
        """
        if not parsed_data.get("parsed") or not parsed_data.get("narx_messages"):
            return None

        messages = parsed_data["narx_messages"]
        log.info(
            f"NarxMessagesComponent: Creating messages component with {len(messages)} messages"
        )

        return self._render_template(
            "templates/components/narx_messages.html", {"messages": messages}
        )
