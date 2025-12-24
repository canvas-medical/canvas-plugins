"""Protocol demonstrating the ASSIGN_DOCUMENT_REVIEWER effect."""

from pydantic import ValidationError

from canvas_sdk.effects import Effect
from canvas_sdk.effects.assign_document_reviewer import (
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
    A protocol that demonstrates assigning a reviewer to incoming documents.

    This protocol responds to DOCUMENT_RECEIVED events and automatically assigns
    a reviewer to the document based on configurable rules.

    Triggers on: DOCUMENT_RECEIVED events
    Effects: Assigns a staff member or team as document reviewer
    """

    RESPONDS_TO = EventType.Name(EventType.DOCUMENT_RECEIVED)

    def compute(self) -> list[Effect]:
        """
        Assign a reviewer to the received document.

        This method demonstrates emitting the ASSIGN_DOCUMENT_REVIEWER effect
        by fetching the first available Staff and Team from the database.
        """
        # Get the document ID from the event target
        document_id = self.event.context.get("document", {}).get("id")

        log.info(f"Processing document {document_id} for reviewer assignment")

        # Fetch first available staff member
        staff = Staff.objects.first()

        # Fetch first available team (optional)
        team = Team.objects.first()

        log.info(f"Found staff: {staff.id if staff else None}, team: {team.id if team else None}")

        try:
            # Assign the staff member as reviewer, and optionally the team
            effect = AssignDocumentReviewer(
                document_id=str(document_id),
                reviewer_id=str(staff.id),
                team_id=str(team.id) if team else None,
                priority=Priority.HIGH,
                review_mode=ReviewMode.REVIEW_REQUIRED,
                confidence_scores={"document_id": 0.95},
            )

            applied_effect = effect.apply()
            log.info(f"Assigned reviewer {staff.id} to document {document_id}")
            return [applied_effect]

        except ValidationError as e:
            log.error(f"Validation error assigning reviewer to document {document_id}: {e}")
            return []
