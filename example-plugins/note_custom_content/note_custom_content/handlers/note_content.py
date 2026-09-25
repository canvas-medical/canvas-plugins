from canvas_sdk.effects import Effect
from canvas_sdk.effects.note_custom_content import NoteCustomContent
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from note_custom_content.sections import SCHEMA_KEYS

BASE_URL = "/plugin-io/api/note_custom_content"


class NoteContent(BaseHandler):
    """Points the note at the blocks this plugin serves.

    Each block is a page of its own rather than inline html, so it keeps a socket open and
    updates itself. The effect only says where to find it.
    """

    RESPONDS_TO = [EventType.Name(EventType.NOTE__GET_CUSTOM_CONTENT)]

    def compute(self) -> list[Effect]:
        """Name the summary above the note body, and a card for each section."""
        note_id = self.event.target.id

        effects = [NoteCustomContent(url=f"{BASE_URL}/banner?note_id={note_id}").apply()]

        effects.extend(
            NoteCustomContent(
                section=section,
                url=f"{BASE_URL}/section?note_id={note_id}&section={section.value}",
            ).apply()
            for section in SCHEMA_KEYS
        )

        return effects
