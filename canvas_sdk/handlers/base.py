import importlib.metadata
from abc import ABC, abstractmethod
from typing import Any

import deprecation

from canvas_sdk.effects import Effect
from canvas_sdk.events import Event

version = importlib.metadata.version("canvas")


class BaseHandler(ABC):
    """The class that all handlers inherit from."""

    environment: dict[str, Any]
    secrets: dict[str, Any]
    event: Event

    def __init__(
        self,
        event: Event,
        secrets: dict[str, Any] | None = None,
        environment: dict[str, Any] | None = None,
    ) -> None:
        self.event = event
        self.secrets = secrets or {}
        self.environment = environment or {}

    @property
    @deprecation.deprecated(
        deprecated_in="0.11.0",
        removed_in="1.0.0",
        current_version=version,
        details="Use 'event.context' directly instead",
    )
    def context(self) -> dict[str, Any]:
        """The context of the event."""
        return self.event.context

    @property
    @deprecation.deprecated(
        deprecated_in="0.11.0",
        removed_in="1.0.0",
        current_version=version,
        details="Use 'event.target.id' directly instead",
    )
    def target(self) -> str:
        """The target id of the event."""
        return self.event.target.id

    @abstractmethod
    def compute(self) -> list[Effect]:
        """Compute the effects to be applied."""
        pass

    def accept_event(self) -> bool:
        """Determine whether an event should be accepted and handled by the handler."""
        return True


__exports__ = ("BaseHandler",)
