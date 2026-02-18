from abc import ABC, abstractmethod

from canvas_sdk.effects import Effect
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from canvas_sdk.handlers.action_button import ActionButton
from canvas_sdk.handlers.utils import normalize_effects


class Application(BaseHandler, ABC):
    """An embeddable application that can be registered to Canvas."""

    RESPONDS_TO = [
        EventType.Name(EventType.APPLICATION__ON_OPEN),
        EventType.Name(EventType.APPLICATION__ON_CONTEXT_CHANGE),
    ]

    def compute(self) -> list[Effect]:
        """Handle the application events."""
        if self.event.target.id != self.identifier:
            return []
        match self.event.type:
            case EventType.APPLICATION__ON_OPEN:
                return normalize_effects(self.on_open())
            case EventType.APPLICATION__ON_CONTEXT_CHANGE:
                return normalize_effects(self.on_context_change())
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


class NoteApplication(ActionButton):
    """An Application that can be shown in a note."""

    NAME: str = ""
    IDENTIFIER: str = ""

    @property
    def BUTTON_TITLE(self) -> str:  # type: ignore[override]
        """Return NAME as the button title."""
        return self.NAME

    @property
    def BUTTON_KEY(self) -> str:  # type: ignore[override]
        """Return IDENTIFIER as the button key."""
        return self.IDENTIFIER

    @property
    def BUTTON_LOCATION(self) -> ActionButton.ButtonLocation:  # type: ignore[override]
        """Return the note body as the button location."""
        return ActionButton.ButtonLocation.NOTE_BODY

    @abstractmethod
    def handle(self) -> list[Effect]:
        """Method to handle button click."""
        raise NotImplementedError("Implement to handle button click")


__exports__ = (
    "Application",
    "NoteApplication",
)
