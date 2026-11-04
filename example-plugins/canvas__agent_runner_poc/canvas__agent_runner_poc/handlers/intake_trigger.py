from canvas_sdk.effects import Effect
from canvas_sdk.effects.agent import RunAgentEffect
from canvas_sdk.events import EventType
from canvas_sdk.handlers.base import BaseHandler


class DocumentIntakeTrigger(BaseHandler):
    """Starts the DocumentIntakeAgent on each document that arrives in the queue."""

    RESPONDS_TO: list[str] = [EventType.Name(EventType.DOCUMENT_RECEIVED)]

    def compute(self) -> list[Effect]:
        """Emit a run about the received document, one at a time per document."""
        return [
            RunAgentEffect(
                agent_id="canvas__agent_runner_poc.agents.intake:DocumentIntakeAgent",
                scope=RunAgentEffect.Scope.DOCUMENT,
                document_id=self.event.target.id,
            ).apply()
        ]
