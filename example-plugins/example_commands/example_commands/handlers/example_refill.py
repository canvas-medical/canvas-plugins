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

    REFILL_COMMAND__POST_VALIDATION runs each time the refill is validated in
    the note. Returning a CommandValidationErrorEffect disables the command's
    REVIEW button, so Sign and send, Sign, and Print can't be reached; the
    message shows as a tooltip on the disabled button. The block applies in the
    note UI only. There is no SDK effect to hide the Sign-and-send button itself,
    so this gates the action instead. Add a condition here (inspect
    self.context, the patient, or the medication) to block selectively rather
    than every refill.

    REFILL_COMMAND__PRE_COMMIT does not work for this: the refill sign actions
    dispatch pre-commit events robustly, so a validation error returned there is
    ignored and the refill commits.
    """

    RESPONDS_TO = [
        EventType.Name(EventType.REFILL_COMMAND__POST_VALIDATION),
    ]

    def compute(self) -> list[Effect]:
        """Reject the refill with a validation message."""
        log.info(f"Blocking refill commit for command {self.event.target.id}")
        return [CommandValidationErrorEffect().add_error(REFILL_BLOCKED_MESSAGE).apply()]
