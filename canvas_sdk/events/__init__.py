from canvas_generated.messages.events_pb2 import Event as EventRequest
from canvas_generated.messages.events_pb2 import EventResponse, EventType

from .base import Event

__all__ = __canvas_allowed_attributes__ = (
    "EventRequest",
    "EventResponse",
    "EventType",
    "Event",
)
