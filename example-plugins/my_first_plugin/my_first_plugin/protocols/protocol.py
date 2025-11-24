import json

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from logger import log


class Protocol(BaseProtocol):
    """You should put a helpful description of this protocol's behavior here."""

    RESPONDS_TO = EventType.Name(EventType.ASSESS_COMMAND__CONDITION_SELECTED)

    NARRATIVE_STRING = "zebra"

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        log.info(self.NARRATIVE_STRING)
        payload = {
            "note": {"uuid": self.event.context["note"]["uuid"]},
            "data": {"narrative": self.NARRATIVE_STRING},
        }

        return [Effect(type=EffectType.LOG, payload=json.dumps(payload))]
