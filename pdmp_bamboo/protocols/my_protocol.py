"""
PDMP Bamboo Plugin Protocol
"""

from typing import List, Any
from canvas_sdk.effects import Effect
from canvas_sdk.events import Event
from canvas_sdk.handlers.action_button import ActionButton
from logger import log

from pdmp_bamboo.services.pdmp_integration_service import PDMPIntegrationService

class PDMPRequestProtocol(ActionButton):
    """PDMP Request Protocol """

    BUTTON_TITLE = "PDMP Request"
    BUTTON_KEY = "pdmp_request_button"
    BUTTON_LOCATION = ActionButton.ButtonLocation.NOTE_HEADER
    PRIORITY = 1

    def __init__(
            self,
            event: Event,
            secrets: dict[str, Any] | None = None,
            environment: dict[str, Any] | None = None,
    ):
        super().__init__(event, secrets, environment)
        self.pdmp_service = PDMPIntegrationService()

    def visible(self) -> bool:
        """Always show the button in note header."""
        return True


    def handle(self) -> List[Effect]:
        """Handle the PDMP request."""
        log.info("PDMP-Protocol: Starting PDMP request")

        try:
            # Process the request
            effects = self.pdmp_service.process_patient_pdmp_request(
                target=self.target,
                context=self.context,
                secrets=self.secrets,
                event=self.event
            )

            return effects

        except Exception as e:
            log.error(f"PDMP-Protocol: Error in handle: {str(e)}")
            raise

