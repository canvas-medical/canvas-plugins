"""Effect for assigning a document reviewer."""

from enum import StrEnum
from typing import Annotated, Any

from pydantic import Field
from typing_extensions import TypedDict

from canvas_sdk.effects.base import EffectType
from canvas_sdk.effects.data_integration.base import _BaseDocumentEffect


class Priority(StrEnum):
    """Priority levels for document review.

    Maps to Boolean in database: HIGH=True, NORMAL=False.

    Attributes:
        NORMAL: Standard priority (default) - maps to False in database
        HIGH: Elevated priority for time-sensitive documents - maps to True in database
    """

    NORMAL = "normal"
    HIGH = "high"


class ReviewMode(StrEnum):
    """Review mode for document review.

    Values are the database short codes used by the home-app interpreter.

    Attributes:
        REVIEW_REQUIRED: Document requires active review and action (default)
        ALREADY_REVIEWED: Document was already reviewed offline
        REVIEW_NOT_REQUIRED: Document does not require review
    """

    REVIEW_REQUIRED = "RR"
    ALREADY_REVIEWED = "AR"
    REVIEW_NOT_REQUIRED = "RN"


class AssignDocumentReviewerConfidenceScores(TypedDict, total=False):
    """Confidence scores for document reviewer assignment.

    Used for monitoring and debugging purposes only, not used in assignment logic.
    All fields are optional. Values must be floats between 0.0 and 1.0,
    representing the confidence level of the document identification.

    Attributes:
        document_id: Confidence score for the document identification (0.0-1.0)
    """

    document_id: Annotated[float, Field(ge=0.0, le=1.0)]


class AssignDocumentReviewer(_BaseDocumentEffect):
    """
    An Effect that assigns a staff member or team as reviewer to a document
    in the Data Integration queue.

    When processed by the home-app interpreter, this effect will:
    - Validate the document (IntegrationTask) exists
    - Validate the Staff exists if reviewer_id is provided
    - Validate the Team exists if team_id is provided
    - Assign the reviewer and/or team to the document with the specified priority and review_mode
    - If both reviewer_id and team_id are provided, both will be assigned

    This effect is typically emitted by LLM-based document processing plugins
    and supports both initial reviewer assignment and reassignment.

    Attributes:
        document_id: The ID of the IntegrationTask document to assign a reviewer to (required).
            Accepts str or int; always serialized as string in the payload.
            Leading/trailing whitespace is stripped during serialization.
        reviewer_id: Optional Staff key of the reviewer to assign.
            Leading/trailing whitespace is stripped during serialization.
        team_id: Optional Team UUID to assign.
            Leading/trailing whitespace is stripped during serialization.
        priority: Priority level for the review (normal, high). Defaults to normal.
        review_mode: Review mode (review_required, already_reviewed, review_not_required).
            Defaults to review_required.
        confidence_scores: Optional confidence scores for document identification.
            See AssignDocumentReviewerConfidenceScores TypedDict for valid keys and value constraints.
            Used for monitoring/debugging only, not used in assignment logic.
    """

    class Meta:
        effect_type = EffectType.ASSIGN_DOCUMENT_REVIEWER
        apply_required_fields = ("document_id",)

    document_id: str | int | None = None
    reviewer_id: str | int | None = None
    team_id: str | int | None = None
    priority: Priority = Priority.NORMAL
    review_mode: ReviewMode = ReviewMode.REVIEW_REQUIRED
    confidence_scores: AssignDocumentReviewerConfidenceScores | None = None

    @classmethod
    def _get_confidence_score_keys(cls) -> frozenset[str]:
        """Return valid keys for confidence_scores validation."""
        return frozenset(AssignDocumentReviewerConfidenceScores.__annotations__.keys())

    @property
    def values(self) -> dict[str, Any]:
        """The effect's values to be sent in the payload.

        Strings are stripped of leading/trailing whitespace during serialization.
        document_id is always converted to string.
        priority is converted to boolean (HIGH=True, NORMAL=False).
        review_mode uses the enum value directly (database short codes).
        """
        result: dict[str, Any] = {
            "document_id": str(self.document_id).strip() if self.document_id is not None else None,
            "priority": self.priority == Priority.HIGH,
            "review_mode": self.review_mode.value,
        }
        if self.reviewer_id is not None:
            result["reviewer_id"] = str(self.reviewer_id).strip()
        if self.team_id is not None:
            result["team_id"] = str(self.team_id).strip()
        if self.confidence_scores is not None:
            result["confidence_scores"] = self.confidence_scores
        return result

    def _get_error_details(self, method: Any) -> list:
        """Validate the effect fields and return any error details.

        Note: confidence_scores validation (invalid keys, range constraints) is
        handled by Pydantic at construction time via model_validator and TypedDict
        with Annotated field constraints.

        Note: Database existence validation (IntegrationTask, Staff, Team) is
        handled by the home-app interpreter, not the SDK.
        """
        return super()._get_error_details(method)


__exports__ = (
    "AssignDocumentReviewer",
    "AssignDocumentReviewerConfidenceScores",
    "Priority",
    "ReviewMode",
)

