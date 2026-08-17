from abc import abstractmethod
from functools import cached_property
from typing import Any

from django.core.exceptions import ImproperlyConfigured

from canvas_sdk.effects import Effect
from canvas_sdk.effects.note_body_automation import ShowNoteBodyAutomationEffect
from canvas_sdk.events import EventType
from canvas_sdk.handlers.base import BaseHandler
from canvas_sdk.v1.data import Note

SHOW_AUTOMATIONS_EVENT = EventType.Name(EventType.SHOW_NOTE_BODY_AUTOMATIONS)
AUTOMATION_SELECTED_EVENT = EventType.Name(EventType.NOTE_BODY_AUTOMATION_SELECTED)


class NoteBodyAutomation(BaseHandler):
    """Base class for note body automations.

    An automation is one entry in the list that shows when the user types "/" in
    the note body. Canvas asks for the list one time per note load, then filters
    it in the browser as the user types. Canvas calls ``handle`` when the user
    selects the entry.

    Canvas puts the effects from ``handle`` on the line the user typed on, so a
    command from ``originate`` needs no ``line_number``.
    """

    RESPONDS_TO = [
        SHOW_AUTOMATIONS_EVENT,
        AUTOMATION_SELECTED_EVENT,
    ]

    AUTOMATION_KEY: str
    AUTOMATION_TITLE: str
    KEYWORDS: list[str] = []
    PRIORITY: int = 0

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Refuse a subclass that has no key or no title."""
        super().__init_subclass__(**kwargs)
        for attribute in ("AUTOMATION_KEY", "AUTOMATION_TITLE"):
            if not getattr(cls, attribute, None):
                raise ImproperlyConfigured(f"{cls.__name__!r} must define {attribute}.")

    @cached_property
    def note(self) -> Note | None:
        """The note that the user types in, or None (cached).

        The note type comes with the note, because ``visible`` usually scopes an
        automation by note type.
        """
        note_id = self.event.context.get("note_id")
        if not note_id:
            return None
        return Note.objects.filter(dbid=note_id).select_related("note_type_version").first()

    def visible(self) -> bool:
        """Return True to show this automation for the note in the event context."""
        return True

    @abstractmethod
    def handle(self) -> list[Effect]:
        """Return the effects to apply when the user selects this automation."""
        raise NotImplementedError("Implement to handle the automation selection")

    def compute(self) -> list[Effect]:
        """List this automation, or handle its selection."""
        if self.event.name == SHOW_AUTOMATIONS_EVENT:
            if not self.visible():
                return []
            return [
                ShowNoteBodyAutomationEffect(
                    key=self.AUTOMATION_KEY,
                    title=self.AUTOMATION_TITLE,
                    keywords=self.KEYWORDS,
                    priority=self.PRIORITY,
                ).apply()
            ]

        if self.event.context.get("key") == self.AUTOMATION_KEY:
            return self.handle()

        return []


__exports__ = (
    "AUTOMATION_SELECTED_EVENT",
    "SHOW_AUTOMATIONS_EVENT",
    "NoteBodyAutomation",
)
