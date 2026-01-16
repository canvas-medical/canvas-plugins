"""Protocol demonstrating the ASSIGN_DOCUMENT_REVIEWER effect with prefill data.

This protocol shows the full flow:
1. Link document to patient
2. Categorize document (set document type)
3. Assign reviewer with annotations
"""

from pydantic import ValidationError

from canvas_sdk.effects import Effect
from canvas_sdk.effects.categorize_document import CategorizeDocument
from canvas_sdk.effects.data_integration import (
    AssignDocumentReviewer,
    LinkDocumentToPatient,
    Priority,
    ReviewMode,
)
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from canvas_sdk.v1.data import Patient, Staff, Team
from logger import log


class AssignDocumentReviewerProtocol(BaseProtocol):
    """
    A protocol that demonstrates the full document processing flow.

    This protocol responds to DOCUMENT_RECEIVED events and:
    1. Links the document to a patient (using first patient in DB)
    2. Categorizes the document (sets document type to Lab Report)
    3. Assigns a reviewer with annotations

    Triggers on: DOCUMENT_RECEIVED events
    Effects: LinkDocumentToPatient, CategorizeDocument, AssignDocumentReviewer
    """

    RESPONDS_TO = EventType.Name(EventType.DOCUMENT_RECEIVED)

    def compute(self) -> list[Effect]:
        """
        Process the received document with full flow.

        This demonstrates emitting multiple effects in sequence to:
        1. Link the document to a patient
        2. Set the document type
        3. Assign a reviewer with annotations
        """
        # Get the document ID from the event target
        document_id = self.event.context.get("document", {}).get("id")

        log.info(f"Processing document {document_id} - full flow")

        effects: list[Effect] = []

        try:
            # 1. Link document to patient
            patient = Patient.objects.first()
            if patient:
                link_effect = LinkDocumentToPatient(
                    document_id=str(document_id),
                    first_name=patient.first_name,
                    last_name=patient.last_name,
                    date_of_birth=patient.birth_date,
                    confidence_scores={
                        "first_name": 0.95,
                        "last_name": 0.95,
                        "date_of_birth": 0.90,
                    },
                )
                effects.append(link_effect.apply())
                log.info(
                    f"Linked document {document_id} to patient "
                    f"{patient.first_name} {patient.last_name}"
                )
            else:
                log.warning("No patient found - skipping link step")

            # 2. Categorize document (set document type)
            categorize_effect = CategorizeDocument(
                document_id=str(document_id),
                document_type={
                    "key": "f605e084dcad4beca16c0f62e6586d76",  # Lab Report key
                    "name": "Lab Report",
                    "report_type": "CLINICAL",
                    "template_type": "LabReportTemplate",
                },
                confidence_scores={
                    "document_id": 0.95,
                    "document_type": {
                        "key": 0.92,
                        "name": 0.92,
                        "report_type": 0.88,
                    },
                },
            )
            effects.append(categorize_effect.apply())
            log.info(f"Categorized document {document_id} as Lab Report")

            # 3. Assign reviewer with annotations
            staff = Staff.objects.first()
            team = Team.objects.first()

            if staff:
                assign_effect = AssignDocumentReviewer(
                    document_id=str(document_id),
                    reviewer_id=str(staff.id),
                    team_id=str(team.id) if team else None,
                    priority=Priority.HIGH,
                    review_mode=ReviewMode.REVIEW_NOT_REQUIRED,
                    # Annotations are stored directly with the prefill for display
                    # Each annotation has "text" and "color" attributes
                    annotations=[
                        {"text": "Team lead", "color": "#4CAF50"},
                        {"text": "Primary care", "color": "#2196F3"},
                        {"text": "Auto-assigned", "color": "#FF9800"},
                    ],
                    # Source protocol identifies which plugin generated this
                    source_protocol="assign_document_reviewer_example",
                )
                applied_assign_effect = assign_effect.apply()
                # Debug: log the full payload to verify annotations are included
                log.info(f"AssignDocumentReviewer payload: {applied_assign_effect.payload}")
                effects.append(applied_assign_effect)
                log.info(f"Assigned reviewer {staff.id} to document {document_id} with annotations")
            else:
                log.warning(f"No staff available for document {document_id}")

            return effects

        except ValidationError as e:
            log.error(f"Validation error processing document {document_id}: {e}")
            return []
