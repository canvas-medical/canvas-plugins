from typing import Annotated, Any

from pydantic import Field
from pydantic_core import InitErrorDetails
from typing_extensions import TypedDict

from canvas_sdk.effects.base import EffectType
from canvas_sdk.effects.data_integration.base import _BaseDocumentEffect


class JunkDocumentConfidenceScores(TypedDict, total=False):
    """
    Confidence scores for the junk document decision.

    All fields are optional. Values must be floats between 0.0 and 1.0,
    representing the confidence level of the junk classification.

    Attributes:
        junk: Confidence score for the decision to junk a document (0.0-1.0).
            Higher values indicate greater confidence that the document is junk/spam.
    """

    junk: Annotated[float, Field(ge=0.0, le=1.0)]


class JunkDocument(_BaseDocumentEffect):
    """
    An Effect that marks a document in the Data Integration queue as junk (spam).

    When processed by the home-app interpreter, this effect will:
    - Validate the document exists
    - Mark the document as junk (spam) by setting IntegrationTask.status to "JUN" (JUNK constant)

    Attributes:
        document_id: The ID of the IntegrationTask document to mark as junk (required, non-empty).
            Accepts str or int; always serialized as string in the payload.
        confidence_scores: Optional confidence scores for the junk classification.
            See JunkDocumentConfidenceScores TypedDict for valid keys and value constraints.
    """

    class Meta:
        effect_type = EffectType.JUNK_DOCUMENT
        apply_required_fields = ("document_id",)

    document_id: str | int | None = None
    confidence_scores: JunkDocumentConfidenceScores | None = None

    @classmethod
    def _get_confidence_score_keys(cls) -> frozenset[str]:
        """Return valid keys for confidence_scores validation."""
        return frozenset(JunkDocumentConfidenceScores.__annotations__.keys())

    @property
    def values(self) -> dict[str, Any]:
        """The effect's values to be sent in the payload."""
        result: dict[str, Any] = {
            "document_id": str(self.document_id).strip() if self.document_id is not None else None,
        }
        if self.confidence_scores is not None:
            result["confidence_scores"] = self.confidence_scores
        return result

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """Validate the effect fields and return any error details."""
        errors = super()._get_error_details(method)
        self._validate_document_id_not_empty(errors)
        return errors


__exports__ = ("JunkDocumentConfidenceScores", "JunkDocument")
