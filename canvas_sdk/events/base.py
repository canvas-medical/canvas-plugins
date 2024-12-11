import json
from typing import Any, NotRequired, TypedDict

from django.db import models

from canvas_generated.messages.events_pb2 import Event as EventRequest
from canvas_generated.messages.events_pb2 import EventType


class TargetType(TypedDict):
    """The target of the event."""

    id: str
    type: NotRequired[models.Model]


class Event:
    """An event that occurs in the Canvas environment."""

    type: EventType
    initial_context: dict[str, Any]
    context: dict[str, Any]
    target: TargetType

    def __init__(self, event_request: EventRequest) -> None:
        # target_model = apps.get_model(app_label="canvas_sdk", model_name=event_request.target_type)

        try:
            context = json.loads(event_request.context)
        except ValueError:
            context = {}

        self.type = event_request.type
        self.initial_context = context
        self.context = context
        self.target = TargetType(id=event_request.target)

    @property
    def name(self) -> str:
        """The name of the event."""
        return EventType.Name(self.type)
