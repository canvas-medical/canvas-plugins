from canvas_sdk.commands.constants import CodeSystems
from canvas_sdk.effects import Effect
from canvas_sdk.effects.billing_line_item import AddBillingLineItem
from canvas_sdk.events import EventType
from canvas_sdk.handlers.base import BaseHandler
from canvas_sdk.v1.data.command import Command
from logger import log


class AddBillingLineItemToAutismDiagnoses(BaseHandler):
    """
    Handler that automatically creates billing line items for newly committed autism diagnosis conditions.

    This handler responds to DIAGNOSE_COMMAND__POST_COMMIT events and checks if the diagnosis
    has an ICD-10 coding for autism screening (Z13.41). When detected, it creates a billing
    line item with CPT code "AUTISM_DX" linked to the latest assessment for the diagnosis.

    Triggers on: DIAGNOSE_COMMAND__POST_COMMIT events
    Effects: Creates AddBillingLineItem for autism screening diagnoses
    """

    RESPONDS_TO = EventType.Name(EventType.DIAGNOSE_COMMAND__POST_COMMIT)

    def compute(self) -> list[Effect]:
        """
        Process the DIAGNOSE_COMMAND__POST_COMMIT event and create billing line item if appropriate.

        Returns:
            list[Effect]: List containing AddBillingLineItem effect if autism diagnosis detected,
                         empty list otherwise.
        """
        try:
            # Get the command that was committed
            command = Command.objects.get(id=self.event.target.id)

            # Get the diagnosis (condition) that was created/updated by this command
            diagnosis = command.anchor_object
            if not diagnosis:
                log.debug(f"No anchor object found for command {command.id}")
                return []

            # Check if this diagnosis has ICD-10 coding for autism screening (Z13.41)
            icd_10_coding = diagnosis.codings.filter(system=CodeSystems.ICD10).first()
            if not icd_10_coding:
                log.debug(f"No ICD-10 coding found for diagnosis {diagnosis.id}")
                return []

            # Remove dots from ICD-10 code and check if it matches Z1341 (Z13.41 without dots)
            icd_code_normalized = icd_10_coding.code.replace('.', '')
            if icd_code_normalized != 'Z1341':
                log.debug(f"ICD-10 code {icd_code_normalized} is not Z1341, skipping billing line item creation")
                return []

            # Get the note that the command was performed in
            note = command.note
            if not note:
                log.error(f"No note found for command {command.id}")
                return []

            # Get the latest assessment for this diagnosis
            latest_assessment = diagnosis.assessments.last()
            if not latest_assessment:
                log.warning(f"No assessments found for diagnosis {diagnosis.id}")
                assessment_ids = []
            else:
                assessment_ids = [str(latest_assessment.id)]

            # Create the billing line item for autism diagnosis
            billing_line_item = AddBillingLineItem(
                note_id=str(note.id),
                cpt="AUTISM_DX",
                assessment_ids=assessment_ids,
            )

            applied_effect = billing_line_item.apply()

            log.info(
                f"Created billing line item for autism diagnosis (ICD-10: {icd_10_coding.code}) "
                f"in note {note.id} with CPT code AUTISM_DX"
            )

            return [applied_effect]

        except Command.DoesNotExist:
            log.error(f"Command with id {self.event.target.id} not found")
            return []
        except Exception as e:
            log.error(f"Error processing autism diagnosis billing for command {self.event.target.id}: {str(e)}")
            return []
