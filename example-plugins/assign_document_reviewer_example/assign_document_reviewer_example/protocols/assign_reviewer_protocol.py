"""Protocol demonstrating the ASSIGN_DOCUMENT_REVIEWER effect."""

from pydantic import ValidationError

from canvas_sdk.effects import Effect
from canvas_sdk.effects.data_integration import (
    Annotation,
    AssignDocumentReviewer,
    Priority,
    ReviewMode,
)
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from canvas_sdk.v1.data import Staff, Team
from logger import log


class AssignDocumentReviewerProtocol(BaseProtocol):
    """
    A protocol that demonstrates the AssignDocumentReviewer effect.

    Triggers on: DOCUMENT_RECEIVED events
    Effects: AssignDocumentReviewer
    """

    RESPONDS_TO = EventType.Name(EventType.DOCUMENT_RECEIVED)

    def compute(self) -> list[Effect]:
        """Assign a reviewer to the received document."""
        document_id = self.event.context.get("document", {}).get("id")

        log.info(f"Processing document {document_id}")

        try:
            staff = Staff.objects.first()
            team = Team.objects.first()

            if not staff:
                log.warning(f"No staff available for document {document_id}")
                return []

            effect = AssignDocumentReviewer(
                document_id=str(document_id),
                reviewer_id=str(staff.id),
                team_id=str(team.id) if team else None,
                priority=Priority.HIGH,
                review_mode=ReviewMode.REVIEW_NOT_REQUIRED,
                annotations=[
                    Annotation(text="Team lead", color="#4CAF50"),
                    Annotation(text="Primary care", color="#2196F3"),
                    Annotation(text="Auto-assigned", color="#FF9800"),
                ],
                source_protocol="assign_document_reviewer_example",
            )

            log.info(f"Assigned reviewer {staff.id} to document {document_id}")
            return [effect.apply()]

        except ValidationError as e:
            log.error(f"Validation error processing document {document_id}: {e}")
            return []
