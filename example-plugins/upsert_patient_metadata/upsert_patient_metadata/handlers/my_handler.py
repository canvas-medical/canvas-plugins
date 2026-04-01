import re

from canvas_sdk.effects import Effect
from canvas_sdk.effects.patient_metadata import PatientMetadata
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from logger import log


class MyHandler(BaseHandler):
    """
    Extracts key-value pairs from plan update narratives and stores them as patient metadata.

    Parses narrative text for patterns like "key=somekey*value=somevalue" where the separator
    can be any non-alphanumeric character. If both key and value are found, creates or updates
    the corresponding patient metadata entry.

    Triggers on: PLAN_COMMAND__POST_UPDATE events
    Effects: PatientMetadata upsert operations
    """

    RESPONDS_TO = EventType.Name(EventType.PLAN_COMMAND__POST_UPDATE)

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        patient_id = self.context["patient"]["id"]
        fields = self.context.get("fields", {})
        narrative = fields.get("narrative", "")

        key_match = re.search(r"key=([^*#_\s]+)", narrative)
        value_match = re.search(r"value=([^*#_\s]+)", narrative)

        key = key_match.group(1) if key_match else None
        value = value_match.group(1) if value_match else None

        log.info(
            f"Upserting patient metadata for patient {patient_id} with key: {key} and value: {value}"
        )

        if not key or not value:
            return []

        return [PatientMetadata(patient_id=patient_id, key=str(key)).upsert(str(value))]
