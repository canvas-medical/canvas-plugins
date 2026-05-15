from typing import Any

from canvas_sdk.effects.base import EffectType
from canvas_sdk.effects.data_integration.base import _PrefillingDocumentEffect
from canvas_sdk.effects.data_integration.types import DocumentType


class CategorizeDocument(_PrefillingDocumentEffect):
    """Categorizes a document in the Data Integration queue into a specific document type.

    When processed, this effect will:
    - Validate the IntegrationTask exists
    - Look up the DocumentType by key (falls back to name if key not found)
    - Create or update an IntegrationTaskReview with `template_name` and `document_key`
    """

    class Meta:
        effect_type = EffectType.CATEGORIZE_DOCUMENT

    document_type: DocumentType

    @property
    def values(self) -> dict[str, Any]:
        """The effect's values to be sent in the payload."""
        return {
            "document_id": str(self.document_id),
            "document_type": self.document_type,
            "annotations": self.annotations,
            "source_protocol": self.source_protocol,
        }


__exports__ = ("CategorizeDocument",)
