import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from canvas_generated.messages.events_pb2 import Event
    from canvas_sdk.data.client import _CanvasGQLClient


class BaseHandler:
    """
    The class that all handlers inherit from.
    """

    def __init__(
        self,
        event: "Event",
        secrets: dict[str, Any] | None = None,
        client: "_CanvasGQLClient | None" = None,
    ) -> None:
        self.event = event
        try:
            self.context = json.loads(event.context)
        except ValueError:
            self.context = {}
        self.target = event.target
        self.secrets = secrets or {}
        self.client = client
