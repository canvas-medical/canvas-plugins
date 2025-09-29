from abc import ABC, abstractmethod

from canvas_sdk.effects import Effect
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from logger import log


class Application(BaseHandler, ABC):
    """An embeddable application that can be registered to Canvas."""

    RESPONDS_TO = [
        EventType.Name(EventType.APPLICATION__ON_OPEN),
        EventType.Name(EventType.APPLICATION__ON_CONTEXT_CHANGE),
    ]

    def compute(self) -> list[Effect]:
        """Handle the application events."""
        log.info(f"self.event.target.id: {self.event.target.id}")
        log.info(f"self.identifier: {self.identifier}")
        if self.event.target.id != self.identifier:
            return []
        log.info(f"Event type: {self.event.type}")
        match self.event.type:
            case EventType.APPLICATION__ON_OPEN:
                open_effect_or_effects = self.on_open()
                if type(open_effect_or_effects) is list[Effect]:
                    return open_effect_or_effects
                if type(open_effect_or_effects) is Effect:
                    return [open_effect_or_effects]
                return []
            case EventType.APPLICATION__ON_CONTEXT_CHANGE:
                context_effect_or_effects = self.on_context_change()
                if context_effect_or_effects is None:
                    return []
                if type(context_effect_or_effects) is list[Effect]:
                    return context_effect_or_effects
                if type(context_effect_or_effects) is Effect:
                    return [context_effect_or_effects]
                return []
            case _:
                return []

    @abstractmethod
    def on_open(self) -> Effect | list[Effect]:
        """Handle the application open event."""
        ...

    def on_context_change(self) -> Effect | list[Effect] | None:
        """Handle the application context change event."""
        return None

    @property
    def identifier(self) -> str:
        """The application identifier."""
        return f"{self.__class__.__module__}:{self.__class__.__qualname__}"


__exports__ = ("Application",)
