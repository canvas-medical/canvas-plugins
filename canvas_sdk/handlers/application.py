from abc import ABC, abstractmethod

from canvas_sdk.effects import Effect
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler


class Application(BaseHandler, ABC):
    """An embeddable application that can be registered to Canvas."""

    RESPONDS_TO = [
        EventType.Name(EventType.APPLICATION__ON_OPEN),
        EventType.Name(EventType.APPLICATION__ON_CONTEXT_CHANGE),
    ]

    def compute(self) -> list[Effect]:
        """Handle the application events."""
        match self.event.type:
            case EventType.APPLICATION__ON_OPEN:
                return [self.on_open()] if self.event.target.id == self.identifier else []
            case EventType.APPLICATION__ON_CONTEXT_CHANGE:
                if self.event.target.id == self.identifier:
                    effect = self.on_context_change()
                    return [effect] if effect is not None else []
                return []
            case _:
                return []

    @abstractmethod
    def on_open(self) -> Effect:
        """Handle the application open event."""
        ...

    def on_context_change(self) -> Effect | None:
        """Handle the application context change event."""
        return None

    @property
    def identifier(self) -> str:
        """The application identifier."""
        return f"{self.__class__.__module__}:{self.__class__.__qualname__}"


__exports__ = ("Application",)
