from canvas_sdk.commands import PrescribeCommand
from canvas_sdk.effects import Effect
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from canvas_sdk.v1.data import Staff
from logger import log


class Protocol(BaseProtocol):
    """
    This protocol responds to the PRESCRIBE_COMMAND__POST_ORIGINATE event.

    It is used to test whether the supervising provider field is automatically populated
    when the Prescribe command is triggered. The protocol reacts to the command's creation
    and sets the field accordingly.

    The same logic can be tested for Refill and Adjust Prescription commands by updating
    the RESPONDS_TO event and the command class.
    """

    RESPONDS_TO = EventType.Name(EventType.PRESCRIBE_COMMAND__POST_ORIGINATE)

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        log.info(f"Target {self.target} on patient {self.context['patient']['id']}")

        staff = Staff.objects.first()
        if not staff:
            log.warning("No staff found — skipping update.")
            return []

        prescription = PrescribeCommand(
            command_uuid=str(self.target),
            supervising_provider_id=staff.id,
        )

        return [prescription.edit()]
