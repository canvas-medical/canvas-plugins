from typing import Annotated, Any

from pydantic import Field, model_validator
from pydantic_core import InitErrorDetails
from typing_extensions import TypedDict

from canvas_sdk.effects.base import EffectType, _BaseEffect


class ConfidenceScores(TypedDict, total=False):
    """
    Confidence scores for document fields extracted from a document.

    All fields are optional. Values must be floats between 0.0 and 1.0,
    representing the confidence level of each extracted field (e.g., from OCR).

    Attributes:
        document_id: Confidence score for the extracted document ID (0.0-1.0)
    """

    document_id: Annotated[float, Field(ge=0.0, le=1.0)]


CONFIDENCE_SCORE_KEYS = frozenset(ConfidenceScores.__annotations__.keys())


class JunkDocument(_BaseEffect):
    """
    An Effect that marks a document in the Data Integration queue as junk (spam).

    When processed by the home-app interpreter, this effect will:
    - Validate the document exists
    - Mark the document as junk (spam) by setting IntegrationTask.status to "JUN" (JUNK constant)

    Attributes:
        document_id: The ID of the IntegrationTask document to mark as junk (required, non-empty).
            Accepts str or int; always serialized as string in the payload.
        confidence_scores: Optional confidence scores for document fields.
            See ConfidenceScores TypedDict for valid keys and value constraints.
    """

    class Meta:
        effect_type = EffectType.JUNK_DOCUMENT
        apply_required_fields = ("document_id",)

    document_id: str | int | None = None
    confidence_scores: ConfidenceScores | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_confidence_scores_keys(cls, data: Any) -> Any:
        """Validate confidence_scores keys before Pydantic processes the TypedDict.

        TypedDict in Pydantic silently drops unknown keys, so we validate
        them here to provide a clear error message to users.
        """
        if isinstance(data, dict) and "confidence_scores" in data:
            scores = data.get("confidence_scores")
            if isinstance(scores, dict):
                invalid_keys = set(scores.keys()) - CONFIDENCE_SCORE_KEYS
                if invalid_keys:
                    raise ValueError(
                        f"confidence_scores contains invalid keys: {sorted(invalid_keys)}. "
                        f"Valid keys are: {sorted(CONFIDENCE_SCORE_KEYS)}"
                    )
        return data

    @property
    def values(self) -> dict[str, Any]:
        """The effect's values to be sent in the payload."""
        result: dict[str, Any] = {
            "document_id": str(self.document_id) if self.document_id is not None else None,
        }
        if self.confidence_scores is not None:
            result["confidence_scores"] = self.confidence_scores
        return result

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """Validate the effect fields and return any error details.

        Note: confidence_scores validation (invalid keys, range constraints) is
        handled by Pydantic at construction time via model_validator and TypedDict
        with Annotated field constraints.
        """
        errors = super()._get_error_details(method)
        return errors


__exports__ = ("ConfidenceScores", "JunkDocument")
