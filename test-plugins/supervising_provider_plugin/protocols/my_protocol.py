import json

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from canvas_sdk.v1.data.staff import Staff
from logger import log


class Protocol(BaseProtocol):
    """You should put a helpful description of this protocol's behavior here."""

    RESPONDS_TO = [
        EventType.Name(EventType.PRESCRIBE__SUPERVISING_PROVIDER__POST_SEARCH),
        EventType.Name(EventType.PRESCRIBE__SUPERVISING_PROVIDER__PRE_SEARCH),
        EventType.Name(EventType.REFILL__SUPERVISING_PROVIDER__POST_SEARCH),
        EventType.Name(EventType.REFILL__SUPERVISING_PROVIDER__PRE_SEARCH),
        EventType.Name(EventType.ADJUST_PRESCRIPTION__SUPERVISING_PROVIDER__POST_SEARCH),
        EventType.Name(EventType.ADJUST_PRESCRIPTION__SUPERVISING_PROVIDER__PRE_SEARCH),
    ]

    NARRATIVE_STRING = "I was inserted from my supervising provider plugin's protocol."

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        log.info(self.NARRATIVE_STRING)

        results = self.context.get("results")

        if results is None:
            return [Effect(type=EffectType.AUTOCOMPLETE_SEARCH_RESULTS, payload=json.dumps(None))]

        post_processed_results = []
        for result in results:
            staff = Staff.objects.get(dbid=result["value"])
            if staff.spi_number:
                result["annotations"] = [f"SPI: {staff.spi_number}"]
            log.info(result)
            post_processed_results.append(result)

        return [
            Effect(
                type=EffectType.AUTOCOMPLETE_SEARCH_RESULTS,
                payload=json.dumps(post_processed_results),
            )
        ]
