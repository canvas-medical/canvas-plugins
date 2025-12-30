"""Protocol demonstrating all Data Integration effects."""

from datetime import date

from pydantic import ValidationError

from canvas_sdk.effects import Effect
from canvas_sdk.effects.categorize_document import (
    CategorizeDocument,
    DocumentType,
)
from canvas_sdk.effects.categorize_document import (
    ConfidenceScores as CategorizeDocumentConfidenceScores,
)
from canvas_sdk.effects.data_integration import (
    AssignDocumentReviewer,
    LinkDocumentToPatient,
    Priority,
    ReviewMode,
)
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from canvas_sdk.v1.data import Staff, Team
from logger import log


class DataIntegrationHandler(BaseProtocol):
    """
    Protocol that demonstrates all Data Integration effects.

    This protocol responds to DOCUMENT_RECEIVED events and demonstrates:
    1. LinkDocumentToPatient - Links documents to patients based on demographics
    2. AssignDocumentReviewer - Assigns a reviewer (staff or team) to documents
    3. CategorizeDocument - Categorizes documents into specific document types

    Triggers on: DOCUMENT_RECEIVED events
    """

    RESPONDS_TO = EventType.Name(EventType.DOCUMENT_RECEIVED)

    def compute(self) -> list[Effect]:
        """
        Process incoming documents and apply Data Integration effects.

        Returns:
            A list of Data Integration effects to apply.
        """
        document_id = self.event.context.get("document", {}).get("id")

        if not document_id:
            log.warning("Missing document.id in event context")
            return []

        log.info(f"Processing document {document_id} for data integration effects")

        effects: list[Effect] = []

        # Create LinkDocumentToPatient effect
        link_effect = self._create_link_document_effect(document_id)
        if link_effect:
            effects.append(link_effect)

        # Create AssignDocumentReviewer effect
        assign_effect = self._create_assign_reviewer_effect(document_id)
        if assign_effect:
            effects.append(assign_effect)

        # Create CategorizeDocument effect
        categorize_effect = self._create_categorize_document_effect(document_id)
        if categorize_effect:
            effects.append(categorize_effect)

        log.info(f"Returning {len(effects)} effect(s) for document {document_id}")
        return effects

    def _create_link_document_effect(self, document_id: str) -> Effect | None:
        """Create a LinkDocumentToPatient effect with sample patient data."""
        try:
            # In a real implementation, you would extract patient demographics
            # from the document using OCR/LLM. This uses sample data for demo.
            effect = LinkDocumentToPatient(
                document_id=str(document_id),
                first_name="John",
                last_name="Doe",
                date_of_birth=date(1990, 5, 15),
                confidence_scores={
                    "first_name": 0.95,
                    "last_name": 0.92,
                    "date_of_birth": 0.88,
                },
            )
            log.info(f"Created LinkDocumentToPatient effect for document {document_id}")
            return effect.apply()
        except ValidationError as e:
            log.error(f"Validation error creating LinkDocumentToPatient: {e}")
            return None

    def _create_assign_reviewer_effect(self, document_id: str) -> Effect | None:
        """Create an AssignDocumentReviewer effect using first available staff/team."""
        # Fetch first available staff member
        staff = Staff.objects.first()

        # Fetch first available team (optional)
        team = Team.objects.first()

        log.info(
            f"Found staff: {staff.id if staff else None}, team: {team.id if team else None}"
        )

        try:
            # Prefer staff over team assignment
            if staff:
                effect = AssignDocumentReviewer(
                    document_id=str(document_id),
                    reviewer_id=str(staff.id),
                    priority=Priority.HIGH,
                    review_mode=ReviewMode.REVIEW_REQUIRED,
                    confidence_scores={"document_id": 0.95},
                )
                log.info(f"Assigned staff {staff.id} to document {document_id}")
            elif team:
                effect = AssignDocumentReviewer(
                    document_id=str(document_id),
                    team_id=str(team.id),
                    priority=Priority.HIGH,
                    review_mode=ReviewMode.REVIEW_REQUIRED,
                    confidence_scores={"document_id": 0.95},
                )
                log.info(f"Assigned team {team.id} to document {document_id}")
            else:
                log.warning(f"No staff or team available for document {document_id}")
                return None

            return effect.apply()

        except ValidationError as e:
            log.error(f"Validation error assigning reviewer to document {document_id}: {e}")
            return None

    def _create_categorize_document_effect(self, document_id: str) -> Effect | None:
        """Create a CategorizeDocument effect using available document types."""
        available_document_types = self.event.context.get("available_document_types", [])

        if not available_document_types:
            log.warning(f"No available_document_types in context for document {document_id}")
            return None

        # Find "Lab Report" document type, or use the first available
        lab_report_type = next(
            (dt for dt in available_document_types if dt.get("name") == "Lab Report"),
            None,
        )

        if not lab_report_type:
            # Fall back to first available document type
            lab_report_type = available_document_types[0]
            log.info(
                f"Lab Report not found, using first available type: {lab_report_type.get('name')}"
            )

        try:
            document_type: DocumentType = {
                "key": lab_report_type["key"],
                "name": lab_report_type["name"],
                "report_type": lab_report_type["report_type"],
                "template_type": lab_report_type.get("template_type"),
            }

            confidence_scores: CategorizeDocumentConfidenceScores = {
                "document_id": 0.90,
                "document_type": {
                    "key": 0.90,
                    "name": 0.95,
                    "report_type": 0.85,
                },
            }

            effect = CategorizeDocument(
                document_id=str(document_id),
                document_type=document_type,
                confidence_scores=confidence_scores,
            )

            log.info(
                f"Categorizing document {document_id} as {document_type['name']}"
            )
            return effect.apply()

        except (ValidationError, KeyError) as e:
            log.error(f"Error creating CategorizeDocument effect: {e}")
            return None
