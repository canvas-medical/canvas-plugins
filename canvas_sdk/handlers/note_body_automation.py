import json
from abc import abstractmethod
from functools import cached_property
from typing import Any

from django.core.exceptions import ImproperlyConfigured

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects import Effect
from canvas_sdk.effects.note_body_automation import ShowNoteBodyAutomationEffect
from canvas_sdk.events import EventType
from canvas_sdk.handlers.base import BaseHandler
from canvas_sdk.v1.data import Note

SHOW_AUTOMATIONS_EVENT = EventType.Name(EventType.SHOW_NOTE_BODY_AUTOMATIONS)
AUTOMATION_SELECTED_EVENT = EventType.Name(EventType.NOTE_BODY_AUTOMATION_SELECTED)

ORIGINATE_EFFECT_PREFIX = "ORIGINATE_"

# The line_number that ``originate`` sends when the author gives no line. Canvas
# reads it as "after the last command in the body".
DEFAULT_LINE_NUMBER = -1


class NoteBodyAutomation(BaseHandler):
    """Base class for note body automations.

    An automation is one entry in the list that shows when the user types "/" in
    the note body. Canvas asks for the list one time per note load, then filters
    it in the browser as the user types. Canvas calls ``handle`` when the user
    selects the entry.

    A command from ``handle`` lands on the line the user typed on, and takes that
    line over the way a native command does. ``originate`` therefore needs no
    ``line_number``. An automation that wants the command somewhere else passes
    one, and it is kept.
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

    @property
    def line_number(self) -> int:
        """The note body line the user typed on, or -1 outside a selection."""
        return self.event.context.get("line_number", DEFAULT_LINE_NUMBER)

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
            return self._place_on_the_user_line(self.handle())

        return []

    def _place_on_the_user_line(self, effects: list[Effect]) -> list[Effect]:
        """Put the command originations in ``effects`` on the line the user typed on.

        An automation answers a keystroke, so its commands belong where the user
        was typing. ``originate`` defaults the line to ``DEFAULT_LINE_NUMBER``,
        which appends, and this fills the real line in. Canvas gives a command
        with a line the line itself, replacing what the user typed, so an author
        who chose a line keeps that placement. Any other effect is left alone.
        """
        if self.line_number == DEFAULT_LINE_NUMBER:
            return effects

        for effect in effects:
            if not EffectType.Name(effect.type).startswith(ORIGINATE_EFFECT_PREFIX):
                continue

            try:
                payload = json.loads(effect.payload)
            except ValueError:
                continue

            if not isinstance(payload, dict):
                continue

            if payload.get("line_number", DEFAULT_LINE_NUMBER) != DEFAULT_LINE_NUMBER:
                continue

            payload["line_number"] = self.line_number
            effect.payload = json.dumps(payload)

        return effects


__exports__ = (
    "AUTOMATION_SELECTED_EVENT",
    "DEFAULT_LINE_NUMBER",
    "SHOW_AUTOMATIONS_EVENT",
    "NoteBodyAutomation",
)
