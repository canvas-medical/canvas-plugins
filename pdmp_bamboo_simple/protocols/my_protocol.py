"""
PDMP Bamboo Plugin Protocol
"""

from typing import List
from canvas_sdk.effects import Effect
from canvas_sdk.handlers.action_button import ActionButton
from pdmp_bamboo_simple.utils.pdmp_workflow import handle_pdmp_request


class PDMPTestRequestProtocol(ActionButton):
    """PDMP Test Request Protocol - Test Environment without Certificates"""

    BUTTON_TITLE = "PDMP Request"
    BUTTON_KEY = "pdmp_request_button"
    BUTTON_LOCATION = ActionButton.ButtonLocation.NOTE_HEADER
    PRIORITY = 1

    def visible(self) -> bool:
        """Always show the button in note header."""
        return True

    def handle(self) -> List[Effect]:
        """Handle test PDMP request by calling shared workflow with test flag."""

        return handle_pdmp_request(self.target, self.context, self.secrets, self.event, use_test_env=True)

