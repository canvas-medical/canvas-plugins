"""
PDMP Integration Service.

Main service that integrates all the refactored components into a single workflow.
This replaces the old handle_pdmp_request function with clean, modular architecture.
Uses dependency injection and RequestContext for better decoupling.
"""

from datetime import datetime

from canvas_sdk.effects import Effect
from logger import log
from pdmp_bamboo.lib.api.pdmp_client import PDMPClient
from pdmp_bamboo.lib.models.request_context import RequestContext
from pdmp_bamboo.lib.services.data_extraction import DataExtractionService
from pdmp_bamboo.lib.services.ui_service import UIService
from pdmp_bamboo.lib.services.xml_generation import XMLGenerationService
from pdmp_bamboo.lib.utils.secrets_manager import SecretsManager


class PDMPIntegrationService:
    """
    Main integration service for PDMP requests.

    Uses dependency injection pattern for better testability and decoupling.
    """

    def __init__(
        self,
        data_extraction_service: DataExtractionService | None = None,
        xml_generation_service: XMLGenerationService | None = None,
        ui_service: UIService | None = None,
        pdmp_client: PDMPClient | None = None,
    ):
        """
        Initialize the integration service with optional dependency injection.

        Args:
            data_extraction_service: Service for extracting Canvas data (default: create new instance)
            xml_generation_service: Service for generating XML (default: create new instance)
            ui_service: Service for creating UI effects (default: create new instance)
            pdmp_client: Client for PDMP API calls (default: create new instance)
        """
        log.info("PDMPIntegrationService: Initializing")

        # Initialize all services (use provided or create new)
        self.data_extraction_service = data_extraction_service or DataExtractionService()
        self.xml_generation_service = xml_generation_service or XMLGenerationService()
        self.ui_service = ui_service or UIService()
        self.pdmp_client = pdmp_client or PDMPClient()

        log.info("PDMPIntegrationService: Initialized")

    def process_patient_pdmp_request(
        self, target: str, context: dict, secrets: dict, event
    ) -> Effect | list[Effect]:
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
        # Extract IDs from Canvas context
        patient_id = target
        practitioner_id = None
        if isinstance(context, dict) and context.get("user"):
            practitioner_id = context["user"].get("id")

        note_id = event.context.get("note_id") if hasattr(event, "context") else None

        # Create request context
        request_context = RequestContext(
            patient_id=patient_id,
            practitioner_id=practitioner_id,
            staff_id=str(practitioner_id) if practitioner_id else None,
            note_id=note_id,
        )

        log.info(f"PDMPIntegrationService: Starting PDMP request: {request_context}")

        try:

            # Step 1: Extract data
            log.info("PDMPIntegrationService: Step 1 - Extracting data")
            extracted_data, extraction_errors = (
                self.data_extraction_service.extract_all_data_for_pdmp(
                    request_context.patient_id, request_context.practitioner_id
                )
            )

            if not extracted_data:
                log.error(
                    "PDMPIntegrationService: Data extraction failed - cannot proceed with PDMP request"
                )
                log.error(f"PDMPIntegrationService: Extraction errors: {extraction_errors}")
                return self.ui_service.create_data_validation_ui(extraction_errors)

            # Update context with organization_id if available
            if extracted_data and extracted_data.get("practitioner"):
                practitioner_dto = extracted_data["practitioner"]
                request_context.organization_id = getattr(practitioner_dto, "organization_id", None)
                log.info(
                    f"PDMPIntegrationService: Updated context with organization_id: {request_context.organization_id}"
                )

            # Step 2: Generate XML
            log.info("PDMPIntegrationService: Step 2 - Generating XML")
            try:
                pdmp_xml = self.xml_generation_service.create_pdmp_xml(extracted_data)
                log.info(
                    f"PDMPIntegrationService: XML generation successful ({len(pdmp_xml)} characters)"
                )
            except ValueError as e:
                log.error(f"PDMPIntegrationService: XML generation failed: {str(e)}")
                log.error(
                    f"PDMPIntegrationService: Available extracted data keys: {list(extracted_data.keys()) if extracted_data else 'None'}"
                )

                # Create available_data for validation modal to show what we have
                available_data = {}
                if extracted_data and extracted_data.get("patient"):
                    available_data["patient"] = extracted_data["patient"].to_dict()

                return self.ui_service.create_data_validation_ui([str(e)], available_data)

            # Step 3: Get API configuration and staff credentials
            log.info("PDMPIntegrationService: Step 3 - Getting API configuration")
            try:
                sm = SecretsManager(secrets)
                api_base_url = sm.get_api_base_url()

                # Resolve staff credentials
                current_staff_id = request_context.staff_id
                if not current_staff_id:
                    raise ValueError("Missing current staff user id in context")

                username, password = sm.get_staff_credentials(str(current_staff_id))
                log.info("PDMPIntegrationService: Resolved staff credentials for current user")
            except ValueError as e:
                log.error(f"PDMPIntegrationService: API configuration failed: {str(e)}")

                # Create available_data for validation modal to show what we have
                available_data = {}
                if extracted_data and extracted_data.get("patient"):
                    available_data["patient"] = extracted_data["patient"].to_dict()

                return self.ui_service.create_data_validation_ui([str(e)], available_data)

            # Step 4: Send API request
            log.info("PDMPIntegrationService: Step 4 - Sending API request")
            api_result = self.pdmp_client.send_patient_request(
                api_base_url=api_base_url,
                xml_content=pdmp_xml,
                username=username,
                password=password,
            )

            # Step 5: Create result object with initial patient data
            log.info("PDMPIntegrationService: Step 5 - Creating result object with patient data")

            # Convert patient DTO to dictionary for UI display
            patient_data_dict = {}
            if extracted_data and extracted_data.get("patient"):
                patient_dto = extracted_data["patient"]
                patient_data_dict = patient_dto.to_dict()
                log.info(
                    f"PDMPIntegrationService: Converted patient DTO to dict with keys: {list(patient_data_dict.keys())}"
                )
                log.info(
                    f"PDMPIntegrationService: Patient name: {patient_data_dict.get('first_name', '')} {patient_data_dict.get('last_name', '')}"
                )
                log.info(
                    f"PDMPIntegrationService: Patient DOB: {patient_data_dict.get('birth_date', 'N/A')}"
                )
                log.info(
                    f"PDMPIntegrationService: Patient sex: {patient_data_dict.get('sex', 'N/A')}"
                )
            else:
                log.error(
                    "PDMPIntegrationService: No patient data available for UI display - this will cause patient header to fail"
                )

            result = {
                "status": api_result.get("status", "error"),
                "patient_id": request_context.patient_id,
                "practitioner_id": request_context.practitioner_id,
                "environment": request_context.env_label,
                "extraction_errors": extraction_errors,
                "api_result": api_result,
                "request_xml": pdmp_xml,
                "note_id": request_context.note_id,
                "patient_data": patient_data_dict,  # Add initial patient data for UI display
            }

            log.info(
                f"PDMPIntegrationService: Result object created with {len(result)} keys: {list(result.keys())}"
            )
            log.info(
                f"PDMPIntegrationService: Patient data included: {'Yes' if patient_data_dict else 'No'}"
            )

            # Step 6: Create UI using RequestContext
            log.info("PDMPIntegrationService: Step 6 - Creating UI")
            log.info(f"PDMPIntegrationService: Request context: {request_context}")

            ui_effects = self.ui_service.create_response_ui_with_context(result, request_context)
            return ui_effects

        except Exception as e:
            log.error(f"PDMPIntegrationService: Unexpected error: {str(e)}")
            # Create user-friendly error response
            error_message = "An unexpected error occurred while processing the PDMP request. Please try again or contact support."
            return self.ui_service.create_error_ui(error_message, str(e))
