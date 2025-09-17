"""
Success Modal Component

Builds success modals for successful PDMP requests.
"""

from typing import Dict, Any, List, Optional
from canvas_sdk.effects import Effect
from logger import log

from pdmp_bamboo.ui.modals.base_modal import BaseModal
from pdmp_bamboo.ui.components import (
    AssessmentStatusComponent,
    NarxScoresComponent,
    NarxMessagesComponent,
    ReportButtonComponent,
    RawResponseComponent
)


class SuccessModal(BaseModal):
    """Builds success modals for PDMP requests."""
    
    def __init__(self):
        super().__init__()
        self.assessment_component = AssessmentStatusComponent()
        self.scores_component = NarxScoresComponent()
        self.messages_component = NarxMessagesComponent()
        self.report_component = ReportButtonComponent()
        self.raw_response_component = RawResponseComponent()

    def create_success_modal(self,
                            result: Dict[str, Any],
                            use_test_env: bool = False,
                            patient_id: Optional[str] = None,
                            practitioner_id: Optional[str] = None,
                            organization_id: Optional[str] = None) -> Effect:
        """
        Create a success modal for a successful PDMP request.

        Args:
            result: PDMP request result data
            use_test_env: Whether this is a test environment request
            patient_id: Patient ID for context
            practitioner_id: Practitioner ID for context
            organization_id: Organization ID for context

        Returns:
            LaunchModalEffect for the success modal
        """
        log.info("SuccessModal: Creating success modal")

        # Extract data
        api_result = result.get("api_result", {})
        parsed_data = result.get("parsed_data", {})
        extraction_errors = result.get("extraction_errors", [])

        # Build modal content
        content = self._build_modal_content(
            result, api_result, parsed_data, extraction_errors,
            use_test_env, patient_id, practitioner_id, organization_id
        )

        # Create modal title
        title = self._create_modal_title(use_test_env)

        return self.create_modal(title, content)

    def _build_modal_content(self,
                           result: Dict[str, Any],
                           api_result: Dict[str, Any],
                           parsed_data: Dict[str, Any],
                           extraction_errors: List[str],
                           use_test_env: bool,
                           patient_id: Optional[str],
                           practitioner_id: Optional[str],
                           organization_id: Optional[str]) -> str:
        """Build the complete modal content."""

        # Main title
        content = self.create_title("✅ PDMP Request Successful", level=3, color="#2e7d32")

        # Status information
        status_info = self._build_status_info(result, api_result, use_test_env)
        content += status_info

        # Assessment status
        assessment_html = self.assessment_component.create_component(result)
        if assessment_html:
            content += assessment_html

        # NarxCare scores
        scores_html = self.scores_component.create_component(parsed_data)
        if scores_html:
            content += scores_html

        # Clinical messages
        messages_html = self.messages_component.create_component(parsed_data)
        if messages_html:
            content += messages_html

        # Report button
        report_html = self.report_component.create_component(
            parsed_data, use_test_env, patient_id, practitioner_id, organization_id
        )
        if report_html:
            content += report_html

        # Raw response
        raw_response_html = self.raw_response_component.create_component(api_result.get("raw_response", ""))
        if raw_response_html:
            content += raw_response_html

        return f'<div style="{self.default_styles["container"]}">{content}</div>'

    def _build_status_info(self, result: Dict[str, Any], api_result: Dict[str, Any], use_test_env: bool) -> str:
        """Build status information section."""
        status_items = [
            f"<strong>Status Code:</strong> {api_result.get('status_code', 'N/A')}",
            f"<strong>Patient ID:</strong> {result.get('patient_id', 'N/A')}",
            f"<strong>Environment:</strong> {'Test Environment' if use_test_env else 'Production Environment'}"
        ]

        # Add request ID if available
        parsed_data = result.get("parsed_data", {})
        if parsed_data.get("request_id"):
            status_items.append(f"<strong>Request ID:</strong> {parsed_data['request_id']}")

        return self.create_info_box("Request Details", status_items, "")

    def _create_modal_title(self, use_test_env: bool) -> str:
        """Create the modal title based on environment."""
        if use_test_env:
            return "✅ PDMP Test Request Successful"
        else:
            return "✅ PDMP Request Successful"