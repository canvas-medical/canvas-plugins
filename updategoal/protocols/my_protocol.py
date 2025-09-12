from datetime import datetime

from canvas_sdk.commands import UpdateGoalCommand
from canvas_sdk.effects import Effect
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from canvas_sdk.v1.data import Command, Goal


class Protocol(BaseProtocol):
    """Protocol."""

    RESPONDS_TO = EventType.Name(EventType.GOAL_COMMAND__POST_COMMIT)

    def compute(self) -> list[Effect]:
        """Compute."""
        note_uuid = str(self.event.context["note"]["uuid"])
        command = Command.objects.get(id=str(self.event.target.id))
        goal_id = str(Goal.objects.get(dbid=command.anchor_object_dbid).id)
        nothing_provided = UpdateGoalCommand(
            note_uuid=note_uuid,
            goal_id=goal_id,
        )
        priority_provided = UpdateGoalCommand(
            note_uuid=note_uuid,
            goal_id=goal_id,
            priority=UpdateGoalCommand.Priority.LOW,
        )
        due_date_provided = UpdateGoalCommand(
            note_uuid=note_uuid,
            goal_id=goal_id,
            due_date=datetime(2026, 9, 1),
        )
        priority_and_due_date_provided = UpdateGoalCommand(
            note_uuid=note_uuid,
            goal_id=goal_id,
            priority=UpdateGoalCommand.Priority.LOW,
            due_date=datetime(2026, 9, 1),
        )
        return [
            nothing_provided.originate(),
            priority_provided.originate(),
            due_date_provided.originate(),
            priority_and_due_date_provided.originate(),
        ]
