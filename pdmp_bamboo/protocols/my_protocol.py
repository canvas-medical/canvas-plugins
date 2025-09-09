"""
PDMP Bamboo Plugin Protocol
"""

from typing import List
from canvas_sdk.effects import Effect
from canvas_sdk.handlers.action_button import ActionButton

from pdmp_bamboo.utils.pdmp_workflow import handle_pdmp_request, handle_pdmp_mock_request


class PDMPRequestProtocol(ActionButton):
    """PDMP Request Protocol - Production with Certificates"""

    BUTTON_TITLE = "PDMP Request (Prod)"
    BUTTON_KEY = "pdmp_request_button_prod"
    BUTTON_LOCATION = ActionButton.ButtonLocation.NOTE_HEADER
    PRIORITY = 1

    def visible(self) -> bool:
        """Always show the button in note header."""
        return True

    def handle(self) -> List[Effect]:
        """Extract Canvas data and send PDMP request."""
        return handle_pdmp_request(
            self.target, self.context, self.secrets, self.event, use_test_env=False
        )


class PDMPTestRequestProtocol(ActionButton):
    """PDMP Test Request Protocol - Test Environment without Certificates"""

    BUTTON_TITLE = "PDMP Request (Test)"
    BUTTON_KEY = "pdmp_request_button_test"
    BUTTON_LOCATION = ActionButton.ButtonLocation.NOTE_HEADER
    PRIORITY = 2

    def visible(self) -> bool:
        """Always show the button in note header."""
        return True

    def handle(self) -> List[Effect]:
        """Handle test PDMP request by calling shared workflow with test flag."""
        return handle_pdmp_request(
            self.target, self.context, self.secrets, self.event, use_test_env=True
        )


class PDMPMockRequestProtocol(ActionButton):
    """PDMP Mock Request Protocol - Uses template mock data for testing functionality"""

    BUTTON_TITLE = "PDMP Request (Mock)"
    BUTTON_KEY = "pdmp_request_button_mock"
    BUTTON_LOCATION = ActionButton.ButtonLocation.NOTE_HEADER
    PRIORITY = 3

    def visible(self) -> bool:
        """Always show the button in note header."""
        return True

    def handle(self) -> List[Effect]:
        """Handle mock PDMP request using template data."""
        return handle_pdmp_mock_request(self.target, self.context, self.secrets, self.event)
