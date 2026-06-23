from canvas_sdk.effects import Effect
from canvas_sdk.effects.note_header_assignee_options import (
    AssigneeOption,
    AssigneeType,
    NoteHeaderAssigneeOptions,
)
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler


class Handler(BaseHandler):
    """Reorders the note header assignee dropdown so teams are listed before individuals."""

    RESPONDS_TO = EventType.Name(EventType.PATIENT_NOTE_HEADER_ASSIGNEE__POST_SEARCH)

    def compute(self) -> list[Effect]:
        """Surface teams first, then staff; omitting a candidate hides it."""
        candidates = self.context.get("results") or []

        teams = [c for c in candidates if c["type"] == AssigneeType.TEAM.value]
        staff = [c for c in candidates if c["type"] == AssigneeType.STAFF.value]

        options = [
            AssigneeOption(id=candidate["id"], type=AssigneeType(candidate["type"]))
            for candidate in (*teams, *staff)
        ]

        return [NoteHeaderAssigneeOptions(options=options).apply()]
