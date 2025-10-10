"""
UI Service.

Main service for creating UI components and modals for PDMP responses.
Uses dependency injection for better testability and decoupling.
"""

from typing import Any

from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from logger import log
from pdmp_bamboo.lib.models.request_context import RequestContext
from pdmp_bamboo.lib.services.response_parser_service import ResponseParserService
from pdmp_bamboo.lib.ui.components import (
    AssessmentStatusComponent,
    NarxMessagesComponent,
    NarxScoresComponent,
    PatientHeaderComponent,
    ReportButtonComponent,
)
from pdmp_bamboo.lib.ui.effects import AssessmentEffectsService
from pdmp_bamboo.lib.ui.modals import DataValidationModal, ErrorModal, NoAccountModal, SuccessModal


class UIService:
    """
    Main service for creating UI components and modals.

    Uses dependency injection pattern for better testability and decoupling.
    All dependencies can be injected, but sensible defaults are provided.
    """

    def __init__(
        self,
        response_parser: ResponseParserService | None = None,
        assessment_effects: AssessmentEffectsService | None = None,
        success_modal: SuccessModal | None = None,
        error_modal: ErrorModal | None = None,
        data_validation_modal: DataValidationModal | None = None,
        no_account_modal: NoAccountModal | None = None,
        patient_header: PatientHeaderComponent | None = None,
        assessment_status: AssessmentStatusComponent | None = None,
        narx_scores: NarxScoresComponent | None = None,
        narx_messages: NarxMessagesComponent | None = None,
        report_button: ReportButtonComponent | None = None,
    ):
        """
        Initialize the UI service with optional dependency injection.

        Args:
            response_parser: Service for parsing PDMP responses (default: create new instance)
            assessment_effects: Service for creating assessment effects (default: create new instance)
            success_modal: Component for success modals (default: create new instance)
            error_modal: Component for error modals (default: create new instance)
            data_validation_modal: Component for validation error modals (default: create new instance)
            no_account_modal: Component for no account modal (default: create new instance)
            patient_header: Component for patient header (default: create new instance)
            assessment_status: Component for assessment status (default: create new instance)
            narx_scores: Component for NarxCare scores (default: create new instance)
            narx_messages: Component for clinical messages (default: create new instance)
            report_button: Component for report button (default: create new instance)
        """
        # Initialize modal components (use provided or create new)
        self.success_modal = success_modal or SuccessModal()
        self.error_modal = error_modal or ErrorModal()
        self.data_validation_modal = data_validation_modal or DataValidationModal()
        self.no_account_modal = no_account_modal or NoAccountModal()

        # Initialize effects service
        self.assessment_effects = assessment_effects or AssessmentEffectsService()

        # Initialize response parser service
        self.response_parser = response_parser or ResponseParserService()

        # Initialize UI components
        self.patient_header = patient_header or PatientHeaderComponent()
        self.assessment_status = assessment_status or AssessmentStatusComponent()
        self.narx_scores = narx_scores or NarxScoresComponent()
        self.narx_messages = narx_messages or NarxMessagesComponent()
        self.report_button = report_button or ReportButtonComponent()

    def create_response_ui_with_context(
        self, result: dict[str, Any], context: RequestContext
    ) -> list[Effect]:
        """
        Create UI effects for a PDMP response using RequestContext.

        This is the preferred method that uses RequestContext for cleaner parameter passing.

        Args:
            result: PDMP request result data
            context: Request context with all necessary IDs and settings

        Returns:
            List of Effects for the response
        """
        return self.create_response_ui(
            result=result,
            patient_id=context.patient_id,
            practitioner_id=context.practitioner_id,
            organization_id=context.organization_id,
        )

    def create_response_ui(
        self,
        result: dict[str, Any],
        patient_id: str | None = None,
        practitioner_id: str | None = None,
        organization_id: str | None = None,
    ) -> list[Effect]:
        """
        Create UI effects for a PDMP response.

        Note: Consider using create_response_ui_with_context() instead for cleaner API.

        Args:
            result: PDMP request result data
            use_test_env: Whether this is a test environment request
            patient_id: Patient ID for context
            practitioner_id: Practitioner ID for context
            organization_id: Organization ID for context

        Returns:
            List of Effects for the response
        """
        effects = []

        # Create assessment effects if request was successful
        if result.get("status") == "success":
            try:
                assessment_effects = self.assessment_effects.create_assessment_effects(
                    patient_id, practitioner_id, result
                )
                effects.extend(assessment_effects)
            except Exception as e:
                log.error(f"UIService: Failed to create assessment effects: {str(e)}")
        else:
            log.error("UIService: Skipping assessment effects for failed request")

        # Create modal effect with enhanced content
        try:
            modal_effect = self._create_enhanced_modal_effect(
                result, False, patient_id, practitioner_id, organization_id
            )
            effects.append(modal_effect)
        except Exception as e:
            log.error(f"UIService: Failed to create modal effect: {str(e)}")

        return effects

    def _create_enhanced_modal_effect(
        self,
        result: dict[str, Any],
        use_test_env: bool,
        patient_id: str | None,
        practitioner_id: str | None,
        organization_id: str | None,
    ) -> Effect:
        """Create the appropriate modal effect with enhanced content based on result status."""
        if result.get("status") == "success":
            return self._create_enhanced_success_modal(
                result, use_test_env, patient_id, practitioner_id, organization_id
            )
        else:
            return self.error_modal.create_error_modal(result, use_test_env)

    def _create_enhanced_success_modal(
        self,
        result: dict[str, Any],
        use_test_env: bool,
        patient_id: str | None,
        practitioner_id: str | None,
        organization_id: str | None,
    ) -> Effect:
        """Create enhanced success modal with parsed PDMP data and report button."""
        # Parse PDMP response for enhanced display
        raw_response = result.get("api_result", {}).get("raw_response", "")
        parsed_data = self.response_parser.parse_pdmp_response(raw_response)

        # Use components to generate HTML sections - Patient data is MANDATORY
        patient_data = result.get("patient_data", {})

        # Validate patient data is present and has required fields
        if not patient_data:
            error_msg = "CRITICAL ERROR: Patient data is mandatory for UI display but was not provided in result"
            log.error(f"UIService: {error_msg}")
            raise ValueError(error_msg)

        if not isinstance(patient_data, dict):
            error_msg = f"CRITICAL ERROR: Patient data must be a dictionary, got {type(patient_data)}: {patient_data}"
            log.error(f"UIService: {error_msg}")
            raise ValueError(error_msg)

        # Check for required patient fields
        required_fields = ["first_name", "last_name"]
        missing_fields = [field for field in required_fields if not patient_data.get(field)]
        if missing_fields:
            error_msg = f"CRITICAL ERROR: Patient data is missing required fields: {missing_fields}. Available fields: {list(patient_data.keys())}"
            log.error(f"UIService: {error_msg}")
            raise ValueError(error_msg)

        # Log successful patient data validation
        patient_name = (
            f"{patient_data.get('first_name', '')} {patient_data.get('last_name', '')}".strip()
        )

        # Create patient header component
        patient_header_html = self.patient_header.create_component(patient_data)

        if not patient_header_html:
            error_msg = f"CRITICAL ERROR: PatientHeaderComponent failed to create HTML for patient: {patient_name}"
            log.error(f"UIService: {error_msg}")
            raise ValueError(error_msg)

        assessment_html = self.assessment_status.create_component(result) or ""

        scores_html = self.narx_scores.create_component(parsed_data) or ""

        messages_html = self.narx_messages.create_component(parsed_data) or ""

        report_button_html = (
            self.report_button.create_component(
                parsed_data,
                use_test_env=use_test_env,
                patient_id=patient_id,
                practitioner_id=practitioner_id,
                organization_id=organization_id,
            )
            or ""
        )

        # Build the complete HTML content using components
        # Order: Patient Header -> [Report Button -> Scores -> Messages -> iframe container] -> Assessment
        from canvas_sdk.templates import render_to_string

        html_content = render_to_string("templates/modals/success_modal_wrapper.html", {
            "patient_header_html": patient_header_html,
            "report_button_html": report_button_html,
            "scores_html": scores_html,
            "messages_html": messages_html,
            "assessment_html": assessment_html
        })

        modal_title = "✅ PDMP Request Successful"

        return LaunchModalEffect(
            content=html_content,
            target=LaunchModalEffect.TargetType.RIGHT_CHART_PANE_LARGE,
            title=modal_title,
        ).apply()

    def create_data_validation_ui(
        self, missing_data: list[str], available_data: dict[str, Any] | None = None
    ) -> Effect:
        """
        Create UI for data validation errors.

        Args:
            missing_data: List of missing data field descriptions
            available_data: Dictionary of available data for context

        Returns:
            Effect for data validation modal
        """
        return self.data_validation_modal.create_data_validation_modal(missing_data, available_data)

    def create_error_ui(self, user_message: str, technical_details: str | None = None) -> Effect:
        """
        Create UI for general errors.

        Args:
            user_message: User-friendly error message
            technical_details: Technical error details for logging (not shown to user)

        Returns:
            Effect for error modal
        """
        log.error(
            f"UIService: Creating error UI - User: {user_message}, Technical: {technical_details}"
        )
        # Create error result dict for ErrorModal
        error_result = {
            "error_type": "unexpected_error",
            "errors": [user_message],
            "api_result": {"raw_response": technical_details or ""},
        }
        return self.error_modal.create_error_modal(error_result, use_test_env=False)

    def create_no_account_ui(self) -> Effect:
        """
        Create UI for users without Bamboo Health account.

        Returns:
            Effect for no account modal
        """
        log.info("UIService: Creating no Bamboo Health account UI")
        return self.no_account_modal.create_no_account_modal()
