from typing import Any

from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect


class RemoveDocumentFromPatient(_BaseEffect):
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

    document_id: str | int | None = None
    patient_id: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The effect's values to be sent in the payload."""
        result: dict[str, Any] = {
            "document_id": str(self.document_id).strip() if self.document_id is not None else None,
        }
        if self.patient_id is not None:
            result["patient_id"] = self.patient_id.strip() if self.patient_id else None
        return result

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """Validate the effect fields and return any error details."""
        errors = super()._get_error_details(method)

        # Validate document_id is non-empty if provided as string
        if isinstance(self.document_id, str) and not self.document_id.strip():
            errors.append(
                self._create_error_detail(
                    "value_error",
                    "document_id must be a non-empty string",
                    self.document_id,
                )
            )

        # Validate patient_id is non-empty if provided
        if self.patient_id is not None and not self.patient_id.strip():
            errors.append(
                self._create_error_detail(
                    "value_error",
                    "patient_id must be a non-empty string",
                    self.patient_id,
                )
            )

        return errors


__exports__ = ("RemoveDocumentFromPatient",)
