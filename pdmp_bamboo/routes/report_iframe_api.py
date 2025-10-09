"""
Report Iframe API.

API endpoint that serves the full PDMP report as a complete HTML page
that can be embedded in an iframe within the Canvas modal.
"""

from http import HTTPStatus
from typing import Any

from canvas_sdk.effects.simple_api import HTMLResponse
from canvas_sdk.handlers.simple_api import SimpleAPIRoute
from canvas_sdk.handlers.simple_api.security import Credentials
from logger import log
from pdmp_bamboo.lib.services.report_service import ReportService


class ReportIframeAPI(SimpleAPIRoute):
    """API endpoint for serving PDMP reports as iframe-ready HTML."""

    PATH = "/report-iframe"

    def authenticate(self, credentials: Credentials) -> bool:
        """Allow all authenticated requests."""
        return True

    def get(self) -> list:
        """
        Serve the full PDMP report as an iframe-ready HTML page.

        Query Parameters:
        - report_id: ID of the report to fetch (required)
        - patient_id: Canvas patient ID (required)
        - practitioner_id: Canvas practitioner ID (required)
        - organization_id: Canvas organization ID (optional)
        - env: Environment (test/prod, defaults to test)
        """
        # Extract and validate parameters
        params = self._extract_parameters()
        validation_error = self._validate_parameters(params)
        if validation_error:
            return [validation_error]

        # Log request details
        self._log_request_details(params)

        try:
            # Create report service
            report_service = ReportService()

            # Fetch complete report content
            result = report_service.fetch_pdmp_report(
                report_id=params["report_id"],
                patient_id=params["patient_id"],
                practitioner_id=params["practitioner_id"],
                secrets=self.secrets,
                use_test_env=params["use_test_env"],
            )

            if result["success"]:
                # Wrap the report content in an iframe-friendly HTML structure
                iframe_html = self._create_iframe_html(result["report_content"])
                log.info("ReportIframeEndpoint: Returning iframe-ready HTML")
                return [HTMLResponse(iframe_html, status_code=HTTPStatus.OK)]
            else:
                log.error(f"ReportIframeEndpoint: Report fetch failed: {result['error_message']}")
                error_html = self._create_error_html(result)
                return [HTMLResponse(error_html, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)]

        except Exception as e:
            log.error(f"ReportIframeEndpoint: Unexpected error: {str(e)}")
            error_html = self._create_error_html(
                {
                    "error_type": "unexpected_error",
                    "error_message": f"An unexpected error occurred: {str(e)}",
                }
            )
            return [HTMLResponse(error_html, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)]

    def _extract_parameters(self) -> dict[str, Any]:
        """Extract and normalize request parameters."""
        return {
            "report_id": self.request.query_params.get("report_id"),
            "env": self.request.query_params.get("env", "test"),
            "patient_id": self.request.query_params.get("patient_id"),
            "practitioner_id": self.request.query_params.get("practitioner_id"),
            "organization_id": self.request.query_params.get("organization_id"),
            "use_test_env": self.request.query_params.get("env", "test") == "test",
        }

    def _validate_parameters(self, params: dict[str, Any]) -> HTMLResponse | None:
        """Validate required parameters."""
        if not params["report_id"]:
            return self._create_error_html(
                {
                    "error_type": "missing_report_id",
                    "error_message": "Report ID is required to fetch the PDMP report.",
                }
            )

        if not params["patient_id"] or not params["practitioner_id"]:
            return self._create_error_html(
                {
                    "error_type": "missing_context",
                    "error_message": "Patient ID and Practitioner ID are required.",
                }
            )

        return None

    def _log_request_details(self, params: dict[str, Any]) -> None:
        """Log request details for debugging."""
        log.info(f"Iframe report request: report_id={params['report_id']}, env={params['env']}, patient={params['patient_id']}")

    def _create_iframe_html(self, report_content: str) -> str:
        """
        Create iframe-friendly HTML wrapper for the report content.

        Args:
            report_content: The full HTML content from the PDMP report

        Returns:
            Complete HTML page ready for iframe embedding
        """
        # Extract the body content and scripts from the report
        # The report content is already a complete HTML document
        return report_content

    def _create_error_html(self, error_data: dict[str, Any]) -> str:
        """Create iframe-friendly error HTML."""
        from canvas_sdk.templates import render_to_string

        error_type = error_data.get("error_type", "unknown_error")
        error_message = error_data.get("error_message", "An unknown error occurred")

        return render_to_string("templates/error/report_iframe_error.html", {
            "error_type": error_type,
            "error_message": error_message
        })
