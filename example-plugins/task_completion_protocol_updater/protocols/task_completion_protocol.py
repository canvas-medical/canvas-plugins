from canvas_sdk.effects import Effect
from canvas_sdk.effects.protocol_card import ProtocolCard
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from logger import log


class Protocol(BaseProtocol):
    """
    Updates ProtocolCard status when affiliated task is completed/closed.
    
    Listens for TASK_CLOSED events and checks if the completed task has:
    1. "LINKED_PROTOCOL_CARD" label indicating it satisfies/closes a protocol
    2. "PROTOCOL_CARD_{key}" label containing the exact protocol key to close
    
    When both labels are found, updates the protocol card with the specified key
    to status=SATISFIED for the task's patient.
    """

    RESPONDS_TO = EventType.Name(EventType.TASK_CLOSED)

    def compute(self) -> list[Effect]:
        """Process task completion and update linked protocol cards."""
        # Get the task information from the event target
        task = self.target.instance
        if not task:
            log.warning("No task instance found in event")
            return []

        # Get task labels
        task_labels = [label.name for label in task.labels.all()]
        log.info(f"Task {task.id} completed with labels: {task_labels}")

        # Check if task has LINKED_PROTOCOL_CARD label
        if "LINKED_PROTOCOL_CARD" not in task_labels:
            log.info(f"Task {task.id} does not have LINKED_PROTOCOL_CARD label, skipping")
            return []

        # Find the protocol key from PROTOCOL_CARD_{key} labels
        protocol_keys = [
            label.replace("PROTOCOL_CARD_", "")
            for label in task_labels
            if label.startswith("PROTOCOL_CARD_")
        ]

        if not protocol_keys:
            log.warning(
                f"Task {task.id} has LINKED_PROTOCOL_CARD label but no PROTOCOL_CARD_{{key}} label found"
            )
            return []

        if len(protocol_keys) > 1:
            log.warning(
                f"Task {task.id} has multiple PROTOCOL_CARD_{{key}} labels: {protocol_keys}. Using the first one."
            )

        protocol_key = protocol_keys[0]
        patient_id = str(task.patient.id) if task.patient else None

        if not patient_id:
            log.warning(f"Task {task.id} has no associated patient, cannot update protocol card")
            return []

        log.info(
            f"Updating protocol card with key '{protocol_key}' to SATISFIED for patient {patient_id}"
        )

        # Create and apply the protocol card update
        # Using SATISFIED status to mark the protocol card as completed
        protocol_card = ProtocolCard(
            patient_id=patient_id,
            key=protocol_key,
            status=ProtocolCard.Status.SATISFIED,
            title="Annual exam task"  # Preserve the original title
        )

        return [protocol_card.apply()]