from datetime import date

from canvas_sdk.effects import Effect
from canvas_sdk.effects.data_integration import (
    AssignDocumentReviewer,
    AssignDocumentReviewerConfidenceScores,
    JunkDocument,
    JunkDocumentConfidenceScores,
    LinkDocumentConfidenceScores,
    LinkDocumentToPatient,
    Priority,
    RemoveDocumentConfidenceScores,
    RemoveDocumentFromPatient,
    ReviewMode,
)
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from logger import log


class DataIntegrationHandler(BaseHandler):
    """
    Handler that demonstrates all Data Integration effects.

    This handler responds to DOCUMENT_RECEIVED events and applies effects based on
    the event context. It demonstrates:
    1. LinkDocumentToPatient - Links documents to patients based on demographics
    2. JunkDocument - Marks documents as junk/spam
    3. RemoveDocumentFromPatient - Removes documents from patients
    4. AssignDocumentReviewer - Assigns a reviewer (staff or team) to documents

    The handler checks the event context for action flags to determine which
    effects to apply.
    """

    RESPONDS_TO: list[str] = [
        EventType.Name(EventType.DOCUMENT_RECEIVED),
    ]

    def compute(self) -> list[Effect]:
        """
        Process incoming documents and apply appropriate Data Integration effects.

        Reads from event context to determine which effects to apply:
        - link_to_patient: Creates LinkDocumentToPatient effect
        - mark_as_junk: Creates JunkDocument effect
        - remove_from_patient: Creates RemoveDocumentFromPatient effect
        - assign_reviewer: Creates AssignDocumentReviewer effect

        Returns:
            A list of Data Integration effects to apply.
        """
        context = self.event.context
        document_id = context.get("document_id")

        if not document_id:
            log.warning("Missing document_id in event context")
            return []

        effects: list[Effect] = []

        # Try to create each effect based on context
        link_effect = self._create_link_document_effect(document_id, context)
        if link_effect:
            effects.append(link_effect)

        junk_effect = self._create_junk_document_effect(document_id, context)
        if junk_effect:
            effects.append(junk_effect)

        remove_effect = self._create_remove_document_effect(document_id, context)
        if remove_effect:
            effects.append(remove_effect)

        assign_effect = self._create_assign_reviewer_effect(document_id, context)
        if assign_effect:
            effects.append(assign_effect)

        return effects

    def _create_link_document_effect(self, document_id: str, context: dict) -> Effect | None:
        """Create a LinkDocumentToPatient effect from event context."""
        link_data = context.get("link_to_patient", {})
        if not link_data:
            return None

        first_name = link_data.get("first_name")
        last_name = link_data.get("last_name")
        dob_str = link_data.get("date_of_birth")

        if not first_name or not last_name or not dob_str:
            log.warning(
                "Missing required fields for LinkDocumentToPatient: document_id=%s",
                document_id,
            )
            return None

        # Parse date of birth
        try:
            date_of_birth = date.fromisoformat(dob_str)
        except (ValueError, TypeError) as e:
            log.error(
                "Invalid date_of_birth format for LinkDocumentToPatient: document_id=%s, dob=%s, error=%s",
                document_id,
                dob_str,
                str(e),
            )
            return None

        # Extract confidence scores if provided
        confidence_scores: LinkDocumentConfidenceScores | None = None
        if "confidence_scores" in link_data:
            confidence_scores = link_data["confidence_scores"]

        # Create the effect
        effect = LinkDocumentToPatient(
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            document_id=document_id,
            confidence_scores=confidence_scores,
        )

        return effect.apply()

    def _create_junk_document_effect(self, document_id: str, context: dict) -> Effect | None:
        """Create a JunkDocument effect from event context."""
        junk_data = context.get("mark_as_junk", {})
        if not junk_data:
            return None

        # Get confidence score, default to 0.95 if not provided
        confidence = junk_data.get("confidence", 0.95)

        # Create confidence scores
        confidence_scores: JunkDocumentConfidenceScores = {"junk": confidence}

        # Create the effect
        effect = JunkDocument(
            document_id=document_id,
            confidence_scores=confidence_scores,
        )

        return effect.apply()

    def _create_remove_document_effect(self, document_id: str, context: dict) -> Effect | None:
        """Create a RemoveDocumentFromPatient effect from event context."""
        remove_data = context.get("remove_from_patient", {})
        if not remove_data:
            return None

        patient_id = remove_data.get("patient_id")
        confidence = remove_data.get("confidence", 0.90)

        # Create confidence scores
        confidence_scores: RemoveDocumentConfidenceScores = {"removal": confidence}

        # Create the effect
        effect = RemoveDocumentFromPatient(
            document_id=document_id,
            patient_id=patient_id,
            confidence_scores=confidence_scores,
        )

        return effect.apply()

    def _create_assign_reviewer_effect(self, document_id: str, context: dict) -> Effect | None:
        """Create an AssignDocumentReviewer effect from event context."""
        assign_data = context.get("assign_reviewer", {})
        if not assign_data:
            return None

        reviewer_id = assign_data.get("reviewer_id")
        team_id = assign_data.get("team_id")

        # At least one of reviewer_id or team_id must be provided
        if not reviewer_id and not team_id:
            log.warning(
                "Missing reviewer_id or team_id for AssignDocumentReviewer: document_id=%s",
                document_id,
            )
            return None

        # Parse priority, default to NORMAL
        priority_str = assign_data.get("priority", "NORMAL")
        try:
            priority = Priority(priority_str.upper())
        except ValueError:
            log.warning(
                "Invalid priority value for AssignDocumentReviewer: document_id=%s, priority=%s, defaulting to NORMAL",
                document_id,
                priority_str,
            )
            priority = Priority.NORMAL

        # Parse review_mode, default to REVIEW_REQUIRED
        review_mode_str = assign_data.get("review_mode", "REVIEW_REQUIRED")
        try:
            review_mode = ReviewMode(review_mode_str.upper())
        except ValueError:
            log.warning(
                "Invalid review_mode value for AssignDocumentReviewer: document_id=%s, review_mode=%s, defaulting to REVIEW_REQUIRED",
                document_id,
                review_mode_str,
            )
            review_mode = ReviewMode.REVIEW_REQUIRED

        # Extract confidence scores if provided
        confidence_scores: AssignDocumentReviewerConfidenceScores | None = None
        if "confidence_scores" in assign_data:
            confidence_scores = assign_data["confidence_scores"]

        # Create the effect
        effect = AssignDocumentReviewer(
            document_id=document_id,
            reviewer_id=reviewer_id,
            team_id=team_id,
            priority=priority,
            review_mode=review_mode,
            confidence_scores=confidence_scores,
        )

        return effect.apply()
