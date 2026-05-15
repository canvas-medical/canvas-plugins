from typing import Any

from canvas_sdk.effects.base import EffectType
from canvas_sdk.effects.data_integration.base import _PrefillingDocumentEffect
from canvas_sdk.effects.data_integration.types import NonEmptyStr


class LinkDocumentToPatient(_PrefillingDocumentEffect):
    """Links a document in the Data Integration queue to a patient by the patient's key.

    The plugin is responsible for matching the patient and providing their key — this
    avoids edge cases with 0 or multiple patient matches in the interpreter.

    When processed, this effect will:
    - Look up the patient by key
    - Link the document to that patient
    - Create an IntegrationTaskPrefill record with patient data and annotations
    """

    class Meta:
        effect_type = EffectType.LINK_DOCUMENT_TO_PATIENT

    patient_key: NonEmptyStr

    @property
    def values(self) -> dict[str, Any]:
        """The effect's values to be sent in the payload."""
        return {
            "document_id": str(self.document_id),
            "patient_key": self.patient_key,
            "annotations": self.annotations,
            "source_protocol": self.source_protocol,
        }


__exports__ = ("LinkDocumentToPatient",)
