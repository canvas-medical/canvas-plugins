import json

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler


class Handler(BaseHandler):
    """Annotate every search result so the autocomplete annotation chips always render."""

    RESPONDS_TO = [
        EventType.Name(EventType.DIAGNOSE__DIAGNOSE__POST_SEARCH),
        EventType.Name(EventType.ASSESS__CONDITION__POST_SEARCH),
    ]

    ANNOTATIONS = ["Demo", "Annotation"]

    def compute(self) -> list[Effect]:
        """Attach demo annotations to each search result and echo them back."""
        results = self.event.context.get("results")
        if results is None:
            return [Effect(type=EffectType.AUTOCOMPLETE_SEARCH_RESULTS, payload=json.dumps(None))]

        for result in results:
            result["annotations"] = list(self.ANNOTATIONS)

        return [
            Effect(
                type=EffectType.AUTOCOMPLETE_SEARCH_RESULTS,
                payload=json.dumps(results),
            )
        ]
