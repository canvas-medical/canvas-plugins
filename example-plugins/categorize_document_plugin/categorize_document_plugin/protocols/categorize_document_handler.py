from canvas_sdk.effects.categorize_document import (
    AnnotationItem,
    CategorizeDocument,
    DocumentType,
)
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from logger import log


class CategorizeDocumentHandler(BaseHandler):
    """
    Handler that categorizes documents when they are received.

    This is an example plugin that demonstrates how to use the CATEGORIZE_DOCUMENT effect.
    """

    RESPONDS_TO = EventType.Name(EventType.DOCUMENT_RECEIVED)

    def compute(self) -> list:
        """Compute effects to categorize document."""
        document_id = self.event.context.get("document", {}).get("id")

        if not document_id:
            log.warning("Document ID not found in event context")
            return []

        available_document_types = self.event.context.get("available_document_types", [])

        # Prefer "Lab Report" document type, fall back to first available
        lab_report_type = next(
            (dt for dt in available_document_types if dt.get("name") == "Lab Report"),
            None,
        )

        if not lab_report_type:
            log.warning(
                f"Lab Report document type not found. "
                f"Available types: {[dt.get('name') for dt in available_document_types]}"
            )
            return []

        document_type: DocumentType = {
            "key": lab_report_type["key"],
            "name": lab_report_type["name"],
            "report_type": lab_report_type["report_type"],
            "template_type": lab_report_type.get("template_type"),
        }

        annotations: list[AnnotationItem] = [
            AnnotationItem(text="AI 95%", color="#00AA00"),
            AnnotationItem(text="Auto-detected", color="#2196F3"),
        ]

        effect = CategorizeDocument(
            document_id=document_id,
            document_type=document_type,
            annotations=annotations,
            source_protocol="categorize_document_plugin",
        )

        log.info(f"Categorized document {document_id} as {document_type['name']}")
        return [effect.apply()]
