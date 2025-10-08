"""
UI Service

Main service for creating UI components and modals for PDMP responses.
"""

from typing import Dict, Any, List, Optional
from canvas_sdk.effects import Effect
from logger import log

from pdmp_bamboo.ui.modals import SuccessModal, ErrorModal, DataValidationModal
from pdmp_bamboo.ui.effects import AssessmentEffectsService
from pdmp_bamboo.services.response_parser_service import ResponseParserService


class UIService:
    """Main service for creating UI components and modals."""

    def __init__(self):
        """Initialize the UI service with all required components."""

        # Initialize modal components
        self.success_modal = SuccessModal()
        self.error_modal = ErrorModal()
        self.data_validation_modal = DataValidationModal()

        # Initialize effects service
        self.assessment_effects = AssessmentEffectsService()

        # Initialize response parser service
        self.response_parser = ResponseParserService()

        log.info("UIService: UI service initialized successfully")

    def create_response_ui(self,
                          result: Dict[str, Any],
                          patient_id: Optional[str] = None,
                          practitioner_id: Optional[str] = None,
                          organization_id: Optional[str] = None) -> List[Effect]:
        """
        Create UI effects for a PDMP response.

        Args:
            result: PDMP request result data
            patient_id: Patient ID for context
            practitioner_id: Practitioner ID for context
            organization_id: Organization ID for context

        Returns:
            List of Effects for the response
        """
        effects = []

        # Create assessment effects if request was successful
        if result.get("status") == "success":
            log.info("UIService: Creating assessment effects for successful request")
            try:
                assessment_effects = self.assessment_effects.create_assessment_effects(
                    patient_id, practitioner_id, result
                )
                log.info(f"UIService: Created {len(assessment_effects)} assessment effects")
                effects.extend(assessment_effects)
            except Exception as e:
                log.error(f"UIService: Failed to create assessment effects: {str(e)}")
        else:
            log.info("UIService: Skipping assessment effects for failed request")

        # Create modal effect with enhanced content
        log.info("UIService: Creating modal effect")
        try:
            modal_effect = self._create_enhanced_modal_effect(
                result, patient_id, practitioner_id, organization_id
            )
            log.info(f"UIService: Created modal effect: {type(modal_effect)}")
            effects.append(modal_effect)
        except Exception as e:
            log.error(f"UIService: Failed to create modal effect: {str(e)}")

        log.info(f"UIService: Created {len(effects)} total UI effects")
        for i, effect in enumerate(effects):
            log.info(f"  Effect {i+1}: {type(effect)}")
            if hasattr(effect, 'content'):
                log.info(f"    Content preview: {str(effect.content)[:100]}...")
            if hasattr(effect, 'target'):
                log.info(f"    Target: {effect.target}")

        return effects

    def _create_enhanced_modal_effect(self,
                                    result: Dict[str, Any],
                                    patient_id: Optional[str],
                                    practitioner_id: Optional[str],
                                    organization_id: Optional[str]) -> Effect:
        """Create the appropriate modal effect with enhanced content based on result status."""

        if result.get("status") == "success":
            return self._create_enhanced_success_modal(
                result, patient_id, practitioner_id, organization_id
            )
        else:
            return self.error_modal.create_error_modal(result)

    def _create_enhanced_success_modal(self,
                                     result: Dict[str, Any],
                                     patient_id: Optional[str],
                                     practitioner_id: Optional[str],
                                     organization_id: Optional[str]) -> Effect:
        """Create enhanced success modal with parsed PDMP data and report button."""

        # Parse PDMP response for enhanced display
        raw_response = result.get("api_result", {}).get("raw_response", "")
        parsed_data = self.response_parser.parse_pdmp_response(raw_response)

        # Assessment status HTML
        assessment_html = ""
        if result.get("assessment_created"):
            assessment_html = f"""
            <div style="background-color: #e3f2fd; padding: 15px; border-radius: 4px; margin: 15px 0; border: 1px solid #bbdefb;">
                <h4 style="color: #1976d2; margin-top: 0;">�� Documentation Created</h4>
                <p style="margin: 5px 0; color: #666;">✅ Structured assessment added to note documenting PDMP check was performed</p>
            </div>
            """
        elif result.get("assessment_error"):
            assessment_html = f"""
            <div style="background-color: #fff3cd; padding: 15px; border-radius: 4px; margin: 15px 0; border: 1px solid #ffeaa7;">
                <h4 style="color: #f57c00; margin-top: 0;">⚠️ Documentation Warning</h4>
                <p style="margin: 5px 0; color: #8b4513;">Could not create structured assessment: {result.get("assessment_error", "Unknown error")}</p>
            </div>
            """

        # Generate scores HTML if available
        scores_html = ""
        if parsed_data.get("parsed") and parsed_data.get("narx_scores"):
            scores_html = f"""
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 4px; margin: 15px 0; border: 1px solid #dee2e6;">
                <h4 style="margin-top: 0; color: #495057;">📊 NarxCare Risk Scores</h4>
                {self.response_parser.generate_scores_html(parsed_data["narx_scores"])}
            </div>
            """

        # Generate messages HTML if available
        messages_html = ""
        if parsed_data.get("parsed") and parsed_data.get("narx_messages"):
            messages_html = f"""
            <div style="background-color: #fff3cd; padding: 15px; border-radius: 4px; margin: 15px 0; border: 1px solid #ffeaa7;">
                <h4 style="margin-top: 0; color: #856404;">🚨 Clinical Alerts</h4>
                {self.response_parser.generate_messages_html(parsed_data["narx_messages"])}
            </div>
            """

        # Generate report button HTML
        report_button_html = ""
        if parsed_data.get("parsed") and parsed_data.get("report_url"):
            report_url = parsed_data.get("report_url", "")
            expiration_date = parsed_data.get("report_expiration", "Unknown")
            report_button_html = self.response_parser.generate_report_button_html(
                report_url,
                expiration_date,
                patient_id=patient_id,
                practitioner_id=practitioner_id,
                organization_id=organization_id
            )

        # Build the complete HTML content
        html_content = f"""
        <div style="padding: 20px; font-family: Arial, sans-serif;">
            <h3 style="color: #2e7d32;">✅ PDMP Request Successful</h3>
            
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; margin: 15px 0;">
                <p><strong>Status Code:</strong> {result.get("api_result", {}).get("status_code", "N/A")}</p>
                <p><strong>Patient ID:</strong> {result.get("patient_id", "N/A")}</p>
                {"<p><strong>Request ID:</strong> " + parsed_data.get("request_id", "N/A") + "</p>" if parsed_data.get("request_id") else ""}
            </div>
            
            {assessment_html}
            {scores_html}
            {messages_html}
            {report_button_html}
            
            <div style="background-color: #e8f5e8; padding: 15px; border-radius: 4px; margin: 15px 0;">
                <h4>Raw PDMP Response:</h4>
                <details>
                    <summary style="cursor: pointer; color: #1976d2;">Click to view raw XML response</summary>
                    <pre style="background-color: white; padding: 10px; border-radius: 4px; overflow-x: auto; max-height: 300px; margin-top: 10px;">{raw_response}</pre>
                </details>
            </div>
        </div>
        """

        modal_title = (
            "✅ PDMP Request Successful"
        )

        from canvas_sdk.effects.launch_modal import LaunchModalEffect
        return LaunchModalEffect(
            content=html_content,
            target=LaunchModalEffect.TargetType.DEFAULT_MODAL,
            title=modal_title,
        ).apply()

    def create_data_validation_ui(self,
                                 missing_data: List[str],
                                 available_data: Optional[Dict[str, Any]] = None) -> Effect:
        """
        Create UI for data validation errors.

        Args:
            missing_data: List of missing data field descriptions
            available_data: Dictionary of available data for context

        Returns:
            Effect for data validation modal
        """
        log.info("UIService: Creating data validation UI")
        return self.data_validation_modal.create_data_validation_modal(missing_data, available_data)