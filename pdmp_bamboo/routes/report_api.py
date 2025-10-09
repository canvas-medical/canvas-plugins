"""
Report API.

Clean API endpoint for PDMP report requests.
Handles HTTP concerns and delegates business logic to ReportService.
"""

from http import HTTPStatus
from typing import Any

from canvas_sdk.effects.simple_api import HTMLResponse
from canvas_sdk.handlers.simple_api import SimpleAPIRoute
from canvas_sdk.handlers.simple_api.security import Credentials
from logger import log
from pdmp_bamboo.lib.services.report_service import ReportService


class ReportAPI(SimpleAPIRoute):
    """Clean API endpoint for PDMP report requests."""

    PATH = "/report"

    def authenticate(self, credentials: Credentials) -> bool:
        """
        Authenticate the request.

        Args:
            credentials: Request credentials

        Returns:
            True to allow all authenticated requests
        """
        return True

    def get(self) -> list:
        """Handle report requests with clean separation of concerns."""
        # Extract and validate parameters
        params = self._extract_parameters()
        validation_error = self._validate_parameters(params)
        if validation_error:
            return [validation_error]

        # Log request details
        self._log_request_details(params)

        try:
            report_service = ReportService()

            # Delegate to service layer
            result = report_service.fetch_pdmp_report(
                report_id=params["report_id"],
                patient_id=params["patient_id"],
                practitioner_id=params["practitioner_id"],
                secrets=self.secrets,
                use_test_env=params["use_test_env"],
            )

            return self._create_response(result, params)

        except Exception as e:
            log.error(f"ReportEndpoint: Unexpected error: {str(e)}")
            return [self._create_error_response("Unexpected Error", f"Unexpected error: {str(e)}")]

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
            return self._create_error_response(
                "Missing Report ID",
                "Report ID is required to fetch the PDMP report.",
                HTTPStatus.BAD_REQUEST,
            )

        if not params["patient_id"] or not params["practitioner_id"]:
            return self._create_error_response(
                "Missing Context",
                "Patient ID and Practitioner ID are required.",
                HTTPStatus.BAD_REQUEST,
            )

        return None

    def _log_request_details(self, params: dict[str, Any]) -> None:
        """Log request details for debugging."""
        log.info(f"Report request: report_id={params['report_id']}, env={params['env']}, patient={params['patient_id']}")

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

    def _create_error_response(
        self, title: str, message: str, status_code: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR
    ) -> HTMLResponse:
        """Create standardized error response using template."""
        from canvas_sdk.templates import render_to_string
        html = render_to_string("templates/error/handler_error.html", {
            "error_message": f"{title} - {message}"
        })
        return HTMLResponse(html, status_code=status_code)
