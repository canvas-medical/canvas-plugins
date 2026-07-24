from canvas_sdk.commands.validation import CommandValidationErrorEffect
from canvas_sdk.effects import Effect
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from logger import log

REFILL_BLOCKED_MESSAGE = (
    "Refills can't be signed and sent from Canvas. Use your organization's refill workflow."
)


class BlockRefillCommit(BaseHandler):
    """
    Prevents a Refill command from being signed or sent.

    Both "Commit" and "Sign and send" on a refill run through
    REFILL_COMMAND__PRE_COMMIT; returning a CommandValidationErrorEffect aborts
    the commit and surfaces the message on the command. There is no SDK effect to
    hide the Sign-and-send button itself, so this gates the action instead. Add a
    condition here (inspect self.context, the patient, or the medication) to block
    selectively rather than every refill.
    """

    RESPONDS_TO = [
        EventType.Name(EventType.REFILL_COMMAND__PRE_COMMIT),
    ]

    def compute(self) -> list[Effect]:
        """Reject the refill commit with a validation message."""
        log.info(f"Blocking refill commit for command {self.event.target.id}")
        return [CommandValidationErrorEffect().add_error(REFILL_BLOCKED_MESSAGE).apply()]
