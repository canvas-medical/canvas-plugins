import json

from canvas_sdk.effects.categorize_document import (
    AnnotationItem,
    CategorizeDocument,
    ConfidenceScores,
    DocumentType,
    DocumentTypeConfidenceScores,
)
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from logger import log

# Log prefix for easy filtering in logs
LOG_PREFIX = "PLUGIN_DEBUG:"


class CategorizeDocumentHandler(BaseHandler):
    """
    Handler that categorizes documents when they are received.

    This is an example plugin that demonstrates how to use the CATEGORIZE_DOCUMENT effect.
    """

    RESPONDS_TO = EventType.Name(EventType.DOCUMENT_RECEIVED)

    def compute(self) -> list:
        """Compute effects to categorize document."""
        log.info(f"{LOG_PREFIX} Handler compute() called")
        log.info(f"{LOG_PREFIX} Event context keys: {list(self.event.context.keys())}")

        document_id = self.event.context.get("document", {}).get("id")
        log.info(f"{LOG_PREFIX} Extracted document_id: {document_id}")

        if not document_id:
            log.warning(f"{LOG_PREFIX} Document ID not found in event context")
            log.info(
                f"{LOG_PREFIX} Event context document: {self.event.context.get('document', {})}"
            )
            return []

        available_document_types = self.event.context.get("available_document_types", [])
        log.info(f"{LOG_PREFIX} Available document types count: {len(available_document_types)}")
        if available_document_types:
            log.info(
                f"{LOG_PREFIX} Sample document type structure: {json.dumps(available_document_types[0] if available_document_types else {}, indent=2)}"
            )

        log.info(f"{LOG_PREFIX} Searching for 'Lab Report' document type")
        lab_report_type = next(
            (dt for dt in available_document_types if dt.get("name") == "Lab Report"),
            None,
        )

        if not lab_report_type:
            log.warning(
                f"{LOG_PREFIX} Lab Report document type not found in available_document_types"
            )
            log.info(
                f"{LOG_PREFIX} Available document type names: {[dt.get('name') for dt in available_document_types]}"
            )
            return []

        log.info(
            f"{LOG_PREFIX} Found Lab Report document type: {json.dumps(lab_report_type, indent=2)}"
        )

        document_type: DocumentType = {
            "key": lab_report_type["key"],
            "name": lab_report_type["name"],
            "report_type": lab_report_type["report_type"],
            "template_type": lab_report_type.get("template_type"),
        }
        log.info(f"{LOG_PREFIX} Constructed document_type: {json.dumps(document_type, indent=2)}")

        document_type_confidence: DocumentTypeConfidenceScores = {
            "key": 0.90,
            "name": 0.95,
            "report_type": 0.85,
            "template_type": 0.90,
        }
        confidence_scores: ConfidenceScores = {
            "document_id": 0.90,
            "document_type": document_type_confidence,
        }
        log.info(f"{LOG_PREFIX} Confidence scores: {json.dumps(confidence_scores, indent=2)}")

        log.info(f"{LOG_PREFIX} Categorizing document {document_id} as {document_type['name']}")

        annotations: list[AnnotationItem] = [
            {"text": "AI 95%", "color": "#00AA00"},
            {"text": "Auto-detected", "color": "#2196F3"},
        ]
        log.info(f"{LOG_PREFIX} Annotations: {json.dumps(annotations, indent=2)}")

        effect = CategorizeDocument(
            document_id=document_id,
            document_type=document_type,
            confidence_scores=confidence_scores,
            annotations=annotations,
            source_protocol="categorize_document_plugin_v1",
        )
        log.info(f"{LOG_PREFIX} Effect created successfully")

        log.info(f"{LOG_PREFIX} Applying effect")
        applied_effect = effect.apply()
        log.info(f"{LOG_PREFIX} Effect applied successfully")

        payload_data = json.loads(applied_effect.payload)
        log.info(
            f"{LOG_PREFIX} CATEGORIZE_DOCUMENT payload (formatted): {json.dumps(payload_data, indent=2)}"
        )
        log.info(f"{LOG_PREFIX} Effect payload (raw): {applied_effect.payload}")
        log.info(f"{LOG_PREFIX} Returning {len([applied_effect])} effect(s)")

        return [applied_effect]
