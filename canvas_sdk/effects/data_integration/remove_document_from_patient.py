from typing import Annotated, Any

from pydantic import Field
from pydantic_core import InitErrorDetails
from typing_extensions import TypedDict

from canvas_sdk.effects.base import EffectType
from canvas_sdk.effects.data_integration.base import _BaseDocumentEffect


class RemoveDocumentConfidenceScores(TypedDict, total=False):
    """
    Confidence scores for document removal decision.

    All fields are optional. Values must be floats between 0.0 and 1.0,
    representing the confidence level of the removal decision.

    Attributes:
        removal: Confidence score that this document should be removed from the patient (0.0-1.0).
            Higher values indicate greater confidence in the removal decision.
    """

    removal: Annotated[float, Field(ge=0.0, le=1.0)]


# Public constant for backward compatibility with tests
CONFIDENCE_SCORE_KEYS = frozenset(RemoveDocumentConfidenceScores.__annotations__.keys())


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
        confidence_scores: Optional confidence scores for the removal decision.
            See RemoveDocumentConfidenceScores TypedDict for valid keys and value constraints.
    """

    class Meta:
        effect_type = EffectType.REMOVE_DOCUMENT_FROM_PATIENT
        apply_required_fields = ("document_id",)

    document_id: str | int | None = None
    patient_id: str | None = None
    confidence_scores: RemoveDocumentConfidenceScores | None = None

    @classmethod
    def _get_confidence_score_keys(cls) -> frozenset[str]:
        """Return valid keys for confidence_scores validation."""
        return frozenset(RemoveDocumentConfidenceScores.__annotations__.keys())

    @property
    def values(self) -> dict[str, Any]:
        """The effect's values to be sent in the payload."""
        result: dict[str, Any] = {
            "document_id": str(self.document_id).strip() if self.document_id is not None else None,
        }
        if self.patient_id is not None:
            result["patient_id"] = self.patient_id.strip() if self.patient_id else None
        if self.confidence_scores is not None:
            result["confidence_scores"] = self.confidence_scores
        return result

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """Validate the effect fields and return any error details."""
        errors = super()._get_error_details(method)
        self._validate_document_id_not_empty(errors)

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


__exports__ = ("RemoveDocumentConfidenceScores", "RemoveDocumentFromPatient")
