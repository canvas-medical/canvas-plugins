# Create a class (embeddable application) that on install, registers an application to Canvas.
# These registered applications would show up WITHOUT any plugin effect required.
# Developers should be able to specify:
# Scope: Patient-Specific and/or Global
# Icon: specific file size, type, dimensions (equivalent to existing icons)
# upload in larger size and we convert? High res & icon?
# Target: Default Modal, New Window, Right Chart Pane
# can we add validation to prevent right chart pane if scope includes global.
# Application Identifier (needed for event that launches application)
# Set by Canvas based on plugin module & class (similar to an android activity)
from canvas_generated.messages.effects_pb2 import Effect
from canvas_generated.messages.events_pb2 import EventType
from canvas_sdk.handlers import BaseHandler


class Application(BaseHandler):
    """An embeddable application that can be registered to Canvas."""

    RESPONDS_TO = [EventType.APPLICATION__ON_OPEN]

    def compute(self) -> list[Effect]:
        """Handle the application events."""
        match self.event.type:
            case EventType.APPLICATION__ON_OPEN:
                return [self.on_open()]

    def on_open(self) -> Effect:
        """Handle the application open event."""
        pass
