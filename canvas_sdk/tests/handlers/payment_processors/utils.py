import json

from canvas_generated.messages.events_pb2 import Event as EventRequest
from canvas_sdk.events import Event, EventType


def create_event(
    type: EventType,
    context: dict | None = None,
) -> Event:
    """Create an event with the given type and context."""
    return Event(
        EventRequest(
            type=type,
            context=json.dumps(context) if context else "{}",
        )
    )
