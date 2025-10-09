"""
PDMP Bamboo Plugin Handler.

Action button handler for initiating PDMP requests from patient notes.
"""

from typing import Any

from canvas_sdk.effects import Effect
from canvas_sdk.events import Event
from canvas_sdk.handlers.action_button import ActionButton
from logger import log
from pdmp_bamboo.lib.services.pdmp_integration_service import PDMPIntegrationService


class PDMPRequestButton(ActionButton):
    """PDMP Request Action Button Handler."""

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

    def _validate_bamboo_account_configuration(self) -> bool:
        """
        Validate that user has Bamboo Health account configured.

        Checks for required credentials in secrets for either test or production environment.

        Returns:
            True if credentials are found, False otherwise
        """
        if not self.secrets:
            log.warning("PDMP-Protocol: No secrets provided")
            return False

        # Check for test environment credentials
        test_url = self.secrets.get("TEST_PDMP_API_URL")
        test_username = self.secrets.get("TEST_PDMP_API_USERNAME")
        test_password = self.secrets.get("TEST_PDMP_API_PASSWORD")

        has_test_credentials = bool(test_url and test_username and test_password)

        # Check for production environment credentials
        prod_url = self.secrets.get("PDMP_API_URL")
        prod_username = self.secrets.get("PDMP_API_USERNAME")
        prod_password = self.secrets.get("PDMP_API_PASSWORD")

        has_prod_credentials = bool(prod_url and prod_username and prod_password)

        # User needs at least one environment configured
        if has_test_credentials or has_prod_credentials:
            log.info(
                f"PDMP-Protocol: Bamboo Health account found (test: {has_test_credentials}, prod: {has_prod_credentials})"
            )
            return True
        else:
            log.warning("PDMP-Protocol: No Bamboo Health account credentials found in secrets")
            return False

    def handle(self) -> list[Effect]:
        """Handle the PDMP request."""
        log.info("PDMP-Protocol: Starting PDMP request")

        # Log input parameters
        log.info(f"PDMP-Protocol: self.target: {self.target}")
        log.info(f"PDMP-Protocol: self.context: {self.context}")
        log.info(
            f"PDMP-Protocol: self.secrets keys: {list(self.secrets.keys()) if self.secrets else 'None'}"
        )
        log.info(f"PDMP-Protocol: self.event: {self.event}")

        # Check if user has Bamboo Health account configured
        if not self._validate_bamboo_account_configuration():
            log.warning("PDMP-Protocol: User does not have Bamboo Health account configured")
            return [self.pdmp_service.ui_service.create_no_account_ui()]

        # Determine environment
        use_test_env = self.secrets.get("USE_TEST_ENV", "false").lower() == "true"
        log.info(f"PDMP-Protocol: Using test environment: {use_test_env}")

        try:
            # Process the request
            log.info("PDMP-Protocol: Calling PDMPIntegrationService.process_patient_pdmp_request")
            effects = self.pdmp_service.process_patient_pdmp_request(
                target=self.target,
                context=self.context,
                secrets=self.secrets,
                event=self.event,
                use_test_env=use_test_env,
            )

            log.info(
                f"PDMP-Protocol: Received {len(effects) if isinstance(effects, list) else 1} effects from service"
            )

            if isinstance(effects, list):
                log.info(f"PDMP-Protocol: Received {len(effects)} effects from service")

                for _i, effect in enumerate(effects):
                    if hasattr(effect, "content"):
                        log.info(f"    Content preview: {str(effect.content)[:100]}...")
                    if hasattr(effect, "target"):
                        log.info(f"    Target: {effect.target}")

                log.info("PDMP-Protocol: Returning list of effects to Canvas")
                return effects
            else:
                # Convert single effect to list
                log.info(f"PDMP-Protocol: Received single effect: {effects}")
                if hasattr(effects, "content"):
                    log.info(f"    Content preview: {str(effects.content)[:100]}...")
                if hasattr(effects, "target"):
                    log.info(f"    Target: {effects.target}")

                log.info("PDMP-Protocol: Converting single effect to list and returning to Canvas")
                return [effects]

        except Exception as e:
            log.error(f"PDMP-Protocol: Error in handle: {str(e)}")
            # Create user-friendly error effect using LaunchModalEffect
            from canvas_sdk.effects.launch_modal import LaunchModalEffect
            from canvas_sdk.templates import render_to_string

            error_html = render_to_string("templates/error/handler_error.html", {
                "error_message": str(e)
            })
            error_effect = LaunchModalEffect(
                content=error_html,
                target=LaunchModalEffect.TargetType.RIGHT_CHART_PANE_LARGE,
                title="PDMP Request Error",
            )
            return [error_effect.apply()]
