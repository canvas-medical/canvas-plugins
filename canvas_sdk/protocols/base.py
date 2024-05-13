import json


class BaseProtocol:
    """
    The class that protocols inherit from.
    """

    def __init__(self, event, secrets=None) -> None:
        self.event = event
        self.context = json.loads(event.context)
        self.secrets = secrets or {}
