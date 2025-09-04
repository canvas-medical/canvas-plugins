import json

from canvas_sdk.effects import Effect
from canvas_sdk.effects.note import Note as NoteEffect
from canvas_sdk.events import EventType
from canvas_sdk.handlers.base import BaseHandler
from canvas_sdk.utils.http import Http
from canvas_sdk.v1.data.command import Command
from canvas_sdk.v1.data.note import CurrentNoteStateEvent, NoteStates
from logger import log


class Handler(BaseHandler):
    """Renames Notes when locked using OpenAI and the contents of the Note."""

    RESPONDS_TO: list[str] = [
        EventType.Name(EventType.NOTE_STATE_CHANGE_EVENT_CREATED),
    ]

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        note_id: str | None = self.context.get("note_id")

        if not note_id:
            log.error("No note ID found in context")
            return []

        if not self.is_locked_note_event():
            return []

        new_title = self.get_note_title(note_id)

        if not new_title:
            return []

        return [NoteEffect(instance_id=note_id, title=new_title).update()]

    def get_note_title(self, note_id: str) -> str | None:
        """Get the new note title from the note."""
        headers = {
            "Authorization": f"Bearer {self.secrets.get('OPENAI_API_KEY')}",
            "Content-Type": "application/json",
        }
        payload = {
            "input": self.get_input(note_id),
            "instructions": self.get_instructions(),
            "model": self.get_model(),
            "temperature": 0,
        }
        response = Http().post(
            "https://api.openai.com/v1/responses", headers=headers, data=json.dumps(payload)
        )

        if not response.ok:
            log.error(
                f"Generate note title request failed: {response.status_code} - {response.text}"
            )
            return None

        response_json = response.json()

        new_title: str | None = None
        try:
            new_title = response_json.get("output")[0].get("content")[0].get("text")
        except Exception as e:
            log.error(f"Failed to get note title from response: {response.text} {e}")

        return new_title

    def get_model(self) -> str:
        """Get the OpenAI model to use."""
        return "gpt-4.1"

    def get_input(self, note_id: str) -> str:
        """Stringified commands within note to be used as input for OpenAI."""
        commands = Command.objects.filter(
            note__id=note_id, entered_in_error__isnull=True, committer__isnull=False
        )

        return json.dumps(list(commands.values("schema_key", "data")))

    def get_instructions(self) -> str:
        """Instructions for OpenAI to use to rename the note."""
        return """
        You are a clinical documentation specialist that generates a clinical note title using 10 words or less.
        This will read by a clinician looking to get a quick overview of the note.
        Return the exact title ONLY and nothing else.

        Examples:
        Ankle edema and amlodipine intolerance, medication change discussion
        Refilled metoprolol succinate ER and rosuvastatin 10 mg tablets
        Follow up call regarding elevated heart rate to 120
        Fall with back pain, unsteady gait, declined ER and HHA
        """

    def is_locked_note_event(self) -> bool:
        """Check if the note is locked."""
        return (
            CurrentNoteStateEvent.objects.values_list("state", flat=True).get(
                id=self.event.target.id
            )
            == NoteStates.LOCKED
        )
