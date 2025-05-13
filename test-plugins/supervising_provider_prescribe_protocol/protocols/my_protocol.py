from canvas_sdk.commands import PrescribeCommand
from canvas_sdk.effects import Effect
from canvas_sdk.effects.protocol_card import ProtocolCard
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from canvas_sdk.v1.data import Staff
from logger import log


class Protocol(BaseProtocol):
    """
    This protocol responds to the NOTE_STATE_CHANGE_EVENT_CREATED event.

    It inserts a ProtocolCard containing a recommended Prescribe command. When the user triggers
    this command, the supervising provider field will be automatically populated.

    This plugin is primarily used to test and validate that the supervising provider is correctly
    set during command initialization from a protocol.
    """

    RESPONDS_TO = EventType.Name(EventType.NOTE_STATE_CHANGE_EVENT_CREATED)

    def compute(self) -> list[Effect]:
        """This method gets called when an event of the type RESPONDS_TO is fired."""
        log.info(f"Note {self.context['note_id']} on patient {self.context['patient_id']}")

        protocol_card = ProtocolCard(
            patient_id=self.context["patient_id"],
            key="test-supervising-provider-prescribe",
            title="Test Prescribe Command with Supervising Provider",
        )

        staff = Staff.objects.first()
        if not staff:
            log.warning("No staff found — skipping update.")
            return []

        prescribe_command = PrescribeCommand(
            supervising_provider_id=staff.id,
        )
        protocol_card.recommendations.append(
            prescribe_command.recommend(
                title="This inserts a prescribe command", button="Prescribe"
            )
        )

        return [protocol_card.apply()]
