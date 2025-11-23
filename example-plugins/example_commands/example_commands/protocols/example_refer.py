from canvas_sdk.effects import Effect
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from canvas_sdk.commands.commands.refer import ReferCommand
from canvas_sdk.commands.constants import ServiceProvider
from logger import log
from random import choices

class AutoPopulateReferCommand(BaseProtocol):
    """
    Protocol that automatically populates a refer command when a referral command is originated.
    """
    RESPONDS_TO = [
        EventType.Name(EventType.REFER_COMMAND__POST_ORIGINATE),
    ]

    def compute(self) -> list[Effect]:
        priority_options = [    
            ReferCommand.Priority.URGENT,
            ReferCommand.Priority.ROUTINE,
            ReferCommand.Priority.STAT,
            None
        ]
        priority = choices(priority_options)[0]
        log.info(f"Automatically populating a refer command for {self.target} with priority {priority}")
        return [
            ReferCommand(
                command_uuid=self.target,
                diagnosis_codes=["E119"],
                priority=priority,
                clinical_question=ReferCommand.ClinicalQuestion.DIAGNOSTIC_UNCERTAINTY,
                comment="this is a comment",
                notes_to_specialist="This is a note to specialist",
                include_visit_note=True,
                service_provider=ServiceProvider(
                    first_name="Clinic",
                    last_name="Acupuncture",
                    practice_name="Clinic Acupuncture",
                    specialty="Acupuncture",
                    business_address="Street Address",
                    business_phone="1234569874",
                    business_fax="1234569874"
                )
            ).edit()
        ]