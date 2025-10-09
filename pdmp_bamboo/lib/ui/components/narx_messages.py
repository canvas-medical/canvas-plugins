"""
NarxCare Messages Component.

Displays clinical alert messages from PDMP responses.
"""

from typing import Any

from canvas_sdk.templates import render_to_string
from logger import log


class NarxMessagesComponent:
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

        try:
            return render_to_string("templates/components/narx_messages.html", {
                "messages": messages
            })
        except Exception as e:
            log.error(f"NarxMessagesComponent: Error rendering template: {e}")
            return None
