import json


class BaseProtocol:
    def __init__(self, event) -> None:
        self.event = event
        self.context = json.loads(event.context)
