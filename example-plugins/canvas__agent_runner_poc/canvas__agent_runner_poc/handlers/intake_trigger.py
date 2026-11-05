from canvas_sdk.effects import Effect
from canvas_sdk.effects.agent import RunAgentEffect
from canvas_sdk.events import EventType
from canvas_sdk.handlers.base import BaseHandler

# The plugin variable listing the channels intake runs on, such as "fax" or "fax, lab".
# Unset or empty runs intake on every channel.
CHANNELS_VARIABLE = "INTAKE_CHANNELS"


class DocumentIntakeTrigger(BaseHandler):
    """Starts the DocumentIntakeAgent on each document that arrives in the queue."""

    RESPONDS_TO: list[str] = [EventType.Name(EventType.DOCUMENT_RECEIVED)]

    def compute(self) -> list[Effect]:
        """Emit a run about the received document, one at a time per document.

        Only on the channels INTAKE_CHANNELS lists, when it lists any, read from the
        event's ``document.channel``.
        """
        listed = {
            channel.strip().lower()
            for channel in str(self.secrets.get(CHANNELS_VARIABLE) or "").split(",")
            if channel.strip()
        }
        channel = str((self.event.context.get("document") or {}).get("channel") or "").lower()
        if listed and channel not in listed:
            return []
        return [
            RunAgentEffect(
                agent_id="canvas__agent_runner_poc.agents.intake:DocumentIntakeAgent",
                scope=RunAgentEffect.Scope.DOCUMENT,
                document_id=self.event.target.id,
            ).apply()
        ]
