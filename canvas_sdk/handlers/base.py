import json


class BaseHandler:
    """
    The class that all handlers inherit from.
    """

    def __init__(self, event, secrets=None) -> None:
        self.event = event
        try:
            self.context = json.loads(event.context)
        except ValueError:
            self.context = {}
        self.target = event.target
        self.secrets = secrets or {}
