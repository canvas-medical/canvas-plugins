"""
Error Modal Component.

Builds error modals for failed PDMP requests.
"""

from typing import Any

from canvas_sdk.effects import Effect
from logger import log
from pdmp_bamboo.lib.ui.modals.base_modal import BaseModal


class ErrorModal(BaseModal):
    """Builds error modals for PDMP requests."""

    def create_error_modal(self, result: dict[str, Any], use_test_env: bool = False) -> Effect:
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

        # Build modal content using templates
        content = self._build_modal_content(error_type, errors, api_result, use_test_env)

        # Create modal title
        title = self._create_modal_title(False)

        return self.create_modal(title, content)

    def _build_modal_content(
        self, error_type: str, errors: list[str], api_result: dict[str, Any], use_test_env: bool
    ) -> str:
        from canvas_sdk.templates import render_to_string

        error_details = self._build_error_details(error_type, errors)
        api_details = self._build_api_details(api_result) if api_result.get("raw_response") else None
        help_section = self._build_help_section()

        return render_to_string("templates/modals/error_modal_content.html", {
            "error_details": error_details,
            "api_details": api_details,
            "help_section": help_section,
        })

    def _build_error_details(self, error_type: str, errors: list[str]) -> str:
        """Build error details section via template."""
        from canvas_sdk.templates import render_to_string
        return render_to_string("templates/components/error_details.html", {
            "error_title": self._get_error_title(error_type),
            "errors": errors,
        })

    def _build_api_details(self, api_result: dict[str, Any]) -> str:
        """Build API response details section via template."""
        from canvas_sdk.templates import render_to_string
        return render_to_string("templates/components/api_details.html", {
            "status_code": api_result.get("status_code", "N/A"),
            "response_url": api_result.get("response_url", "N/A"),
            "response_reason": api_result.get("response_reason"),
        })

    def _build_help_section(self) -> str:
        """Build help section with next steps via template."""
        from canvas_sdk.templates import render_to_string
        help_items = [
            "Check that all required patient data is present in Canvas",
            "Verify practitioner has valid NPI or DEA numbers",
            "Ensure organization and practice location data is complete",
            "Try the request again after verifying data",
            "Contact your system administrator if errors persist",
        ]
        return render_to_string("templates/components/help_section.html", {
            "items": help_items,
        })

    def _get_error_title(self, error_type: str) -> str:
        """Get a user-friendly error title based on error type."""
        error_titles = {
            "data_extraction_failed": "Data Extraction Failed",
            "xml_generation_failed": "XML Generation Failed",
            "configuration_error": "Configuration Error",
            "api_request_failed": "API Request Failed",
            "response_parsing_failed": "Response Parsing Failed",
            "unexpected_error": "Unexpected Error",
        }
        return error_titles.get(error_type, "Request Failed")

    def _create_modal_title(self, use_test_env: bool) -> str:
        """Create the modal title based on environment."""
        return "❌ PDMP Request Failed"
