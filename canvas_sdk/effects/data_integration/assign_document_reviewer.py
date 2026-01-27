"""Effect for assigning a document reviewer."""

from enum import StrEnum
from typing import Any

from canvas_sdk.effects.base import EffectType, _BaseEffect
from canvas_sdk.effects.data_integration.types import AnnotationItem


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

    Maps to short codes in database: RR, AR, RN.

    Attributes:
        REVIEW_REQUIRED: Document requires active review and action (default) - maps to "RR"
        ALREADY_REVIEWED: Document was already reviewed offline - maps to "AR"
        REVIEW_NOT_REQUIRED: Document does not require review - maps to "RN"
    """

    REVIEW_REQUIRED = "review_required"
    ALREADY_REVIEWED = "already_reviewed"
    REVIEW_NOT_REQUIRED = "review_not_required"


class AssignDocumentReviewer(_BaseEffect):
    """
    An Effect that assigns a staff member or team as reviewer to a document
    in the Data Integration queue.

    When processed by the home-app interpreter, this effect will:
    - Validate the document (IntegrationTask) exists
    - Validate the Staff exists if reviewer_id is provided
    - Validate the Team exists if team_id is provided
    - Assign the reviewer and/or team to the document with the specified priority and review_mode
    - If both reviewer_id and team_id are provided, both will be assigned
    - Create/update an IntegrationTaskPrefill record with field_type="reviewer"

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
        annotations: Optional list of AnnotationItem objects to display with the reviewer prefill.
            Each annotation has "text" and "color" attributes (e.g., [AnnotationItem(text="Team lead", color="#FF0000")]).
        source_protocol: Optional identifier for the protocol/plugin that generated this effect.
            Used for tracking and debugging (e.g., "llm_v1").
    """

    class Meta:
        effect_type = EffectType.ASSIGN_DOCUMENT_REVIEWER
        apply_required_fields = ("document_id",)

    document_id: str | int | None = None
    reviewer_id: str | int | None = None
    team_id: str | int | None = None
    priority: Priority = Priority.NORMAL
    review_mode: ReviewMode = ReviewMode.REVIEW_REQUIRED
    annotations: list[AnnotationItem] | None = None
    source_protocol: str | None = None

    # Mapping from SDK review_mode values to database short codes
    _REVIEW_MODE_TO_DB: dict[str, str] = {
        "review_required": "RR",
        "already_reviewed": "AR",
        "review_not_required": "RN",
    }

    @property
    def values(self) -> dict[str, Any]:
        """The effect's values to be sent in the payload.

        Strings are stripped of leading/trailing whitespace during serialization.
        document_id is always converted to string.
        priority is converted to boolean (HIGH=True, NORMAL=False).
        review_mode is converted to database short codes (RR, AR, RN).
        annotations is serialized as list of dicts with text and color keys.
        source_protocol is stripped of leading/trailing whitespace.
        """
        result: dict[str, Any] = {
            "document_id": str(self.document_id).strip() if self.document_id is not None else None,
            "priority": self.priority == Priority.HIGH,
            "review_mode": self._REVIEW_MODE_TO_DB[self.review_mode.value],
        }
        if self.reviewer_id is not None:
            result["reviewer_id"] = str(self.reviewer_id).strip()
        if self.team_id is not None:
            result["team_id"] = str(self.team_id).strip()
        if self.annotations is not None:
            result["annotations"] = self.annotations
        if self.source_protocol is not None:
            result["source_protocol"] = self.source_protocol.strip()
        return result

    def _get_error_details(self, method: Any) -> list:
        """Validate the effect fields and return any error details.

        Note: Database existence validation (IntegrationTask, Staff, Team) is
        handled by the home-app interpreter, not the SDK.
        """
        return super()._get_error_details(method)


__exports__ = (
    "AssignDocumentReviewer",
    "Priority",
    "ReviewMode",
)
