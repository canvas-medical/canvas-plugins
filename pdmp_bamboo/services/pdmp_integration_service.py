"""
PDMP Integration Service

Main service that integrates all the components into a single workflow.
"""

from canvas_sdk.effects import Effect
from logger import log

from pdmp_bamboo.services.data_extraction import DataExtractionService
from pdmp_bamboo.services.xml_generation import XMLGenerationService
from pdmp_bamboo.services.ui_service import UIService
from pdmp_bamboo.api.client.pdmp_client import PDMPClient
from pdmp_bamboo.utils.secrets_helper import get_pdmp_api_url


class PDMPIntegrationService:
    """Main integration service for PDMP requests."""

    def __init__(self):
        """Initialize the integration service with all required components."""

        # Initialize all services
        self.data_extraction_service = DataExtractionService()
        self.xml_generation_service = XMLGenerationService()
        self.ui_service = UIService()
        self.pdmp_client = PDMPClient()


    def process_patient_pdmp_request(self,
                                     target: str,
                                     context: dict,
                                     secrets: dict,
                                     event) -> Effect | list[Effect]:
        """
        Process a complete PDMP request.

        Args:
            target: Patient ID from button target
            context: Canvas context dict containing user info
            secrets: Plugin secrets dict
            event: Canvas event object

        Returns:
            List of Effects (assessment effects + modal effects)
        """

        try:
            # Step 1: Extract data
            patient_id = target
            practitioner_id = None
            if isinstance(context, dict) and context.get("user"):
                practitioner_id = context["user"].get("id")

            extracted_data, extraction_errors = self.data_extraction_service.extract_all_data_for_pdmp(
                patient_id, practitioner_id
            )

            if not extracted_data:
                return self.ui_service.create_data_validation_ui(extraction_errors)

            # Step 2: Generate XML
            try:
                pdmp_xml = self.xml_generation_service.create_pdmp_xml(extracted_data)
            except ValueError as e:
                return self.ui_service.create_data_validation_ui([str(e)])

            # Step 3: Validate API configuration
            try:
                base_url = get_pdmp_api_url(secrets)
                if not base_url:
                    return self.ui_service.create_data_validation_ui([f"Secret PDMP_API_URL is required"])
            except ValueError as e:
                return self.ui_service.create_data_validation_ui([str(e)])

            # Step 4: Send API request using new PDMPClient

            # Build API URL
            if base_url.endswith("/"):
                api_url = f"{base_url}v5_1/patient"
            else:
                api_url = f"{base_url}/v5_1/patient"

            api_result = self.pdmp_client.send_patient_request(
                api_url=api_url,
                xml_content=pdmp_xml,
                secrets=secrets,
                staff_id=practitioner_id,
                timeout=60
            )

            # Step 5: Create result object
            result = {
                "status": api_result.get("status", "error"),
                "patient_id": patient_id,
                "practitioner_id": practitioner_id,
                "extraction_errors": extraction_errors,
                "api_result": api_result,
                "request_xml": pdmp_xml,
                "note_id": event.context.get("note_id") if hasattr(event, 'context') else None
            }

            # Step 6: Create UI

            # Extract organization_id from practitioner data if available
            organization_id = None
            if extracted_data and extracted_data.get("practitioner"):
                practitioner_dto = extracted_data["practitioner"]
                # Access the attribute directly on the DTO object
                organization_id = getattr(practitioner_dto, 'organization_id', None)
                log.info(f"PDMPIntegrationService: Extracted organization_id: {organization_id}")

            ui_effects = self.ui_service.create_response_ui(
                result, patient_id, practitioner_id, organization_id
            )
            return ui_effects

        except Exception as e:
            log.error(f"PDMPIntegrationService: Unexpected error: {str(e)}")
            return self.ui_service.create_data_validation_ui([str(e)])
