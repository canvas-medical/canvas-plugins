import json


class Protocol:
    RESPONDS_TO = "ASSESS_COMMAND__CONDITION_SELECTED"

    def __init__(self, event) -> None:
        self.event = event
        self.payload = json.loads(event.target)

    def compute(self):
        return [{
            "effect_type": "ADD_PLAN_COMMAND",
            "payload": {
                "note": {
                    "uuid": self.payload["note"]["uuid"]
                },
                "data": {
                    "narrative": "monkey"
                }
            }
        }]
