from enum import StrEnum
from typing import Any
from uuid import UUID

from canvas_sdk.effects.base import EffectType
from canvas_sdk.effects.data_integration.base import _BaseDocumentEffect


class Priority(StrEnum):
    """Priority levels for document review."""

    NORMAL = "normal"
    HIGH = "high"


class ReviewMode(StrEnum):
    """Review mode for document review."""

    REVIEW_REQUIRED = "RR"
    ALREADY_REVIEWED = "AR"
    REVIEW_NOT_REQUIRED = "RN"


class AssignDocumentReviewer(_BaseDocumentEffect):
    """Assigns a staff member or team as reviewer to a document in the Data Integration queue.

    When processed, this effect will:
    - Validate the IntegrationTask exists
    - Validate the Staff exists if `reviewer_id` is provided
    - Validate the Team exists if `team_id` is provided
    - Assign the reviewer and/or team with the given `priority` and `review_mode`
    - Create/update an IntegrationTaskPrefill record with field_type="reviewer"

    Both `reviewer_id` and `team_id` are optional; if both are provided, both are assigned.
    """

    class Meta:
        effect_type = EffectType.ASSIGN_DOCUMENT_REVIEWER

    reviewer_id: str | None = None
    team_id: UUID | str | None = None
    priority: Priority = Priority.NORMAL
    review_mode: ReviewMode = ReviewMode.REVIEW_REQUIRED

    @property
    def values(self) -> dict[str, Any]:
        """The effect's values to be sent in the payload."""
        return {
            "document_id": str(self.document_id),
            "priority": self.priority == Priority.HIGH,
            "review_mode": self.review_mode,
            "reviewer_id": self.reviewer_id,
            "team_id": str(self.team_id) if self.team_id is not None else None,
            "annotations": self.annotations,
            "source_protocol": self.source_protocol,
        }


__exports__ = (
    "AssignDocumentReviewer",
    "Priority",
    "ReviewMode",
)
