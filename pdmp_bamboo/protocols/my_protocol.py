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

    # def __init__(self):
    #     super().__init__()
    #     self.integration_service = PDMPIntegrationService()

    # integration_service = PDMPIntegrationService()

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

#     def handle(self) -> List[Effect]:
#         """Handle test PDMP request by calling shared workflow with test flag."""
#         # Initialize service
#
#         # Log all the protocol attributes
#         # log.info("=" * 80)
#         # log.info("PDMP-Protocol: PROTOCOL ATTRIBUTES DEBUG")
#         # log.info("=" * 80)
#         #
#         # # Log self.target
#         # log.info("PDMP-Protocol: self.target:")
#         # log.info(f"  Value: {safe_str(self.target)}")
#         #
#         # # Log self.context
#         # log.info("PDMP-Protocol: self.context:")
#         # log.info(f"  Value: {safe_str(self.context)}")
#         #
#         # # Log self.secrets
#         # log.info("PDMP-Protocol: self.secrets:")
#         # log.info(f"  Value: {safe_str(self.secrets)}")
#         #
#         # # Log self.event
#         # log.info("PDMP-Protocol: self.event:")
#         # log.info(f"  Value: {safe_str(self.event)}")
#         #
#         # log.info("=" * 80)
#
#
#         # data_service = DataExtractionService()
#         # # Extract patient data
#         # # patient_dto, errors = data_service.extract_patient(self.target)
#         # practitioner_id = None
#         # if isinstance(self.context, dict) and self.context.get("user"):
#         #     practitioner_id = self.context["user"].get("id")
#         # data_service.extract_all_data_for_pdmp(self.target,practitioner_id)
#         #
#         # # if patient_dto:
#         # #     # Use typed DTO
#         # #     print(f"Patient: {patient_dto.first_name} {patient_dto.last_name}")
#         # #     print(f"Address: {patient_dto.address.street}, {patient_dto.address.city}")
#         # #
#         # #     # Check validation errors
#         # #     if errors:
#         # #         print(f"Validation errors: {errors}")
#         #
#         # return handle_pdmp_request(self.target, self.context, self.secrets, self.event, use_test_env=True)
#         # return []
#         integration_service = PDMPIntegrationService()
#         integration_service.process_pdmp_request(
#             target=self.target,
#             context=self.context,
#             secrets=self.secrets,
#             event=self.event,
#             use_test_env=True  # This is a test request
#         )
#
#         return []
#
#         # try:
#         #     # Use the new integration service
#         #     effects = self.integration_service.process_pdmp_request(
#         #         target=self.target,
#         #         context=self.context,
#         #         secrets=self.secrets,
#         #         event=self.event,
#         #         use_test_env=True  # This is a test request
#         #     )
#         #
#         #     log.info(f"PDMP-Protocol-New: Created {len(effects)} effects")
#         #     return effects
#         #
#         # except Exception as e:
#         #     log.error(f"PDMP-Protocol-New: Error in handle: {str(e)}")
#         #     return []


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
            log.info("PDMP-Protocol: Calling PDMPIntegrationService.process_pdmp_request")
            effects = self.pdmp_service.process_pdmp_request(
                target=self.target,
                context=self.context,
                secrets=self.secrets,
                event=self.event,
                use_test_env=use_test_env
            )

            log.info(f"PDMP-Protocol: Received {len(effects) if isinstance(effects, list) else 1} effects from service")
            # log.info(f"PDMP-Protocol: Effects type: {effects}")

            # Ensure we always return a list
            if isinstance(effects, list):
                log.info(f"PDMP-Protocol: Received {len(effects)} effects from service")
                # log.info(f"PDMP-Protocol: Effects type: {type(effects)}")

                for i, effect in enumerate(effects):
                    # log.info(f"  Effect {i + 1}: {type(effect)}")
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

