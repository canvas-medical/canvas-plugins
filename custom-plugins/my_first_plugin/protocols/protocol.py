import json

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol


class Protocol(BaseProtocol):
    NARRATIVE_STRING = "monkey"

    # TODO - move __init__ to BaseProtocol class;
    def __init__(self, event) -> None:
        self.event = event
        self.payload = json.loads(event.target)

    def compute(self):
        payload = {
            "note": {"uuid": self.payload["note"]["uuid"]},
            "data": {"narrative": self.NARRATIVE_STRING},
        }

        return [Effect(type=EffectType.ADD_PLAN_COMMAND, payload=json.dumps(payload))]
