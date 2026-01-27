"""Protocol demonstrating the full document processing flow with all Data Integration effects."""

from pydantic import ValidationError

from canvas_sdk.effects import Effect
from canvas_sdk.effects.categorize_document import CategorizeDocument
from canvas_sdk.effects.data_integration import (
    AssignDocumentReviewer,
    LinkDocumentToPatient,
    Priority,
    ReviewMode,
)
from canvas_sdk.effects.data_integration.types import AnnotationItem
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from canvas_sdk.v1.data import Patient, Staff, Team
from logger import log


class AssignDocumentReviewerProtocol(BaseProtocol):
    """
    A protocol that demonstrates the full document processing flow.

    Triggers on: DOCUMENT_RECEIVED events
    Effects: LinkDocumentToPatient, CategorizeDocument, AssignDocumentReviewer
    """

    RESPONDS_TO = EventType.Name(EventType.DOCUMENT_RECEIVED)

    def compute(self) -> list[Effect]:
        """Process the received document with full flow."""
        document_id = self.event.context.get("document", {}).get("id")

        log.info(f"Processing document {document_id} for rewiewer assignment")

        effects: list[Effect] = []

        link_effect = self._create_link_effect(document_id)
        if link_effect:
            effects.append(link_effect)

        categorize_effect = self._create_categorize_effect(document_id)
        if categorize_effect:
            effects.append(categorize_effect)

        assign_effect = self._create_assign_effect(document_id)
        if assign_effect:
            effects.append(assign_effect)

        log.info(f"Returning {len(effects)} effect(s) for document {document_id}")
        return effects

    def _create_link_effect(self, document_id: str) -> Effect | None:
        """Create a LinkDocumentToPatient effect using first available patient."""
        patient = Patient.objects.first()
        if not patient:
            log.warning(f"No patient available for document {document_id}")
            return None

        try:
            effect = LinkDocumentToPatient(
                document_id=str(document_id),
                patient_key=str(patient.id),
                annotations=[
                    AnnotationItem(text="AI 95%", color="#00AA00"),
                    AnnotationItem(text="Auto-linked", color="#2196F3"),
                ],
                source_protocol="assign_document_reviewer_example",
            )
            log.info(
                f"Linked document {document_id} to patient {patient.first_name} {patient.last_name}"
            )
            return effect.apply()
        except ValidationError as e:
            log.error(f"Validation error creating LinkDocumentToPatient: {e}")
            return None

    def _create_categorize_effect(self, document_id: str) -> Effect | None:
        """Create a CategorizeDocument effect, preferring Lab Report type."""
        available_document_types = self.event.context.get("available_document_types", [])

        if not available_document_types:
            log.warning(f"No available_document_types in context for document {document_id}")
            return None

        # Prefer "Lab Report" document type, fall back to first available
        doc_type = next(
            (dt for dt in available_document_types if dt.get("name") == "Lab Report"),
            available_document_types[0],
        )

        try:
            effect = CategorizeDocument(
                document_id=str(document_id),
                document_type={
                    "key": doc_type["key"],
                    "name": doc_type["name"],
                    "report_type": doc_type["report_type"],
                    "template_type": doc_type.get("template_type"),
                },
                annotations=[
                    AnnotationItem(text="AI 92%", color="#00AA00"),
                    AnnotationItem(text="Auto-categorized", color="#2196F3"),
                ],
                source_protocol="assign_document_reviewer_example",
            )
            log.info(f"Categorized document {document_id} as {doc_type['name']}")
            return effect.apply()
        except (ValidationError, KeyError) as e:
            log.error(f"Validation error creating CategorizeDocument: {e}")
            return None

    def _create_assign_effect(self, document_id: str) -> Effect | None:
        """Create an AssignDocumentReviewer effect."""
        staff = Staff.objects.first()
        team = Team.objects.first()

        if not staff:
            log.warning(f"No staff available for document {document_id}")
            return None

        try:
            effect = AssignDocumentReviewer(
                document_id=str(document_id),
                reviewer_id=str(staff.id),
                team_id=str(team.id) if team else None,
                priority=Priority.HIGH,
                review_mode=ReviewMode.REVIEW_NOT_REQUIRED,
                annotations=[
                    AnnotationItem(text="Team lead", color="#4CAF50"),
                    AnnotationItem(text="Primary care", color="#2196F3"),
                    AnnotationItem(text="Auto-assigned", color="#FF9800"),
                ],
                source_protocol="assign_document_reviewer_example",
            )
            log.info(f"Assigned reviewer {staff.id} to document {document_id}")
            return effect.apply()
        except ValidationError as e:
            log.error(f"Validation error creating AssignDocumentReviewer: {e}")
            return None
