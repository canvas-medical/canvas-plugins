"""
Error Modal Component

Builds error modals for failed PDMP requests.
"""

from typing import Dict, Any, List
from canvas_sdk.effects import Effect
from logger import log

from pdmp_bamboo.ui.modals.base_modal import BaseModal


class ErrorModal(BaseModal):
    """Builds error modals for PDMP requests."""
    
    def create_error_modal(self,
                          result: Dict[str, Any],
                          use_test_env: bool = False) -> Effect:
        """
        Create an error modal for a failed PDMP request.

        Args:
            result: PDMP request result data
            use_test_env: Whether this is a test environment request

        Returns:
            LaunchModalEffect for the error modal
        """
        log.info("ErrorModal: Creating error modal")

        # Extract error information
        error_type = result.get("error_type", "unknown_error")
        errors = result.get("errors", ["Unknown error occurred"])
        api_result = result.get("api_result", {})

        # Build modal content
        content = self._build_modal_content(error_type, errors, api_result, use_test_env)

        # Create modal title
        title = self._create_modal_title(use_test_env)

        return self.create_modal(title, content)

    def _build_modal_content(self,
                           error_type: str,
                           errors: List[str],
                           api_result: Dict[str, Any],
                           use_test_env: bool) -> str:
        """Build the complete modal content."""

        # Main title
        content = self.create_title("❌ PDMP Request Failed", level=3, color="#d32f2f")

        # Error details
        error_details = self._build_error_details(error_type, errors)
        content += error_details

        # API response details if available
        if api_result.get("raw_response"):
            api_details = self._build_api_details(api_result)
            content += api_details

        # Help section
        help_section = self._build_help_section()
        content += help_section

        return f'<div style="{self.default_styles["container"]}">{content}</div>'

    def _build_error_details(self, error_type: str, errors: List[str]) -> str:
        """Build error details section."""
        error_title = self._get_error_title(error_type)
        return self.create_error_box(error_title, errors, "❌")

    def _build_api_details(self, api_result: Dict[str, Any]) -> str:
        """Build API response details section."""
        api_items = [
            f"<strong>Status Code:</strong> {api_result.get('status_code', 'N/A')}",
            f"<strong>Response URL:</strong> {api_result.get('response_url', 'N/A')}"
        ]

        if api_result.get("response_reason"):
            api_items.append(f"<strong>Response Reason:</strong> {api_result['response_reason']}")

        return self.create_info_box("API Response Details", api_items, "")

    def _build_help_section(self) -> str:
        """Build help section with next steps."""
        help_items = [
            "Check that all required patient data is present in Canvas",
            "Verify practitioner has valid NPI or DEA numbers",
            "Ensure organization and practice location data is complete",
            "Try the request again after verifying data",
            "Contact your system administrator if errors persist"
        ]

        return self.create_info_box("What to do next", help_items, "💡")

    def _get_error_title(self, error_type: str) -> str:
        """Get a user-friendly error title based on error type."""
        error_titles = {
            "data_extraction_failed": "Data Extraction Failed",
            "xml_generation_failed": "XML Generation Failed",
            "configuration_error": "Configuration Error",
            "api_request_failed": "API Request Failed",
            "response_parsing_failed": "Response Parsing Failed",
            "unexpected_error": "Unexpected Error"
        }
        return error_titles.get(error_type, "Request Failed")

    def _create_modal_title(self, use_test_env: bool) -> str:
        """Create the modal title based on environment."""
        if use_test_env:
            return "❌ PDMP Test Request Failed"
        else:
            return "❌ PDMP Request Failed"