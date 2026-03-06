import warnings
from abc import ABC, abstractmethod

from canvas_sdk.effects import Effect
from canvas_sdk.effects.show_application import ShowApplicationEffect
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from canvas_sdk.handlers.utils import normalize_effects


class Application(BaseHandler, ABC):
    """An embeddable application that can be registered to Canvas."""

    RESPONDS_TO = [
        EventType.Name(EventType.APPLICATION__ON_OPEN),
        EventType.Name(EventType.APPLICATION__ON_CONTEXT_CHANGE),
        EventType.Name(EventType.APPLICATION__ON_GET),
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


class DynamicApplication(Application, ABC):
    """An embeddable application that can be registered to Canvas."""

    NAME: str
    SCOPE: str
    IDENTIFIER: str | None = None
    PRIORITY: int = 0

    def compute(self) -> list[Effect]:
        """Handle the application events."""
        match self.event.type:
            case EventType.APPLICATION__ON_GET:
                if self.visible():
                    return [
                        ShowApplicationEffect(
                            name=self.NAME,
                            identifier=self.identifier,
                            open_by_default=self.open_by_default(),
                            priority=self.PRIORITY,
                        ).apply()
                    ]
                return []
            case _:
                return super().compute()

    def open_by_default(self) -> bool:
        """Open the application by default."""
        return False

    def visible(self) -> bool:
        """Determine whether the application should be visible."""
        return self.context.get("scope") == self.SCOPE

    @property
    def identifier(self) -> str:
        """The application identifier."""
        return self.IDENTIFIER if self.IDENTIFIER else super().identifier


class NoteApplication(DynamicApplication):
    """An Application that can be shown in a note."""

    SCOPE = "note"

    def on_open(self) -> Effect | list[Effect]:
        """Delegate to handle() for backward compatibility with old plugins."""
        # If a subclass overrides handle(), call it for backward compat.
        # New plugins should override on_open() directly.
        return self.handle()

    def handle(self) -> list[Effect]:
        """Method to handle application click/on_open.

        .. deprecated::
            Override :meth:`on_open` instead.
        """
        warnings.warn(
            "NoteApplication.handle() is deprecated. Override on_open() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return []


__exports__ = (
    "Application",
    "DynamicApplication",
    "NoteApplication",
)
