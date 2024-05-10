import json

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol

from logger import log


class Protocol(BaseProtocol):
    RESPONDS_TO = EventType.Name(EventType.ASSESS_COMMAND__CONDITION_SELECTED)

    NARRATIVE_STRING = "monkey"

    def compute(self):
        log.info(self.NARRATIVE_STRING)
        payload = {
            "note": {"uuid": self.context["note"]["uuid"]},
            "data": {"narrative": self.NARRATIVE_STRING},
        }

        return [Effect(type=EffectType.ADD_PLAN_COMMAND, payload=json.dumps(payload))]
