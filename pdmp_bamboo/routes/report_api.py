"""
Report API.

Clean API endpoint for PDMP report requests.
Handles HTTP concerns and delegates business logic to ReportService.
"""

from http import HTTPStatus
from typing import Any

from canvas_sdk.effects.simple_api import HTMLResponse
from logger import log
from pdmp_bamboo.lib.services.report_service import ReportService
from pdmp_bamboo.routes.base_report_api import BaseReportAPI


class ReportAPI(BaseReportAPI):
    """Clean API endpoint for PDMP report requests."""

    PATH = "/report"

    def get(self) -> list:
        """Handle report requests with clean separation of concerns."""
        request_id = self._generate_request_id()

        # Extract and validate parameters
        params = self._extract_parameters()
        validation_error = self._validate_parameters(params)
        if validation_error:
            return [validation_error]

        # Log request details with tracking ID
        self._log_request_details(params, request_id)

        try:
            report_service = ReportService()

            # Delegate to service layer
            result = report_service.fetch_pdmp_report(
                report_id=params["report_id"],
                patient_id=params["patient_id"],
                practitioner_id=params["practitioner_id"],
                secrets=self.secrets,
            )

            response = self._create_response(result, params)

            # Log response details
            if response and len(response) > 0:
                status_code = getattr(response[0], "status_code", 200)
                content = getattr(response[0], "content", "")
                self._log_response_details(request_id, status_code, len(content) if content else 0)

            return response

        except Exception as e:
            log.error(f"[{request_id}] ReportEndpoint: Unexpected error: {str(e)}", exc_info=True)
            return [self._create_error_response("Unexpected Error", f"Unexpected error: {str(e)}")]

    def _create_response(self, result: dict[str, Any], params: dict[str, Any]) -> list:
        """Create appropriate HTTP response based on service result."""
        if result["success"]:
            return [HTMLResponse(result["report_content"], status_code=HTTPStatus.OK)]
        else:
            return [
                self._create_error_response(
                    f"Failed to fetch PDMP report: {result['error_message']}",
                    f"Error Type: {result['error_type']}",
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                )
            ]
