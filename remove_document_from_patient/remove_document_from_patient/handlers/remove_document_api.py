"""
Remove Document From Patient API Handler.

This module provides a Simple API endpoint for removing/unlinking a patient
from a document in the Data Integration queue.

Example usage:
    curl -X POST /plugin-io/api/remove_document_from_patient/remove-document-from-patient \
         -H "Content-Type: application/json" \
         -d '{"document_id": "50272cbb-3051-4bcd-b627-8d5b6c3e1cde"}'

    # With optional confidence score:
    curl -X POST /plugin-io/api/remove_document_from_patient/remove-document-from-patient \
         -H "Content-Type: application/json" \
         -d '{"document_id": "50272cbb-3051-4bcd-b627-8d5b6c3e1cde", "confidence_score": 0.95}'
"""

from canvas_sdk.effects.data_integration import RemoveDocumentFromPatient
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api import SimpleAPIRoute
from canvas_sdk.handlers.simple_api.security import Credentials
from logger import log


class RemoveDocumentFromPatientAPI(SimpleAPIRoute):
    """
    Simple API endpoint to remove/unlink a patient from a document.

    This endpoint is typically used by LLM-based document processing systems
    when they determine that a document should not be linked to a patient.

    POST /remove-document-from-patient
    Body: {
        "document_id": str,       # Required: ID or UUID of the document
        "confidence_score": float # Optional: Confidence score (0.0-1.0)
    }
    """

    PATH = "/remove-document-from-patient"

    def authenticate(self, credentials: Credentials) -> bool:
        """Allow unauthenticated access for testing."""
        log.info("RemoveDocumentFromPatientAPI.authenticate() called")
        return True

    def post(self) -> list[Response]:
        """Handle POST request to remove patient from document."""
        log.info("RemoveDocumentFromPatientAPI.post() called")
        log.info(f"Request path: {self.request.path}")

        try:
            params = self._extract_request_params()

            if "error" in params:
                return [JSONResponse({"error": params["error"]}, status_code=400)]

            effect = self._create_effect(params)

            log.info(f"Removing patient from document {params['document_id']}")

            return [
                effect.apply(),
                JSONResponse(
                    {
                        "success": True,
                        "message": f"Patient removed from document {params['document_id']}",
                        "document_id": params["document_id"],
                    }
                ),
            ]
        except Exception as e:
            log.error(f"Error processing request: {e}", exc_info=True)
            return [JSONResponse({"error": str(e)}, status_code=500)]

    def _extract_request_params(self) -> dict:
        """Extract and validate parameters from request body.

        Returns:
            dict: Dictionary containing:
                - document_id: str (ID or UUID)
                - confidence_score: float | None
                - error: str (only if validation fails)
        """
        try:
            body = self.request.json()
        except Exception:
            return {"error": "Invalid JSON body"}

        document_id = body.get("document_id")
        confidence_score = body.get("confidence_score")

        if document_id is None:
            return {"error": "document_id is required"}

        # Accept string (UUID) or integer
        if not isinstance(document_id, (str, int)):
            return {"error": "document_id must be a string or integer"}
        document_id = str(document_id)

        if confidence_score is not None:
            if not isinstance(confidence_score, (int, float)):
                return {"error": "confidence_score must be a number"}
            if not (0.0 <= confidence_score <= 1.0):
                return {"error": "confidence_score must be between 0.0 and 1.0"}

        log.info(f"Params - document_id: {document_id}, confidence_score: {confidence_score}")

        return {
            "document_id": document_id,
            "confidence_score": confidence_score,
        }

    def _create_effect(self, params: dict) -> RemoveDocumentFromPatient:
        """Create the RemoveDocumentFromPatient effect with given parameters.

        Args:
            params: Dictionary with document_id and optional confidence_score

        Returns:
            RemoveDocumentFromPatient: The configured effect
        """
        document_id = str(params["document_id"])
        confidence_score = params.get("confidence_score")

        if confidence_score is not None:
            return RemoveDocumentFromPatient(
                document_id=document_id,
                confidence_scores={"removal": confidence_score},
            )

        return RemoveDocumentFromPatient(document_id=document_id)
