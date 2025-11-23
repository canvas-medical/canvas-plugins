from random import choices

from canvas_sdk.commands import ImagingOrderCommand
from canvas_sdk.commands.constants import ServiceProvider
from canvas_sdk.effects import Effect
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from logger import log


class AutoPopulateImagingOrderCommand(BaseProtocol):
    """
    Protocol that automatically enriches imaging orders right after they are originated.
    """

    RESPONDS_TO = [
        EventType.Name(EventType.IMAGING_ORDER_COMMAND__POST_ORIGINATE),
    ]

    def compute(self) -> list[Effect]:
        log.info(f"Enriching imaging order command {self.target}")

        priorities = [
            ImagingOrderCommand.Priority.ROUTINE,
            ImagingOrderCommand.Priority.URGENT,
            ImagingOrderCommand.Priority.STAT,
            None,
        ]

        priority = choices(priorities)[0]

        return [
            ImagingOrderCommand(
                command_uuid=self.target,
                image_code="G0204",
                diagnosis_codes=["E119"],
                priority=priority,
                additional_details="Auto-populated imaging order details",
                comment="Example comment for imaging order",
                service_provider=ServiceProvider(
                    first_name="Clinic",
                    last_name="Imaging",
                    practice_name="Clinic Imaging",
                    specialty="Radiology",
                    business_address="123 Imaging St",
                    business_phone="1234569874",
                    business_fax="1234569874",
                ),
            ).edit()
        ]

