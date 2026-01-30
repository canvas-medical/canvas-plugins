from typing import Any

from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType
from canvas_sdk.effects.data_integration.base import _BaseDocumentEffect


class RemoveDocumentFromPatient(_BaseDocumentEffect):
    """
    An Effect that removes/unlinks a document from a patient in the Data Integration queue.

    When processed by the home-app interpreter, this effect will:
    - Find the document by document_id (IntegrationTask ID)
    - Remove the patient association from the document
    - Optionally filter by patient_id if multiple patients could be linked

    Attributes:
        document_id: The ID of the IntegrationTask document to unlink (required, non-empty).
            Accepts str or int; always serialized as string in the payload.
        patient_id: Optional patient ID to specify which patient link to remove.
            If not provided, removes the current patient association.
    """

    class Meta:
        effect_type = EffectType.REMOVE_DOCUMENT_FROM_PATIENT
        apply_required_fields = ("document_id",)

    patient_id: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The effect's values to be sent in the payload."""
        result: dict[str, Any] = {
            "document_id": self._serialize_document_id(),
        }
        if self.patient_id is not None:
            result["patient_id"] = self.patient_id.strip() if self.patient_id else None
        return result

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """Validate the effect fields and return any error details."""
        errors = super()._get_error_details(method)
        errors.extend(self._validate_non_empty_string("patient_id", self.patient_id))
        return errors


__exports__ = ("RemoveDocumentFromPatient",)
