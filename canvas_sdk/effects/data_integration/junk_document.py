from typing import Any

from canvas_sdk.effects.base import EffectType
from canvas_sdk.effects.data_integration.base import _BaseDocumentEffect


class JunkDocument(_BaseDocumentEffect):
    """Marks a document in the Data Integration queue as junk (spam).

    When processed, this effect will:
    - Validate the document exists
    - Set IntegrationTask.status to "JUN" (JUNK)
    """

    class Meta:
        effect_type = EffectType.JUNK_DOCUMENT

    @property
    def values(self) -> dict[str, Any]:
        """The effect's values to be sent in the payload."""
        return {
            "document_id": str(self.document_id),
        }


__exports__ = ("JunkDocument",)
