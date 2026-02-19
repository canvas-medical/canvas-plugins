from typing import Any

from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType
from canvas_sdk.effects.data_integration.base import _BaseDocumentEffect


class LinkDocumentToPatient(_BaseDocumentEffect):
    """
    An Effect that links a document in the Data Integration queue to a patient
    using the patient's key.

    The plugin is responsible for finding/matching the patient and providing their key.
    This simplifies the interpreter and eliminates edge cases with 0 or multiple patient matches.

    When processed by the home-app interpreter, this effect will:
    - Look up the patient by key
    - Link the document to that patient
    - Create an IntegrationTaskPrefill record with patient data and annotations

    Attributes:
        document_id: The ID of the IntegrationTask document to link (required, non-empty).
            Accepts str or int; always serialized as string in the payload.
        patient_key: The patient's key (required, non-empty string).
        annotations: Optional list of AnnotationItem dicts with text and color.
            Example: [AnnotationItem(text="AI 95%", color="#00AA00"), AnnotationItem(text="DOB matched", color="#2196F3")]
        source_protocol: Optional protocol/plugin identifier (e.g., "llm_v1").
    """

    class Meta:
        effect_type = EffectType.LINK_DOCUMENT_TO_PATIENT
        apply_required_fields = (
            "document_id",
            "patient_key",
        )

    patient_key: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The effect's values to be sent in the payload."""
        result: dict[str, Any] = {
            "document_id": self._serialize_document_id(),
            "patient_key": str(self.patient_key).strip() if self.patient_key else None,
        }
        if self.annotations is not None:
            result["annotations"] = self.annotations
        if self.source_protocol is not None:
            result["source_protocol"] = self._serialize_source_protocol()
        return result

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """Validate the effect fields and return any error details."""
        errors = super()._get_error_details(method)
        errors.extend(self._validate_non_empty_string("patient_key", self.patient_key))
        return errors


__exports__ = ("LinkDocumentToPatient",)
