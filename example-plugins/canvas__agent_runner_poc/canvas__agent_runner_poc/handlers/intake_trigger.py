from canvas_sdk.effects import Effect
from canvas_sdk.effects.agent import RunAgentEffect
from canvas_sdk.events import EventType
from canvas_sdk.handlers.base import BaseHandler
from logger import log

# The plugin variable listing the channels intake runs on, such as "fax" or "fax, lab".
# Unset or empty, intake is off: every run sends a document to the model, so an operator
# chooses the channels rather than a fresh install running on uploads and lab feeds too.
CHANNELS_VARIABLE = "INTAKE_CHANNELS"

# Holds one entry once this process has said intake is off, so the log says it once.
_SAID_OFF: list[bool] = []


class DocumentIntakeTrigger(BaseHandler):
    """Starts the DocumentIntakeAgent on each document that arrives in the queue."""

    RESPONDS_TO: list[str] = [EventType.Name(EventType.DOCUMENT_RECEIVED)]

    def compute(self) -> list[Effect]:
        """Emit a run about the received document, one at a time per document.

        Only on the channels INTAKE_CHANNELS lists, read from the event's
        ``document.channel``; with none listed, intake is off.
        """
        listed = {
            channel.strip().lower()
            for channel in str(self.secrets.get(CHANNELS_VARIABLE) or "").split(",")
            if channel.strip()
        }
        if not listed:
            if not _SAID_OFF:
                _SAID_OFF.append(True)
                log.info(f"Document intake is off: {CHANNELS_VARIABLE} lists no channel.")
            return []
        channel = str((self.event.context.get("document") or {}).get("channel") or "").lower()
        if channel not in listed:
            return []
        return [
            RunAgentEffect(
                agent_id="canvas__agent_runner_poc.agents.intake:DocumentIntakeAgent",
                scope=RunAgentEffect.Scope.DOCUMENT,
                document_id=self.event.target.id,
            ).apply()
        ]
