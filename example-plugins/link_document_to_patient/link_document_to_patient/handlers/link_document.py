"""
Example handler demonstrating the LINK_DOCUMENT_TO_PATIENT effect.

This handler responds to DOCUMENT_RECEIVED events and demonstrates how to
use the LinkDocumentToPatient effect to link documents to patients based
on extracted patient demographics.

In a real implementation, this would integrate with an LLM or OCR system
to extract patient information from the document content. This example
uses sample data for demonstration purposes.
"""

from datetime import date

from canvas_sdk.effects import Effect
from canvas_sdk.effects.data_integration import LinkDocumentToPatient
from canvas_sdk.events import EventType
from canvas_sdk.handlers.base import BaseHandler
from logger import log


class LinkDocumentHandler(BaseHandler):
    """
    Handler that links incoming documents to patients based on demographics.

    This handler demonstrates the LINK_DOCUMENT_TO_PATIENT effect by:
    1. Responding to DOCUMENT_RECEIVED events
    2. Extracting patient demographics from the document (simulated in this example)
    3. Emitting a LinkDocumentToPatient effect to link the document to the matching patient

    In a production implementation, you would:
    - Use an LLM or OCR to extract patient demographics from the document content
    - Handle the confidence scores returned by the extraction system
    - Implement retry logic or manual review workflows for ambiguous matches
    """

    RESPONDS_TO: list[str] = [
        EventType.Name(EventType.DOCUMENT_RECEIVED),
    ]

    def compute(self) -> list[Effect]:
        """
        Process incoming documents and link them to patients.

        This method is called when a new document is received in the
        Data Integration queue. It extracts patient demographics and
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
        # 1. Fetch the document content
        # 2. Use an LLM or OCR to extract patient demographics
        # 3. Return the extracted data with confidence scores

        # For this example, we simulate extracted patient demographics
        extracted_data = self._extract_patient_demographics(document_id)

        if not extracted_data:
            log.info(
                "Could not extract patient demographics from document: document_id=%s",
                document_id,
            )
            return []

        # Create the LinkDocumentToPatient effect
        effect = LinkDocumentToPatient(
            first_name=extracted_data["first_name"],
            last_name=extracted_data["last_name"],
            date_of_birth=extracted_data["date_of_birth"],
            document_id=document_id,
            confidence_scores=extracted_data.get("confidence_scores"),
        )

        log.info(
            "Attempting to link document to patient: document_id=%s, first_name=%s, last_name=%s, date_of_birth=%s",
            document_id,
            extracted_data["first_name"],
            extracted_data["last_name"],
            str(extracted_data["date_of_birth"]),
        )

        return [effect.apply()]

    def _extract_patient_demographics(self, document_id: str) -> dict | None:
        """
        Extract patient demographics from a document.

        In a real implementation, this method would:
        1. Fetch the document content from storage
        2. Process the document using OCR if it's an image/PDF
        3. Use an LLM to extract patient demographics
        4. Return structured data with confidence scores

        Args:
            document_id: The ID of the document to process

        Returns:
            A dictionary containing extracted patient demographics and
            confidence scores, or None if extraction failed.
        """
        # This is a placeholder implementation for demonstration purposes.
        # In production, you would integrate with an actual extraction service.

        # Example of what extracted data might look like:
        # (In practice, this would come from an LLM or OCR system)
        return {
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": date(1990, 5, 15),
            "confidence_scores": {
                "first_name": 0.95,
                "last_name": 0.92,
                "date_of_birth": 0.88,
            },
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

        # Simulate extraction with confidence scores
        extracted_data = self._extract_with_llm(document_id)

        if not extracted_data:
            return []

        # Check if confidence is high enough for auto-linking
        confidence_scores = extracted_data.get("confidence_scores", {})
        avg_confidence = self._calculate_average_confidence(confidence_scores)

        if avg_confidence < self.MIN_CONFIDENCE_THRESHOLD:
            log.info(
                "Document extraction confidence too low for auto-linking: document_id=%s, average_confidence=%s, threshold=%s",
                document_id,
                avg_confidence,
                self.MIN_CONFIDENCE_THRESHOLD,
            )
            # In production, you might create a task for manual review here
            return []

        # Confidence is high enough - create the effect
        effect = LinkDocumentToPatient(
            first_name=extracted_data["first_name"],
            last_name=extracted_data["last_name"],
            date_of_birth=extracted_data["date_of_birth"],
            document_id=document_id,
            confidence_scores=confidence_scores,
        )

        return [effect.apply()]

    def _extract_with_llm(self, document_id: str) -> dict | None:
        """
        Extract patient demographics using an LLM.

        This is a placeholder. In production, you would:
        1. Call your LLM API with the document content
        2. Parse the structured response
        3. Return the extracted demographics with confidence scores
        """
        # Placeholder - replace with actual LLM integration
        return {
            "first_name": "Jane",
            "last_name": "Smith",
            "date_of_birth": date(1985, 3, 20),
            "confidence_scores": {
                "first_name": 0.90,
                "last_name": 0.88,
                "date_of_birth": 0.92,
            },
        }

    def _calculate_average_confidence(self, confidence_scores: dict) -> float:
        """Calculate the average confidence score."""
        if not confidence_scores:
            return 0.0

        values = [v for v in confidence_scores.values() if isinstance(v, (int, float))]
        return sum(values) / len(values) if values else 0.0
