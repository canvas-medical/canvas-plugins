"""Protocol demonstrating all Data Integration effects."""

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
    Protocol that demonstrates all Data Integration effects and document lifecycle events.

    Effects (emitted on DOCUMENT_RECEIVED):
    1. LinkDocumentToPatient - Links documents to patients based on demographics
    2. AssignDocumentReviewer - Assigns a reviewer (staff or team) to documents
    3. CategorizeDocument - Categorizes documents into specific document types

    Document Lifecycle Events (logged only):
    - DOCUMENT_LINKED_TO_PATIENT - Fires when document is linked to a patient
    - DOCUMENT_CATEGORIZED - Fires when document type is assigned
    - DOCUMENT_REVIEWER_ASSIGNED - Fires when reviewer is assigned
    - DOCUMENT_FIELDS_UPDATED - Fires when document fields change
    - DOCUMENT_REVIEWED - Fires when document review is completed
    - DOCUMENT_DELETED - Fires when document is soft-deleted
    """

    RESPONDS_TO = [
        EventType.Name(EventType.DOCUMENT_RECEIVED),
        EventType.Name(EventType.DOCUMENT_LINKED_TO_PATIENT),
        EventType.Name(EventType.DOCUMENT_CATEGORIZED),
        EventType.Name(EventType.DOCUMENT_REVIEWER_ASSIGNED),
        EventType.Name(EventType.DOCUMENT_FIELDS_UPDATED),
        EventType.Name(EventType.DOCUMENT_REVIEWED),
        EventType.Name(EventType.DOCUMENT_DELETED),
    ]

    def compute(self) -> list[Effect]:
        """
        Process incoming document events and route to appropriate handlers.

        Returns:
            A list of Data Integration effects to apply (only for DOCUMENT_RECEIVED).
        """
        event_name = EventType.Name(self.event.type)
        document_id = self.event.context.get("document", {}).get("id")

        if not document_id:
            log.warning(f"[{event_name}] Missing document.id in event context")
            return []

        log.info(f"[{event_name}] Processing document {document_id}")

        event_type = self.event.type
        if event_type == EventType.DOCUMENT_RECEIVED:
            return self._handle_document_received(document_id)
        elif event_type == EventType.DOCUMENT_LINKED_TO_PATIENT:
            return self._handle_document_linked_to_patient(document_id)
        elif event_type == EventType.DOCUMENT_CATEGORIZED:
            return self._handle_document_categorized(document_id)
        elif event_type == EventType.DOCUMENT_REVIEWER_ASSIGNED:
            return self._handle_document_reviewer_assigned(document_id)
        elif event_type == EventType.DOCUMENT_FIELDS_UPDATED:
            return self._handle_document_fields_updated(document_id)
        elif event_type == EventType.DOCUMENT_REVIEWED:
            return self._handle_document_reviewed(document_id)
        elif event_type == EventType.DOCUMENT_DELETED:
            return self._handle_document_deleted(document_id)
        else:
            log.warning(f"Received unexpected event type: {event_name}")
            return []

    def _handle_document_received(self, document_id: str) -> list[Effect]:
        """Handle DOCUMENT_RECEIVED: Apply all Data Integration effects."""
        effects: list[Effect] = []

        link_effect = self._create_link_document_effect(document_id)
        if link_effect:
            effects.append(link_effect)

        assign_effect = self._create_assign_reviewer_effect(document_id)
        if assign_effect:
            effects.append(assign_effect)

        categorize_effect = self._create_categorize_document_effect(document_id)
        if categorize_effect:
            effects.append(categorize_effect)

        log.info(f"[DOCUMENT_RECEIVED] Returning {len(effects)} effect(s) for document {document_id}")
        return effects

    def _handle_document_linked_to_patient(self, document_id: str) -> list[Effect]:
        """Handle DOCUMENT_LINKED_TO_PATIENT: Log successful patient linking."""
        ctx = self.event.context
        patient = ctx.get("patient", {})
        patient_id = patient.get("id")
        previous_patient = ctx.get("previous_patient")
        previous_patient_id = previous_patient.get("id") if previous_patient else None
        linked_at = ctx.get("linked_at")

        if previous_patient_id:
            log.info(
                f"[DOCUMENT_LINKED_TO_PATIENT] Document {document_id} relinked "
                f"from patient {previous_patient_id} to patient {patient_id} at {linked_at}"
            )
        else:
            log.info(
                f"[DOCUMENT_LINKED_TO_PATIENT] Document {document_id} "
                f"linked to patient {patient_id} at {linked_at}"
            )
        return []

    def _handle_document_categorized(self, document_id: str) -> list[Effect]:
        """Handle DOCUMENT_CATEGORIZED: Log document type assignment."""
        ctx = self.event.context
        doc_type = ctx.get("document_type")
        previous_type = ctx.get("previous_document_type")
        categorized_at = ctx.get("categorized_at")

        if doc_type:
            type_name = doc_type.get("name", "Unknown")
            report_type = doc_type.get("report_type", "Unknown")

            if previous_type:
                prev_name = previous_type.get("name", "Unknown")
                log.info(
                    f"[DOCUMENT_CATEGORIZED] Document {document_id} recategorized "
                    f"from '{prev_name}' to '{type_name}' ({report_type}) at {categorized_at}"
                )
            else:
                log.info(
                    f"[DOCUMENT_CATEGORIZED] Document {document_id} "
                    f"categorized as '{type_name}' ({report_type}) at {categorized_at}"
                )
        else:
            log.info(f"[DOCUMENT_CATEGORIZED] Document {document_id} uncategorized at {categorized_at}")
        return []

    def _handle_document_reviewer_assigned(self, document_id: str) -> list[Effect]:
        """Handle DOCUMENT_REVIEWER_ASSIGNED: Log reviewer assignment."""
        ctx = self.event.context
        reviewer = ctx.get("reviewer")
        previous_reviewer = ctx.get("previous_reviewer")
        assigned_at = ctx.get("assigned_at")

        if reviewer:
            reviewer_type = reviewer.get("type", "Unknown")
            reviewer_name = reviewer.get("name", "Unknown")
            reviewer_id = reviewer.get("id")

            if previous_reviewer:
                prev_name = previous_reviewer.get("name", "Unknown")
                prev_type = previous_reviewer.get("type", "Unknown")
                log.info(
                    f"[DOCUMENT_REVIEWER_ASSIGNED] Document {document_id} reassigned "
                    f"from {prev_type} '{prev_name}' to {reviewer_type} '{reviewer_name}' "
                    f"(id={reviewer_id}) at {assigned_at}"
                )
            else:
                log.info(
                    f"[DOCUMENT_REVIEWER_ASSIGNED] Document {document_id} "
                    f"assigned to {reviewer_type} '{reviewer_name}' (id={reviewer_id}) at {assigned_at}"
                )
        else:
            log.info(f"[DOCUMENT_REVIEWER_ASSIGNED] Document {document_id} reviewer unassigned at {assigned_at}")
        return []

    def _handle_document_fields_updated(self, document_id: str) -> list[Effect]:
        """Handle DOCUMENT_FIELDS_UPDATED: Log field changes (no effect available)."""
        ctx = self.event.context
        updated_fields = ctx.get("updated_fields", [])
        updated_at = ctx.get("updated_at")

        if not updated_fields:
            log.info(f"[DOCUMENT_FIELDS_UPDATED] Document {document_id} updated with no field changes at {updated_at}")
            return []

        log.info(f"[DOCUMENT_FIELDS_UPDATED] Document {document_id} fields updated at {updated_at}:")
        for field in updated_fields:
            field_name = field.get("name", "Unknown")
            value = field.get("value")
            previous_value = field.get("previous_value")
            log.info(f"  - {field_name}: '{previous_value}' -> '{value}'")

        log.info("[DOCUMENT_FIELDS_UPDATED] No UPDATE_DOCUMENT_FIELDS effect available yet")
        return []

    def _handle_document_reviewed(self, document_id: str) -> list[Effect]:
        """Handle DOCUMENT_REVIEWED: Log review completion (no effect available)."""
        ctx = self.event.context
        review = ctx.get("review", {})
        reviewed_at = ctx.get("reviewed_at")

        reviewer = review.get("reviewer", {})
        reviewer_name = reviewer.get("name", "Unknown") if reviewer else "Unknown"
        status = review.get("status", "Unknown")
        communication_method = review.get("patient_communication_method", "N/A")
        internal_comment = review.get("internal_comment", "")
        message_to_patient = review.get("message_to_patient", "")

        log.info(
            f"[DOCUMENT_REVIEWED] Document {document_id} reviewed by '{reviewer_name}' "
            f"with status '{status}' at {reviewed_at}"
        )
        if communication_method and communication_method != "N/A":
            log.info(f"  - Patient communication method: {communication_method}")
        if internal_comment:
            log.info(f"  - Internal comment: {internal_comment}")
        if message_to_patient:
            log.info(f"  - Message to patient: {message_to_patient}")

        log.info("[DOCUMENT_REVIEWED] No MARK_DOCUMENT_REVIEWED effect available yet")
        return []

    def _handle_document_deleted(self, document_id: str) -> list[Effect]:
        """Handle DOCUMENT_DELETED: Log document deletion."""
        ctx = self.event.context
        deleted_at = ctx.get("deleted_at")
        deleted_by = ctx.get("deleted_by")
        patient = ctx.get("patient")
        doc_type = ctx.get("document_type")

        if deleted_by:
            deleted_by_name = deleted_by.get("name", "Unknown")
            log.info(f"[DOCUMENT_DELETED] Document {document_id} deleted by '{deleted_by_name}' at {deleted_at}")
        else:
            log.info(f"[DOCUMENT_DELETED] Document {document_id} deleted at {deleted_at}")

        if patient:
            log.info(f"  - Was linked to patient: {patient.get('id')}")
        if doc_type:
            log.info(f"  - Document type was: {doc_type.get('name')}")
        return []

    def _create_link_document_effect(self, document_id: str) -> Effect | None:
        """Create a LinkDocumentToPatient effect using patient key."""
        try:
            # Sample patient key - in production, this would come from patient matching
            sample_patient_key = "5e4e107888564e359e1b3592e08f502f"

            effect = LinkDocumentToPatient(
                document_id=str(document_id),
                patient_key=sample_patient_key,
                annotations=[
                    {"text": "AI 95%", "color": "#00AA00"},
                    {"text": "DOB matched", "color": "#2196F3"},
                ],
                source_protocol="data_integration_example_v1",
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
