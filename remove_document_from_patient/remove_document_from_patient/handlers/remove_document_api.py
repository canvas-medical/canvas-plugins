"""
Remove Document From Patient API Handler.

This module provides a Simple API endpoint for removing/unlinking a patient
from a document in the Data Integration queue.

Example usage:
    curl -X POST /plugin-io/api/remove_document_from_patient/remove-document-from-patient \
         -H "Content-Type: application/json" \
         -d '{"document_id": "50272cbb-3051-4bcd-b627-8d5b6c3e1cde", "patient_id": "1c8a7ea5ba6a433daf32524085092c46"}'

    # With optional confidence score:
    curl -X POST /plugin-io/api/remove_document_from_patient/remove-document-from-patient \
         -H "Content-Type: application/json" \
         -d '{"document_id": "50272cbb-3051-4bcd-b627-8d5b6c3e1cde", "patient_id": "1c8a7ea5ba6a433daf32524085092c46", "confidence_score": 0.95}'
"""

from canvas_sdk.effects.data_integration import RemoveDocumentFromPatientEffect
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
        "patient_id": str,        # Optional: ID or UUID of the patient (for logging/audit)
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

            log.info(
                f"Removing patient {params['patient_id']} from document {params['document_id']}"
            )

            return [
                effect.apply(),
                JSONResponse(
                    {
                        "success": True,
                        "message": f"Patient {params['patient_id']} removed from document {params['document_id']}",
                        "document_id": params["document_id"],
                        "patient_id": params["patient_id"],
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
                - patient_id: str | None (ID or UUID)
                - confidence_score: float | None
                - error: str (only if validation fails)
        """
        try:
            body = self.request.json()
        except Exception:
            return {"error": "Invalid JSON body"}

        document_id = body.get("document_id")
        patient_id = body.get("patient_id")
        confidence_score = body.get("confidence_score")

        if document_id is None:
            return {"error": "document_id is required"}

        # Accept string (UUID) or integer
        if not isinstance(document_id, (str, int)):
            return {"error": "document_id must be a string or integer"}
        document_id = str(document_id)

        # patient_id is optional, but if provided must be string or int
        if patient_id is not None:
            if not isinstance(patient_id, (str, int)):
                return {"error": "patient_id must be a string or integer"}
            patient_id = str(patient_id)

        if confidence_score is not None:
            if not isinstance(confidence_score, (int, float)):
                return {"error": "confidence_score must be a number"}
            if not (0.0 <= confidence_score <= 1.0):
                return {"error": "confidence_score must be between 0.0 and 1.0"}

        log.info(
            f"Params - document_id: {document_id}, patient_id: {patient_id}, "
            f"confidence_score: {confidence_score}"
        )

        return {
            "document_id": document_id,
            "patient_id": patient_id,
            "confidence_score": confidence_score,
        }

    def _create_effect(self, params: dict) -> RemoveDocumentFromPatientEffect:
        """Create the RemoveDocumentFromPatientEffect with given parameters.

        Args:
            params: Dictionary with document_id, patient_id, and optional confidence_score

        Returns:
            RemoveDocumentFromPatientEffect: The configured effect
        """
        document_id = str(params["document_id"])
        confidence_score = params.get("confidence_score")

        if confidence_score is not None:
            return RemoveDocumentFromPatientEffect(
                document_id=document_id,
                confidence_scores={document_id: confidence_score},
            )

        return RemoveDocumentFromPatientEffect(document_id=document_id)
