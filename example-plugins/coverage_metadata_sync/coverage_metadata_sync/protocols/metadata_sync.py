from canvas_sdk.effects import Effect
from canvas_sdk.effects.patient_metadata.base import PatientMetadata
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from logger import log

# The specific label and metadata key we are working with.
MONITORED_LABEL = "MISSING_COVERAGE"
METADATA_KEY = "coverage_status"


class CoverageStatusSyncProtocol(BaseProtocol):
    """
    Synchronizes patient metadata based on appointment label changes.

    This protocol listens for appointment label events and updates a patient's
    'coverage_status' metadata field when the 'MISSING_COVERAGE' label is added or removed:

    - When MISSING_COVERAGE label is ADDED → sets coverage_status to "Missing"
    - When MISSING_COVERAGE label is REMOVED → sets coverage_status to "Active"

    This provides a centralized metadata field that reflects the patient's current
    insurance coverage status, making it easy to query and report on coverage gaps.

    The protocol is designed to work seamlessly with the appointment_coverage_label plugin,
    which manages the addition and removal of the MISSING_COVERAGE label based on actual
    insurance coverage records.
    """

    RESPONDS_TO = [
        EventType.Name(EventType.APPOINTMENT_LABEL_ADDED),
        EventType.Name(EventType.APPOINTMENT_LABEL_REMOVED),
    ]

    def compute(self) -> list[Effect]:
        """
        Process appointment label events and update patient metadata accordingly.

        This method is called when an APPOINTMENT_LABEL_ADDED or APPOINTMENT_LABEL_REMOVED
        event is fired. It examines the event context to determine:
        1. Which label was affected
        2. The patient associated with the appointment
        3. Whether to update metadata (only for MISSING_COVERAGE label)

        The method includes defensive programming to safely access event context
        and handle any malformed events gracefully.

        Returns:
            list[Effect]: List containing a single PatientMetadata upsert effect if the
                         MISSING_COVERAGE label was affected, otherwise empty list
        """
        # Safely extract patient ID from event context
        patient_id = self.context.get("patient", {}).get("id")
        if not patient_id:
            log.warning(
                "No patient ID found in event context for label event. "
                "Cannot update metadata. Event type: {self.event.type}"
            )
            return []

        # Safely extract label name from event context
        label_in_event = self.context.get("label")
        if not label_in_event:
            log.warning(
                f"No label name found in event context for patient {patient_id}. "
                "Cannot determine which label was affected."
            )
            return []

        # Only process events for the MISSING_COVERAGE label
        if label_in_event != MONITORED_LABEL:
            log.info(
                f"Ignoring event for label '{label_in_event}' because it is not the "
                f"monitored label ('{MONITORED_LABEL}'). Patient: {patient_id}"
            )
            return []

        # Determine the new metadata value based on event type
        if self.event.type == EventType.APPOINTMENT_LABEL_ADDED:
            new_status = "Missing"
            log.info(
                f"MISSING_COVERAGE label added for patient {patient_id}. "
                f"Will update metadata '{METADATA_KEY}' to '{new_status}'."
            )
        elif self.event.type == EventType.APPOINTMENT_LABEL_REMOVED:
            new_status = "Active"
            log.info(
                f"MISSING_COVERAGE label removed for patient {patient_id}. "
                f"Will update metadata '{METADATA_KEY}' to '{new_status}'."
            )
        else:
            log.warning(
                f"Received unexpected event type '{self.event.type}' in "
                "CoverageStatusSyncProtocol. This event type is in RESPONDS_TO but "
                "has no handler logic defined."
            )
            return []

        log.info(
            f"Reacting to '{EventType.Name(self.event.type)}' event. "
            f"Updating patient {patient_id} metadata '{METADATA_KEY}' to '{new_status}'."
        )

        # Create and return the metadata update effect
        try:
            # Create an instance of the PatientMetadata effect
            metadata_effect_instance = PatientMetadata(patient_id=patient_id, key=METADATA_KEY)

            # Call .upsert() to generate the final Effect object with the new value
            # This will create the metadata field if it doesn't exist, or update it if it does
            update_effect = metadata_effect_instance.upsert(value=new_status)

            log.info(
                f"Successfully created PatientMetadata upsert effect for patient {patient_id}. "
                f"Metadata key: '{METADATA_KEY}', new value: '{new_status}'."
            )

            return [update_effect]

        except Exception as e:
            log.error(
                f"Failed to create PatientMetadata effect for patient {patient_id}. "
                f"Metadata key: '{METADATA_KEY}', intended value: '{new_status}'. "
                f"Error: {e}",
                exc_info=True,
            )
            return []
