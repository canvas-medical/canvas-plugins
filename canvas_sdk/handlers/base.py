import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from canvas_generated.messages.events_pb2 import Event


class BaseHandler:
    """
    The class that all handlers inherit from.
    """

    secrets: dict[str, Any]
    target: str

    def __init__(
        self,
        event: "Event",
        secrets: dict[str, Any] | None = None,
    ) -> None:
        self.event = event

        try:
            self.context = json.loads(event.context)
        except ValueError:
            self.context = {}

        self.target = event.target
        self.secrets = secrets or {}
