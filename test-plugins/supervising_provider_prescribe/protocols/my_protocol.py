from canvas_generated.messages.effects_pb2 import Effect
from canvas_sdk.commands import PrescribeCommand
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from logger import log


class Protocol(BaseProtocol):
    """
    This protocol responds to the PRESCRIBE_COMMAND__POST_ORIGINATE event.
    When a prescribe command is created, protocol will be triggered and fill in the supervising provider field.
    """

    RESPONDS_TO = EventType.Name(EventType.PRESCRIBE_COMMAND__POST_ORIGINATE)

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        log.info(f"Target {self.target} on patient {self.context['patient']['id']}")

        prescription = PrescribeCommand(
            command_uuid=str(self.target),
            supervising_provider_id="4150cd20de8a470aa570a852859ac87e",
        )

        return [prescription.edit()]
