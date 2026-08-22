from functools import cached_property
from typing import Any

from django.core.exceptions import ImproperlyConfigured

from canvas_sdk.effects import Effect
from canvas_sdk.effects.note_body_automation import ShowNoteBodyAutomationEffect
from canvas_sdk.events import EventType
from canvas_sdk.handlers.surface_entry import PluginSurfaceEntry
from canvas_sdk.v1.data import Note

# The line Canvas reads as "after the last command in the body".
APPEND_AFTER_LAST_COMMAND = -1


class NoteBodyAutomation(PluginSurfaceEntry):
    """Base class for note body automations.

    An automation is one entry in the list that shows when the user types "/" in
    the note body. Canvas asks for the list one time per note load, then filters
    it in the browser as the user types. Canvas calls ``handle`` when the user
    selects the entry.

    ``line_number`` is the line the user typed on. A command given that line takes
    it over, replacing what the user typed, the way a native command does::

        def handle(self) -> list[Effect]:
            return [
                PlanCommand(note_uuid=..., narrative="...").originate(
                    line_number=self.line_number
                )
            ]

    A command with no line appends after the last command in the body instead.
    """

    RESPONDS_TO = [
        EventType.Name(EventType.SHOW_NOTE_BODY_AUTOMATIONS),
        EventType.Name(EventType.NOTE_BODY_AUTOMATION_SELECTED),
    ]

    AUTOMATION_KEY: str
    AUTOMATION_TITLE: str
    KEYWORDS: list[str] = []

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
        return self.event.context.get("line_number", APPEND_AFTER_LAST_COMMAND)

    @property
    def entry_key(self) -> str:
        """The key Canvas sends back when the user selects this automation."""
        return self.AUTOMATION_KEY

    def is_list_event(self) -> bool:
        """Whether Canvas is collecting the automations for a note."""
        return self.event.name == EventType.Name(EventType.SHOW_NOTE_BODY_AUTOMATIONS)

    def shows_this_entry(self) -> bool:
        """The note body is one surface, so its list event always asks for this."""
        return True

    def entry_effect(self) -> Effect:
        """The effect that puts this automation in the note body command list."""
        return ShowNoteBodyAutomationEffect(
            key=self.AUTOMATION_KEY,
            title=self.AUTOMATION_TITLE,
            keywords=self.KEYWORDS,
            priority=self.PRIORITY,
        ).apply()


__exports__ = ("APPEND_AFTER_LAST_COMMAND", "NoteBodyAutomation")
