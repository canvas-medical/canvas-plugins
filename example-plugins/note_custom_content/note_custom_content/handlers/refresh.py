from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import Broadcast
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from canvas_sdk.v1.data.command import Command
from note_custom_content.sections import channel_for, counts_for

CHANGED_SUFFIXES = (
    "_COMMAND__POST_ORIGINATE",
    "_COMMAND__POST_DELETE",
    "_COMMAND__POST_ENTER_IN_ERROR",
)

COMMAND_CHANGED_EVENTS = [
    name
    for name in EventType.keys()  # noqa: SIM118
    if name.endswith(CHANGED_SUFFIXES)
]


class BroadcastCounts(BaseHandler):
    """Push a note's section counts out whenever its commands change.

    The cards hold their own numbers rather than re-reading the note, so the message
    carries the counts themselves and the browser has nothing to fetch.
    """

    RESPONDS_TO = COMMAND_CHANGED_EVENTS

    def compute(self) -> list[Effect]:
        """Broadcast the note's counts as they now stand."""
        note_id = (
            Command.objects.filter(id=self.event.target.id)
            .values_list("note__id", flat=True)
            .first()
        )

        if not note_id:
            return []

        return [
            Broadcast(
                channel=channel_for(str(note_id)),
                message={"event_type": "counts", "counts": counts_for(str(note_id))},
            ).apply()
        ]
