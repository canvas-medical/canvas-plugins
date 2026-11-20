"""Staff-authenticated proxy for the Virtuosis voice biomarker API."""

from __future__ import annotations

import json
from http import HTTPStatus
from urllib.parse import quote, urlencode

from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api import SimpleAPI, StaffSessionAuthMixin, api
from canvas_sdk.utils import Http

from virtuosis_voice_biomarker.validation import (
    normalize_analysis_query,
    validate_recording_id,
    validate_submission,
)

API_BASE_URL = "https://api.virtuosis.ai/v1.3"


class VirtuosisAnalysisAPI(StaffSessionAuthMixin, SimpleAPI):
    """Submit consented recordings and retrieve their analysis state."""

    PREFIX = "/analysis"

    @api.post("/")
    def analyze(self) -> list[Response | Effect]:
        """Submit a completed, consented recording for selected analyses."""
        request_body, validation_error = validate_submission(self.request.json())
        if validation_error:
            return [JSONResponse({"error": validation_error}, status_code=HTTPStatus.BAD_REQUEST)]
        response = self._request("POST", "/recordings", request_body)
        return [self._json_response(response)]

    @api.get("/<recording_id>")
    def result(self) -> list[Response | Effect]:
        """Retrieve current results for an authorized recording."""
        recording_id = self.request.path_params.get("recording_id")
        if not validate_recording_id(recording_id):
            return [
                JSONResponse(
                    {"error": "recording_id must be a UUID."},
                    status_code=HTTPStatus.BAD_REQUEST,
                )
            ]
        try:
            analyses = normalize_analysis_query(self.request.query_params.get("analysis"))
        except ValueError as error:
            return [JSONResponse({"error": str(error)}, status_code=HTTPStatus.BAD_REQUEST)]

        query = f"?{urlencode({'analysis': ','.join(analyses)})}" if analyses else ""
        path = f"/recordings/{quote(str(recording_id), safe='')}/analysis{query}"
        response = self._request("GET", path)
        return [self._json_response(response)]

    def _request(self, method: str, path: str, body: dict | None = None):
        headers = {
            "Authorization": f"Bearer {self.secrets['VIRTUOSIS_API_TOKEN']}",
            "Accept": "application/json",
        }
        client = Http()
        if method == "POST":
            headers["Content-Type"] = "application/json"
            return client.post(f"{API_BASE_URL}{path}", headers=headers, data=json.dumps(body))
        return client.get(f"{API_BASE_URL}{path}", headers=headers)

    @staticmethod
    def _json_response(response) -> JSONResponse:
        try:
            body = response.json()
        except (TypeError, ValueError):
            body = {"error": "Virtuosis returned a non-JSON response."}
        status_code = response.status_code
        if not isinstance(status_code, int) or not 100 <= status_code <= 599:
            status_code = HTTPStatus.BAD_GATEWAY
        return JSONResponse(body, status_code=status_code)
