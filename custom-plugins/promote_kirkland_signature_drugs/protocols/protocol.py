import json

from canvas_sdk.events import EventType
from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.protocols import BaseProtocol


class Protocol(BaseProtocol):
    def __init__(self, event) -> None:
        self.event = event
        self.context = json.loads(event.context)

    def compute(self):
        results = self.context.get("results")

        if results is None:
            return [Effect(type=EffectType.AUTOCOMPLETE_SEARCH_RESULTS, payload=json.dumps(None))]

        post_processed_results = []
        for result in results:
            should_float_to_top = False
            for coding in result.get("extra", {}).get("coding", []):
                if (
                    coding.get("code") == 554704
                    and coding.get("system") == "http://www.fdbhealth.com/"
                ):
                    if result.get("annotations") is None:
                        result["annotations"] = []
                    result["annotations"].append("Kirkland Signature")
                    should_float_to_top = True
            if should_float_to_top:
                post_processed_results.insert(0, result)
            else:
                post_processed_results.append(result)

        return [
            Effect(
                type=EffectType.AUTOCOMPLETE_SEARCH_RESULTS,
                payload=json.dumps(post_processed_results),
            )
        ]
