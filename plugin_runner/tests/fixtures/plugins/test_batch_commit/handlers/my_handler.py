from canvas_sdk.commands import AssessCommand, PlanCommand
from canvas_sdk.effects import Effect
from canvas_sdk.effects.batch_commit import BatchCommitCommandEffect
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler


class MyHandler(BaseHandler):
    """Test handler that returns a BatchCommitCommandEffect."""

    RESPONDS_TO = EventType.Name(EventType.UNKNOWN)

    def compute(self) -> list[Effect]:
        """Return a batch commit effect with two commands."""
        commands = [
            PlanCommand(command_uuid="cmd-001"),
            AssessCommand(command_uuid="cmd-002"),
        ]
        return [BatchCommitCommandEffect(commands=commands).apply()]
