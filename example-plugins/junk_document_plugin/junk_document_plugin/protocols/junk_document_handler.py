from canvas_sdk.effects.junk_document import ConfidenceScores, JunkDocument
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from logger import log


class JunkDocumentHandler(BaseHandler):
    """
    Handler that marks documents as junk when they are received.

    This is an example plugin that demonstrates how to use the JUNK_DOCUMENT effect.
    """

    RESPONDS_TO = EventType.Name(EventType.DOCUMENT_RECEIVED)

    def compute(self) -> list:
        """
        Compute effects to mark document as junk.

        Returns:
            list: List of JunkDocument effects to apply
        """
        document_id = self.event.context.get("document", {}).get("id")

        if not document_id:
            log.warning("Document ID not found in event context")
            return []

        log.info(f"Marking document {document_id} as junk")

        # Create JunkDocument effect with optional confidence score
        effect = JunkDocument(
            document_id=document_id,
            confidence_scores=ConfidenceScores(junk_document=0.90),
        )

        return [effect.apply()]
