from canvas_sdk.effects.data_integration import JunkDocument
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
        # Get the document ID from the event target
        document_id = self.event.target.id

        if not document_id:
            log.warning("Document ID not found in event target")
            return []

        log.info(f"Marking document {document_id} as junk")

        # Create JunkDocument effect
        effect = JunkDocument(document_id=document_id)

        return [effect.apply()]
