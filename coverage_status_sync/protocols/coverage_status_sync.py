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
    A protocol that listens for appointment label events and updates a patient's
    'Coverage status' metadata field accordingly.
    """

    RESPONDS_TO = [
        EventType.Name(EventType.APPOINTMENT_LABEL_ADDED),
        EventType.Name(EventType.APPOINTMENT_LABEL_REMOVED),
    ]

    def compute(self) -> list[Effect]:
        """
        Reacts to label events and updates patient metadata. This implementation
        includes safe dictionary access to prevent crashes from malformed event contexts.
        """

        patient_id = self.context["patient"]["id"]
        label_in_event = self.context["label"]

        # Check if this is the specific label we want to react to.
        if label_in_event != MONITORED_LABEL:
            # This is a normal, expected case. The log clarifies we are intentionally skipping.
            log.info(f"Ignoring event for label '{label_in_event}' because it is not the monitored label ('{MONITORED_LABEL}').")
            return []

        if self.event.type == EventType.APPOINTMENT_LABEL_ADDED:
            new_status = "Missing"
        elif self.event.type == EventType.APPOINTMENT_LABEL_REMOVED:
            new_status = "Active"
        else:
            log.warning(f"Received an unexpected event type '{self.event.type}' that was not handled.")
            return []

        log.info(
            f"Reacting to '{self.event.type}'. Updating patient {patient_id} "
            f"metadata '{METADATA_KEY}' to '{new_status}'."
        )

        try:
            # Create an instance of the PatientMetadata effect.
            metadata_effect_instance = PatientMetadata(
                patient_id=patient_id, key=METADATA_KEY
            )

            # Call .upsert() to generate the final Effect object with the new value.
            update_effect = metadata_effect_instance.upsert(value=new_status)
            return [update_effect]
        except Exception as e:
            log.error(f"Failed to create PatientMetadata effect for patient {patient_id}: {e}", exc_info=True)
            return []
