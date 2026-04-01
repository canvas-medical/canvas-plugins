import importlib.metadata
from abc import ABC, abstractmethod
from enum import StrEnum

import deprecation

from canvas_sdk.effects import Effect
from canvas_sdk.effects.show_application import ShowApplicationEffect
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from canvas_sdk.handlers.utils import normalize_effects

version = importlib.metadata.version("canvas")


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


class ApplicationScope(StrEnum):
    """Available scopes for embedded applications."""

    NOTE = "note"


class EmbeddedApplication(Application, ABC):
    """An embeddable application that can be registered to Canvas."""

    NAME: str
    SCOPE: ApplicationScope
    IDENTIFIER: str | None = None
    PRIORITY: int = 0

    def compute(self) -> list[Effect]:
        """Handle the application events."""
        match self.event.type:
            case EventType.APPLICATION__ON_GET:
                if self._matches_scope() and self.visible():
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

    def _matches_scope(self) -> bool:
        """Check if the event scope matches the application scope."""
        return self.event.context.get("scope") == self.SCOPE

    def open_by_default(self) -> bool:
        """Open the application by default."""
        return False

    def visible(self) -> bool:
        """Determine whether the application should be visible."""
        return True

    @property
    def identifier(self) -> str:
        """The application identifier."""
        return self.IDENTIFIER if self.IDENTIFIER else super().identifier


class NoteApplication(EmbeddedApplication):
    """An Application that can be shown in a note."""

    SCOPE = ApplicationScope.NOTE

    def on_open(self) -> Effect | list[Effect]:
        """Delegate to handle() for backward compatibility with old plugins."""
        # If a subclass overrides handle(), call it for backward compat.
        # New plugins should override on_open() directly.
        context_patient = self.event.context.get("patient")
        if context_patient and (patient_id := context_patient.get("id")):
            self.event.target.id = patient_id

        return self.handle()

    @deprecation.deprecated(
        deprecated_in="0.111.0",
        removed_in="1.0.0",
        current_version=version,
        details="Use 'on_open' instead",
    )
    def handle(self) -> list[Effect]:
        """Method to handle application click/on_open."""
        return []


__exports__ = (
    "Application",
    "ApplicationScope",
    "EmbeddedApplication",
    "NoteApplication",
)
