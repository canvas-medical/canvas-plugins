"""
PDMP Request Service

Main service for handling PDMP requests using the new modular architecture.
"""

from typing import Dict, Any, List, Tuple, Optional
from logger import log

from canvas_sdk.effects import Effect

# Import our new components
from pdmp_bamboo.api.client import PDMPClient, AuthHandler
from pdmp_bamboo.services.data_extraction import DataExtractionService
from pdmp_bamboo.services.ui_service import UIService
from pdmp_bamboo.services.xml_generation import XMLGenerationService
from pdmp_bamboo.utils.secrets_helper import get_secret_value


class PDMPRequestService:
    """Main service for handling PDMP requests."""
    
    def __init__(self):
        """Initialize the PDMP request service with all required components."""
        self.ui_service = UIService()
        log.info("PDMPRequestService: Initializing PDMP request service")
        
        # Initialize services
        self.data_extraction_service = DataExtractionService()
        self.xml_generation_service = XMLGenerationService()
        
        # Initialize API components
        self.pdmp_client = PDMPClient()
        self.auth_handler = AuthHandler()

        log.info("PDMPRequestService: PDMP request service initialized successfully")

    def process_pdmp_request(self,
                             target: str,
                             context: dict,
                             secrets: dict,
                             event,
                             use_test_env: bool = False) -> Effect | list[Effect]:
        """
        Process a complete PDMP request using the new modular architecture.

        This is the main entry point that replaces the old handle_pdmp_request function.

        Args:
            target: Patient ID from button target
            context: Canvas context dict containing user info
            secrets: Plugin secrets dict
            event: Canvas event object
            use_test_env: If True, uses test credentials and no certificates

        Returns:
            List of Effects (assessment effects + modal effects)
        """
        env_label = "test" if use_test_env else "production"
        log.info(f"PDMPIntegrationService: Starting PDMP request for {env_label} environment")

        try:
            # Step 1: Extract data
            log.info("PDMPIntegrationService: Step 1 - Extracting data")
            patient_id = target
            practitioner_id = None
            if isinstance(context, dict) and context.get("user"):
                practitioner_id = context["user"].get("id")

            extracted_data, extraction_errors = self.data_extraction_service.extract_all_data_for_pdmp(
                patient_id, practitioner_id
            )

            if not extracted_data:
                return [self.ui_service.create_data_validation_ui(extraction_errors)]

            # Step 2: Generate XML
            log.info("PDMPIntegrationService: Step 2 - Generating XML")
            try:
                pdmp_xml = self.xml_generation_service.create_pdmp_xml(extracted_data)
            except ValueError as e:
                return [self.ui_service.create_data_validation_ui([str(e)])]

            # Step 3: Validate API configuration
            log.info("PDMPIntegrationService: Step 3 - Validating API configuration")
            try:
                url_key = "TEST_PDMP_API_URL" if use_test_env else "PDMP_API_URL"
                base_url = get_secret_value(secrets, url_key)
                if not base_url:
                    return [self.ui_service.create_data_validation_ui([f"Secret '{url_key}' is required"])]
            except ValueError as e:
                return [self.ui_service.create_data_validation_ui([str(e)])]

            # Step 4: Send API request using new PDMPClient
            log.info("PDMPIntegrationService: Step 4 - Sending API request")

            # Build API URL
            if base_url.endswith("/"):
                api_url = f"{base_url}v5_1/patient"
            else:
                api_url = f"{base_url}/v5_1/patient"

            log.info(f"PDMPIntegrationService: Built API URL: {api_url}")

            # Use new PDMPClient
            api_result = self.pdmp_client.send_patient_request(
                api_url=api_url,
                xml_content=pdmp_xml,
                secrets=secrets,
                use_test_env=use_test_env,
                timeout=60
            )

            # Step 5: Create result object
            result = {
                "status": api_result.get("status", "error"),
                "patient_id": patient_id,
                "practitioner_id": practitioner_id,
                "environment": env_label,
                "extraction_errors": extraction_errors,
                "api_result": api_result,
                "request_xml": pdmp_xml,
                "note_id": event.context.get("note_id") if hasattr(event, 'context') else None
            }

            # Step 6: Create UI
            log.info("PDMPIntegrationService: Step 5 - Creating UI")
            return self.ui_service.create_response_ui(
                result, use_test_env, patient_id, practitioner_id
            )

        except Exception as e:
            log.error(f"PDMPIntegrationService: Unexpected error: {str(e)}")
            return [self.ui_service.create_data_validation_ui([str(e)])]
    
    def _create_error_result(self, error_type: str, errors: List[str]) -> Dict[str, Any]:
        """Create standardized error result."""
        return {
            "status": "error",
            "error_type": error_type,
            "errors": errors
        }
    
    def validate_credentials(self, secrets: Dict[str, str], use_test_env: bool = False) -> bool:
        """Validate that required credentials are available."""
        return self.auth_handler.validate_credentials(secrets, use_test_env)

