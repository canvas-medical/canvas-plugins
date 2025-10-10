"""
Base Report API.

Base class for PDMP report API endpoints with shared functionality.
"""

import uuid
from abc import ABC
from http import HTTPStatus
from typing import Any

from canvas_sdk.effects.simple_api import HTMLResponse
from canvas_sdk.handlers.simple_api import SimpleAPIRoute
from canvas_sdk.handlers.simple_api.security import Credentials
from canvas_sdk.templates import render_to_string
from logger import log


class BaseReportAPI(SimpleAPIRoute, ABC):
    """Base class for PDMP report API endpoints."""

    def authenticate(self, credentials: Credentials) -> bool:
        """
        Authenticate the request.

        Args:
            credentials: Request credentials

        Returns:
            True to allow all authenticated requests
        """
        return True

    def _generate_request_id(self) -> str:
        """
        Generate unique request ID for tracking.

        Returns:
            Short unique request ID (8 characters)
        """
        return str(uuid.uuid4())[:8]

    def _extract_parameters(self) -> dict[str, Any]:
        """
        Extract and normalize request parameters.

        Returns:
            Dictionary of extracted parameters
        """
        return {
            "report_id": self.request.query_params.get("report_id"),
            "patient_id": self.request.query_params.get("patient_id"),
            "practitioner_id": self.request.query_params.get("practitioner_id"),
            "organization_id": self.request.query_params.get("organization_id"),
            "staff_id": self.request.query_params.get("staff_id"),
        }

    def _validate_parameters(self, params: dict[str, Any]) -> HTMLResponse | None:
        """
        Validate required parameters.

        Args:
            params: Dictionary of parameters to validate

        Returns:
            HTMLResponse error if validation fails, None if valid
        """
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

    def _log_request_details(self, params: dict[str, Any], request_id: str | None = None) -> None:
        """
        Log request details for debugging with request ID tracking.

        Args:
            params: Dictionary of parameters to log
            request_id: Optional request ID for tracking
        """
        request_id = request_id or self._generate_request_id()
        log.info(
            f"[{request_id}] PDMP API Request - "
            f"endpoint={self.PATH}, "
            f"report_id={params['report_id']}, "
            f"patient_id={params['patient_id']}, "
            f"practitioner_id={params['practitioner_id']}"
        )

    def _log_response_details(
        self, request_id: str, status_code: int, response_size: int = 0
    ) -> None:
        """
        Log response details for debugging.

        Args:
            request_id: Request ID for tracking
            status_code: HTTP status code
            response_size: Size of response content in bytes
        """
        log.info(
            f"[{request_id}] PDMP API Response - "
            f"endpoint={self.PATH}, "
            f"status={status_code}, "
            f"size={response_size} bytes"
        )

    def _create_error_response(
        self, title: str, message: str, status_code: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR
    ) -> HTMLResponse:
        """
        Create standardized error response using template.

        Args:
            title: Error title
            message: Error message details
            status_code: HTTP status code

        Returns:
            HTMLResponse with error content
        """
        html = render_to_string(
            "templates/error/handler_error.html", {"error_message": f"{title} - {message}"}
        )
        return HTMLResponse(html, status_code=status_code)

