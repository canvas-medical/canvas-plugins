from typing import Any

from canvas_sdk.effects.base import EffectType
from canvas_sdk.effects.data_integration.base import _BaseDocumentEffect
from canvas_sdk.effects.data_integration.types import NonEmptyStr


class RemoveDocumentFromPatient(_BaseDocumentEffect):
    """Removes/unlinks a document from a patient in the Data Integration queue.

    When processed, this effect will:
    - Find the IntegrationTask by `document_id`
    - Remove the patient association from the document
    - If `patient_id` is provided, only remove the link to that specific patient
    """

    class Meta:
        effect_type = EffectType.REMOVE_DOCUMENT_FROM_PATIENT

    patient_id: NonEmptyStr | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The effect's values to be sent in the payload."""
        return {
            "document_id": str(self.document_id),
            "patient_id": self.patient_id,
        }


__exports__ = ("RemoveDocumentFromPatient",)
