import json

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from logger import log


class Protocol(BaseProtocol):
    """
    Protocol that listens to OBSERVATION_CREATED events and logs glucose observations.

    This plugin captures glucose-related observation creation events and logs details
    about the observation for debugging or auditing purposes. Non-glucose observations
    are ignored.
    """

    # Listen to observation creation events
    RESPONDS_TO = EventType.Name(EventType.OBSERVATION_CREATED)

    # Common glucose-related LOINC codes
    GLUCOSE_LOINC_CODES = {
        "2339-0",  # Glucose [Mass/volume] in Blood
        "2345-7",  # Glucose [Mass/volume] in Serum or Plasma
        "41653-7",  # Glucose [Mass/volume] in Capillary blood by Glucometer
        "1558-6",  # Fasting glucose [Mass/volume] in Serum or Plasma
        "14749-6",  # Glucose [Moles/volume] in Serum or Plasma
        "14743-9",  # Glucose [Moles/volume] in Capillary blood by Glucometer
        "1521-4",  # Glucose [Mass/volume] in Serum or Plasma --post dose glucose
        "20438-8",  # Glucose [Mass/volume] in Capillary blood
        "6689-4",  # Glucose [Mass/volume] in Cerebral spinal fluid
        "15074-8",  # Glucose [Moles/volume] in Blood
    }

    def compute(self) -> list[Effect]:
        """
        Log glucose observation context and target when a glucose observation is created.

        Returns early if the observation is not glucose-related.

        Returns:
            list[Effect]: A list containing a LOG effect with the observation details,
                         or an empty list if the observation is not glucose-related.
        """
        # Get the observation code from the event context
        observation = self.event.context.get("observation", {})
        code_info = observation.get("code", {})
        loinc_code = code_info.get("code")

        # Return early if this is not a glucose observation
        if loinc_code not in self.GLUCOSE_LOINC_CODES:
            log.debug(f"Ignoring non-glucose observation with LOINC code: {loinc_code}")
            return []

        # Log the glucose observation event
        log.info(f"OBSERVATION_CREATED event fired for glucose observation: {self.event.target}")

        # Prepare the payload with context and target information
        payload = {
            "event_type": "OBSERVATION_CREATED",
            "target": self.event.target,
            "context": self.event.context,
        }

        # Log the glucose observation details
        log.info(f"Glucose observation context: {json.dumps(self.event.context, indent=2)}")
        log.info(f"Glucose observation target: {self.event.target}")

        # Return a LOG effect with the payload
        return [Effect(type=EffectType.LOG, payload=json.dumps(payload))]
