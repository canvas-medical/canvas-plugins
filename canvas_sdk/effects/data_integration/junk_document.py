from typing import Any

from canvas_sdk.effects.base import EffectType
from canvas_sdk.effects.data_integration.base import _BaseDocumentEffect


class JunkDocument(_BaseDocumentEffect):
    """
    An Effect that marks a document in the Data Integration queue as junk (spam).

    When processed by the home-app interpreter, this effect will:
    - Validate the document exists
    - Mark the document as junk (spam) by setting IntegrationTask.status to "JUN" (JUNK constant)

    Attributes:
        document_id: The ID of the IntegrationTask document to mark as junk (required, non-empty).
            Accepts str or int; always serialized as string in the payload.
    """

    class Meta:
        effect_type = EffectType.JUNK_DOCUMENT
        apply_required_fields = ("document_id",)

    @property
    def values(self) -> dict[str, Any]:
        """The effect's values to be sent in the payload."""
        return {
            "document_id": self._serialize_document_id(),
        }


__exports__ = ("JunkDocument",)
