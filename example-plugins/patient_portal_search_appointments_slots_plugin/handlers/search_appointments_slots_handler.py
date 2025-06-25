import json

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.events import EventType
from canvas_sdk.handlers.base import BaseHandler


# Inherit from BaseHandler to properly get registered for events
class SearchAppointmentsSlotsHandler(BaseHandler):
    """Handler responsible for processing search appointments slots events."""

    # Name the event type you wish to run in response to
    RESPONDS_TO = EventType.Name(
        EventType.PATIENT_PORTAL__APPOINTMENTS__SLOTS__POST_SEARCH,
    )

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        slots_by_provider = json.loads(self.context.get("slots_by_provider") or "{}")

        if not slots_by_provider:
            return [self._respond_with(None)]

        filtered = {
            provider: dates
            for provider, dates in slots_by_provider.items()
            if not all(len(slots) == 0 for slots in dates.values())
        }

        payload = {
            "slots_by_provider": filtered
        }

        return [
            self._respond_with(payload),
        ]

    def _respond_with(self, payload: dict) -> Effect:
        """Helper method to create a response effect."""
        return Effect(
            type=EffectType.PATIENT_PORTAL__APPOINTMENTS__SLOTS__POST_SEARCH_RESULTS,
            payload=json.dumps(payload),
        )
