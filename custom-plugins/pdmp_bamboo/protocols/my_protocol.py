"""
PDMP Bamboo Plugin Protocol
"""

from typing import List, Any
from canvas_sdk.effects import Effect
from canvas_sdk.events import Event
from canvas_sdk.handlers.action_button import ActionButton
from logger import log

from pdmp_bamboo.services.pdmp_integration_service import PDMPIntegrationService


def safe_str(obj):
    """Safely convert object to string representation."""
    try:
        if hasattr(obj, '__dict__'):
            return str(obj.__dict__)
        elif hasattr(obj, '__iter__') and not isinstance(obj, str):
            return str(list(obj))
        else:
            return str(obj)
    except Exception as e:
        return f"<Error converting to string: {e}>"

class PDMPRequestProtocol(ActionButton):
    """PDMP Test Request Protocol - Test Environment without Certificates"""

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

        # Log input parameters
        log.info(f"PDMP-Protocol: self.target: {self.target}")
        log.info(f"PDMP-Protocol: self.context: {self.context}")
        log.info(f"PDMP-Protocol: self.secrets keys: {list(self.secrets.keys()) if self.secrets else 'None'}")
        log.info(f"PDMP-Protocol: self.event: {self.event}")

        # Determine environment
        use_test_env = self.secrets.get("USE_TEST_ENV", "false").lower() == "true"
        use_test_env = True # TODO: HARDCODE FOR TESTING
        log.info(f"PDMP-Protocol: Using test environment: {use_test_env}")

        try:
            # Process the request
            log.info("PDMP-Protocol: Calling PDMPIntegrationService.process_patient_pdmp_request")
            effects = self.pdmp_service.process_patient_pdmp_request(
                target=self.target,
                context=self.context,
                secrets=self.secrets,
                event=self.event,
                use_test_env=use_test_env
            )

            log.info(f"PDMP-Protocol: Received {len(effects) if isinstance(effects, list) else 1} effects from service")

            if isinstance(effects, list):
                log.info(f"PDMP-Protocol: Received {len(effects)} effects from service")

                for i, effect in enumerate(effects):
                    if hasattr(effect, 'content'):
                        log.info(f"    Content preview: {str(effect.content)[:100]}...")
                    if hasattr(effect, 'target'):
                        log.info(f"    Target: {effect.target}")

                log.info("PDMP-Protocol: Returning list of effects to Canvas")
                return effects
            else:
                # Convert single effect to list
                log.info(f"PDMP-Protocol: Received single effect: {effects}")
                if hasattr(effects, 'content'):
                    log.info(f"    Content preview: {str(effects.content)[:100]}...")
                if hasattr(effects, 'target'):
                    log.info(f"    Target: {effects.target}")

                log.info("PDMP-Protocol: Converting single effect to list and returning to Canvas")
                return [effects]

        except Exception as e:
            log.error(f"PDMP-Protocol: Error in handle: {str(e)}")
            raise

