"""
Example handler demonstrating the LINK_DOCUMENT_TO_PATIENT effect.

This handler responds to DOCUMENT_RECEIVED events and demonstrates how to
use the LinkDocumentToPatient effect to link documents to patients using
the patient's key (UUID).

In a real implementation, this would integrate with an LLM or OCR system
to extract patient information from the document content and find the
matching patient. This example uses sample data for demonstration purposes.
"""

from canvas_sdk.effects import Effect
from canvas_sdk.effects.data_integration import LinkDocumentToPatient
from canvas_sdk.events import EventType
from canvas_sdk.handlers.base import BaseHandler
from logger import log


class LinkDocumentHandler(BaseHandler):
    """
    Handler that links incoming documents to patients using patient_key.

    This handler demonstrates the LINK_DOCUMENT_TO_PATIENT effect by:
    1. Responding to DOCUMENT_RECEIVED events
    2. Finding the patient using extracted demographics (simulated in this example)
    3. Emitting a LinkDocumentToPatient effect with the patient's key

    The plugin is responsible for finding/matching the patient and providing their key.
    This simplifies the interpreter and eliminates edge cases with 0 or multiple patient matches.
    """

    RESPONDS_TO: list[str] = [
        EventType.Name(EventType.DOCUMENT_RECEIVED),
    ]

    def compute(self) -> list[Effect]:
        """
        Process incoming documents and link them to patients.

        This method is called when a new document is received in the
        Data Integration queue. It finds the matching patient and
        returns a LinkDocumentToPatient effect to link the document.

        Returns:
            A list containing the LinkDocumentToPatient effect, or an empty
            list if the document should not be auto-linked.
        """
        # Get the document ID from the event target
        document_id = self.event.target.id

        if not document_id:
            log.error("No document_id found in event target")
            return []

        # In a real implementation, you would:
        # 1. Extract patient demographics from the document (via LLM/OCR)
        # 2. Search for the patient in Canvas using the FHIR API
        # 3. Return the patient's key if found

        # For this example, we simulate finding a patient
        patient_data = self._find_patient_from_document(document_id)

        if not patient_data:
            log.info(
                "Could not find patient for document: document_id=%s",
                document_id,
            )
            return []

        # Create the LinkDocumentToPatient effect with the patient's key
        effect = LinkDocumentToPatient(
            document_id=document_id,
            patient_key=patient_data["patient_key"],
            annotations=patient_data.get("annotations"),
            source_protocol=patient_data.get("source_protocol"),
        )

        log.info(
            "Linking document to patient: document_id=%s, patient_key=%s, annotations=%s",
            document_id,
            patient_data["patient_key"],
            patient_data.get("annotations"),
        )

        return [effect.apply()]

    def _find_patient_from_document(self, document_id: str) -> dict | None:
        """
        Find a patient based on document content.

        In a real implementation, this method would:
        1. Fetch the document content from storage
        2. Use an LLM to extract patient demographics
        3. Search for the patient in Canvas using the FHIR Patient API
        4. Return the patient's key and annotations for display

        Args:
            document_id: The ID of the document to process

        Returns:
            A dictionary containing the patient_key and annotations,
            or None if no matching patient was found.
        """
        # This is a placeholder implementation for demonstration purposes.
        # Example return value - replace with actual patient lookup
        return {
            "patient_key": "1d46a570bc31443d8448ef43b0600609",
            "annotations": [
                {"text": "AI 95%", "color": "#00AA00"},
                {"text": "DOB matched"},
            ],
            "source_protocol": "llm_v1",
        }


# Alternative handler that demonstrates more complex logic
class ConditionalLinkDocumentHandler(BaseHandler):
    """
    Handler that conditionally links documents based on confidence thresholds.

    This handler demonstrates how to:
    1. Set minimum confidence thresholds for auto-linking
    2. Only emit the effect when confidence is high enough
    3. Log low-confidence extractions for manual review
    """

    RESPONDS_TO: list[str] = [
        EventType.Name(EventType.DOCUMENT_RECEIVED),
    ]

    # Minimum confidence score required for auto-linking
    MIN_CONFIDENCE_THRESHOLD = 0.85

    def compute(self) -> list[Effect]:
        """Process documents and conditionally link based on confidence."""
        document_id = self.event.target.id

        if not document_id:
            return []

        # Simulate extraction and patient lookup with confidence
        result = self._extract_and_find_patient(document_id)

        if not result:
            return []

        # Check if confidence is high enough for auto-linking
        if result["confidence"] < self.MIN_CONFIDENCE_THRESHOLD:
            log.info(
                "Patient match confidence too low for auto-linking: document_id=%s, confidence=%s, threshold=%s",
                document_id,
                result["confidence"],
                self.MIN_CONFIDENCE_THRESHOLD,
            )
            # In production, you might create a task for manual review here
            return []

        # Confidence is high enough - create the effect
        # Annotations are dicts with "text" (required) and "color" (optional)
        effect = LinkDocumentToPatient(
            document_id=document_id,
            patient_key=result["patient_key"],
            annotations=[
                {"text": f"AI {int(result['confidence'] * 100)}%", "color": "#00AA00"},
                {"text": "Auto-linked"},
            ],
            source_protocol="llm_v1",
        )

        return [effect.apply()]

    def _extract_and_find_patient(self, document_id: str) -> dict | None:
        """
        Extract demographics and find matching patient.

        This is a placeholder. In production, you would:
        1. Call your LLM API to extract demographics from document
        2. Search for patients using Canvas FHIR API
        3. Return the best match with confidence score
        """
        # Placeholder - replace with actual implementation
        return {
            "patient_key": "1d46a570bc31443d8448ef43b0600609",
            "confidence": 0.92,
        }
