"""
Success Modal Component.

Builds success modals for successful PDMP requests.
"""

from typing import Any

from canvas_sdk.effects import Effect
from logger import log
from pdmp_bamboo.lib.ui.components import (
    AlertsComponent,
    AssessmentStatusComponent,
    NarxMessagesComponent,
    NarxScoresComponent,
    PatientHeaderComponent,
    RawResponseComponent,
    ReportButtonComponent,
)
from pdmp_bamboo.lib.ui.modals.base_modal import BaseModal


class SuccessModal(BaseModal):
    """Builds success modals for PDMP requests."""

    def __init__(self):
        super().__init__()
        self.alerts_component = AlertsComponent()
        self.assessment_component = AssessmentStatusComponent()
        self.scores_component = NarxScoresComponent()
        self.messages_component = NarxMessagesComponent()
        self.patient_header_component = PatientHeaderComponent()
        self.report_component = ReportButtonComponent()
        self.raw_response_component = RawResponseComponent()

    def create_success_modal(
        self,
        result: dict[str, Any],
        use_test_env: bool = False,
        patient_id: str | None = None,
        practitioner_id: str | None = None,
        organization_id: str | None = None,
    ) -> Effect:
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
            result,
            api_result,
            parsed_data,
            extraction_errors,
            use_test_env,
            patient_id,
            practitioner_id,
            organization_id,
        )

        # Create modal title
        title = self._create_modal_title(use_test_env)

        return self.create_modal(title, content)

    def _build_modal_content(
        self,
        result: dict[str, Any],
        api_result: dict[str, Any],
        parsed_data: dict[str, Any],
        extraction_errors: list[str],
        use_test_env: bool,
        patient_id: str | None,
        practitioner_id: str | None,
        organization_id: str | None,
    ) -> str:
        """Build the complete modal content via template."""
        from canvas_sdk.templates import render_to_string

        patient_data = result.get("patient_data", {})
        patient_header_html = self.patient_header_component.create_component(patient_data)

        scores_html = self.scores_component.create_component(parsed_data) or ""
        alerts_html = self.alerts_component.create_component(parsed_data) or ""
        messages_html = self.messages_component.create_component(parsed_data) or ""
        raw_response_html = self.raw_response_component.create_component(
            api_result.get("raw_response", "")
        ) or ""

        return render_to_string("templates/modals/success_modal_wrapper.html", {
            "patient_header_html": patient_header_html or "",
            "report_button_html": self.report_component.create_component(
                parsed_data,
                use_test_env=use_test_env,
                patient_id=patient_id,
                practitioner_id=practitioner_id,
                organization_id=organization_id,
            ) or "",
            "scores_html": scores_html,
            "messages_html": (alerts_html or messages_html),
            "raw_response_html": raw_response_html,
            "assessment_html": self.assessment_component.create_component(result) or "",
        })

    def _build_status_info(
        self, result: dict[str, Any], api_result: dict[str, Any], use_test_env: bool
    ) -> str:
        """Build status information section."""
        status_items = [
            f"Status Code: {api_result.get('status_code', 'N/A')}",
            f"Patient ID: {result.get('patient_id', 'N/A')}",
            f"Environment: {'Test Environment' if use_test_env else 'Production Environment'}",
        ]

        # Add request ID if available
        parsed_data = result.get("parsed_data", {})
        if parsed_data.get("request_id"):
            status_items.append(f"Request ID: {parsed_data['request_id']}")

        return self.create_info_box("Request Details", status_items, "")

    def _create_modal_title(self, use_test_env: bool) -> str:
        """Create the modal title based on environment."""
        if use_test_env:
            return "✅ PDMP Test Request Successful"
        else:
            return "✅ PDMP Request Successful"

    def _get_reference_css(self) -> str:
        """Deprecated - styles served from templates."""
        return ""
