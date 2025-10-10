"""
Report Iframe API.

API endpoint that serves the full PDMP report as a complete HTML page
that can be embedded in an iframe within the Canvas modal.
"""

from http import HTTPStatus
from typing import Any

from canvas_sdk.effects.simple_api import HTMLResponse
from logger import log
from pdmp_bamboo.lib.services.report_service import ReportService
from pdmp_bamboo.routes.base_report_api import BaseReportAPI


class ReportIframeAPI(BaseReportAPI):
    """API endpoint for serving PDMP reports as iframe-ready HTML."""

    PATH = "/report-iframe"

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
        request_id = self._generate_request_id()

        # Extract and validate parameters
        params = self._extract_parameters()
        validation_error = self._validate_parameters(params)
        if validation_error:
            return [validation_error]

        # Log request details with tracking ID
        self._log_request_details(params, request_id)

        try:
            # Create report service
            report_service = ReportService()

            # Fetch complete report content
            result = report_service.fetch_pdmp_report(
                report_id=params["report_id"],
                patient_id=params["patient_id"],
                practitioner_id=params["practitioner_id"],
                secrets=self.secrets,
            )

            if result["success"]:
                # Wrap the report content in an iframe-friendly HTML structure
                iframe_html = self._create_iframe_html(result["report_content"])

                # Log successful response
                self._log_response_details(request_id, HTTPStatus.OK, len(iframe_html))

                log.info(f"[{request_id}] ReportIframeEndpoint: Returning iframe-ready HTML")
                return [HTMLResponse(iframe_html, status_code=HTTPStatus.OK)]
            else:
                log.error(
                    f"[{request_id}] ReportIframeEndpoint: Report fetch failed: {result['error_message']}"
                )
                error_html = self._create_error_html(result)

                # Log error response
                self._log_response_details(request_id, HTTPStatus.INTERNAL_SERVER_ERROR, len(error_html))

                return [HTMLResponse(error_html, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)]

        except Exception as e:
            log.error(f"[{request_id}] ReportIframeEndpoint: Unexpected error: {str(e)}", exc_info=True)
            error_html = self._create_error_html(
                {
                    "error_type": "unexpected_error",
                    "error_message": f"An unexpected error occurred: {str(e)}",
                }
            )

            # Log error response
            self._log_response_details(request_id, HTTPStatus.INTERNAL_SERVER_ERROR, len(error_html))

            return [HTMLResponse(error_html, status_code=HTTPStatus.INTERNAL_SERVER_ERROR)]

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
        from canvas_sdk.templates import render_to_string as render_template

        error_type = error_data.get("error_type", "unknown_error")
        error_message = error_data.get("error_message", "An unknown error occurred")

        return render_template(
            "templates/error/report_iframe_error.html",
            {"error_type": error_type, "error_message": error_message},
        )
