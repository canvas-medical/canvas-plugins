import dataclasses
import json
from functools import cached_property
from typing import Any

from django.apps import apps
from django.db import models

from canvas_generated.messages.events_pb2 import Event as EventRequest
from canvas_generated.messages.events_pb2 import EventType


@dataclasses.dataclass
class TargetType:
    """The target of the event."""

    id: str
    type: type[models.Model] | None

    @cached_property
    def instance(self) -> models.Model | None:
        """Return the instance of the target."""
        return self.type._default_manager.filter(id=self.id).first() if self.type else None


class Event:
    """An event that occurs in the Canvas environment."""

    name: str
    type: EventType
    context: dict[str, Any]
    target: TargetType

    def __init__(self, event_request: EventRequest) -> None:
        try:
            target_model = apps.get_model(app_label="v1", model_name=event_request.target_type)
        except LookupError:
            target_model = None

        try:
            context = json.loads(event_request.context)
        except ValueError:
            context = {}

        self.type = event_request.type
        self.name = EventType.Name(self.type)
        self.context = context
        self.target = TargetType(id=event_request.target, type=target_model)


__exports__ = ("TargetType", "Event")
