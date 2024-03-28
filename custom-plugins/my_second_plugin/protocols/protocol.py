import json


class Protocol:
    RESPONDS_TO = "SOMETHING_ELSE"

    NARRATIVE_STRING = ""

    def __init__(self, event) -> None:
        self.event = event
        self.payload = json.loads(event.target)

    def compute(self):
        return [{"effect_type": "ANOTHER_COMMAND_ADDITION", "payload": {}}]
