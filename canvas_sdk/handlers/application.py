import importlib.metadata
from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any

import deprecation

from canvas_sdk.effects import Effect
from canvas_sdk.effects.application_notification_badge import ApplicationNotificationBadge
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
        EventType.Name(EventType.APPLICATION__GET_NOTIFICATION_BADGE),
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
            case EventType.APPLICATION__GET_NOTIFICATION_BADGE:
                count = self.compute_notification_badge()
                if count is None:
                    return []
                staff = self.event.context.get("staff") or {}
                patient = self.event.context.get("patient") or {}
                staff_id = staff.get("id")
                patient_id = patient.get("id")
                staff_ids = [str(staff_id)] if staff_id else []
                patient_ids = [str(patient_id)] if patient_id else []
                return [
                    ApplicationNotificationBadge(application_identifier=self.identifier)
                    .filter(patient_ids=patient_ids)
                    .broadcast(count, staff_ids=staff_ids)
                ]
            case _:
                return []

    @abstractmethod
    def on_open(self) -> Effect | list[Effect]:
        """Handle the application open event."""
        ...

    def on_context_change(self) -> Effect | list[Effect] | None:
        """Handle the application context change event."""
        return None

    def compute_notification_badge(self) -> int | None:
        """Return the current notification badge count for this application.

        Override to expose a count on the application icon. Return ``None`` (the
        default) to emit no badge. ``0`` is a valid value and clears an existing
        badge.
        """
        return None

    @property
    def identifier(self) -> str:
        """The application identifier."""
        return f"{self.__class__.__module__}:{self.__class__.__qualname__}"


class ApplicationScope(StrEnum):
    """Available scopes for embedded applications."""

    NOTE = "note"
    SCHEDULING = "scheduling"
    DOCKED = "docked"


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
                    return [ShowApplicationEffect(**self._show_application_values()).apply()]
                return []
            case EventType.APPLICATION__GET_NOTIFICATION_BADGE:
                # Explicitly ignore the event here in case it's emitted directly.
                return []
            case _:
                return super().compute()

    def _show_application_values(self) -> dict[str, Any]:
        """What this application tells Canvas about itself on APPLICATION__ON_GET.

        Subclasses whose surface needs more than the common fields extend this rather
        than reimplementing ``compute``.
        """
        return {
            "name": self.NAME,
            "identifier": self.identifier,
            "open_by_default": self.open_by_default(),
            "priority": self.PRIORITY,
        }

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


class DockEdge(StrEnum):
    """Which edge of the window a docked pane occupies."""

    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"


class DockedApplication(EmbeddedApplication):
    """An Application that mounts in a persistent pane on an edge of the window.

    A dock is always shown. It has no launcher entry to be opened from and no control to
    dismiss it, so its presence is settled by installing the plugin — which is why
    ``open_by_default`` is not overridable here the way it is for other embedded scopes.

    ``DOCK_EDGE`` and ``DOCK_SIZE`` are required: without them Canvas has nowhere to put
    the pane and no track to size, so a subclass omitting either is a programming error
    rather than a pane that quietly never appears.
    """

    SCOPE = ApplicationScope.DOCKED

    DOCK_EDGE: DockEdge
    DOCK_SIZE: str

    def open_by_default(self) -> bool:
        """Always true: a dock is chrome, not a window the user opens."""
        return True

    def _show_application_values(self) -> dict[str, Any]:
        """Add the placement Canvas needs to size the pane's track."""
        for attribute in ("DOCK_EDGE", "DOCK_SIZE"):
            if not getattr(self, attribute, None):
                raise NotImplementedError(
                    f"{type(self).__name__} must set {attribute}: a docked application "
                    "has nowhere to mount without an edge and a size."
                )

        return {
            **super()._show_application_values(),
            "dock_edge": DockEdge(self.DOCK_EDGE).value,
            "dock_size": self.DOCK_SIZE,
        }


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


class SchedulingApplication(EmbeddedApplication):
    """An Application that replaces the built-in scheduling modal.

    Implement ``on_open`` to return a ``LaunchModalEffect``. The following keys
    may be present on ``self.event.context``, each only when the originating
    entry point supplies it. Entities are delivered as ``{"id": <external id>}``
    objects, resolvable with the conventional ``.objects.get(id=...)``:

    * ``patient``: ``{"id": <patient key>}`` — patient chart and reschedule flows.
    * ``provider``: ``{"id": <staff key>}`` — calendar and chart.
    * ``location``: ``{"id": <practice location id>}`` — the current location.
    * ``appointment``: ``{"id": <appointment id>}`` — reschedule flows.
    * ``note``: ``{"id": <note id>}`` — note reschedule flow.

    And the following scalars:

    * ``start``: ISO-8601 datetime of the selected slot (all entry points).
    * ``end`` / ``duration``: the slot length arrives as *one or the other*
      depending on ``origin``, never both — ``end`` (ISO-8601) from the calendar
      drag-and-drop, ``duration`` (minutes) from the reschedule flows, and
      neither from the schedule-page / patient-chart buttons. Derive a missing
      end as ``start + duration``.
    * ``mode``: one of ``schedule``, ``reschedule``, ``followup``.
    * ``origin``: the launching surface — ``schedule_page``, ``patient_chart``,
      ``calendar``, ``calendar_reschedule``, or ``note_reschedule``.
    """

    SCOPE = ApplicationScope.SCHEDULING


__exports__ = (
    "Application",
    "ApplicationScope",
    "DockEdge",
    "DockedApplication",
    "EmbeddedApplication",
    "NoteApplication",
    "SchedulingApplication",
)
