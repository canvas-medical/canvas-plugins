import json

from canvas_sdk.commands import PrescribeCommand
from canvas_sdk.commands.commands.prescribe import CompoundMedicationData
from canvas_sdk.commands.constants import ClinicalQuantity
from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from canvas_sdk.v1.data import Command
from canvas_sdk.v1.data.compound_medication import CompoundMedication
from canvas_sdk.v1.data.compound_medication import CompoundMedication as CompoundMedicationModel
from logger import log


# Inherit from BaseProtocol to properly get registered for events
class Handle(BaseHandler):
    """Handler for prescribe command available actions events."""

    RESPONDS_TO = EventType.Name(EventType.PRESCRIBE_COMMAND__AVAILABLE_ACTIONS)

    def compute(self) -> list[Effect]:
        """Compute available actions based on command state and signature."""
        c = Command.objects.get(id=self.target)

        actions = self.context["actions"]
        log.info(f"################# {actions}")

        if c.state == "staged":
            if c.data["sig"] == "NO CARRY FORWARD":
                actions = self.context["actions"]
                payload = [action for action in actions if action["name"] != "carry_forward"]

                return [
                    Effect(
                        type=EffectType.COMMAND_AVAILABLE_ACTIONS_RESULTS,
                        payload=json.dumps(payload),
                    )
                ]

            if c.data["sig"] == "NO AUDIT":
                actions = self.context["actions"]
                payload = [action for action in actions if action["name"] != "audit"]

                return [
                    Effect(
                        type=EffectType.COMMAND_AVAILABLE_ACTIONS_RESULTS,
                        payload=json.dumps(payload),
                    )
                ]

            if c.data["sig"] == "REORDER":
                actions = self.context["actions"]
                payload = [actions[1], actions[0]]

                return [
                    Effect(
                        type=EffectType.COMMAND_AVAILABLE_ACTIONS_RESULTS,
                        payload=json.dumps(payload),
                    )
                ]

        if c.state == "in_review":
            if c.data["sig"] == "NO CHANGES":
                actions = self.context["actions"]
                payload = [action for action in actions if action["name"] != "make_changes"]

                return [
                    Effect(
                        type=EffectType.COMMAND_AVAILABLE_ACTIONS_RESULTS,
                        payload=json.dumps(payload),
                    )
                ]

            if c.data["sig"] == "ONLY SIGN":
                actions = self.context["actions"]
                payload = [action for action in actions if action["name"] == "sign_action"]

                return [
                    Effect(
                        type=EffectType.COMMAND_AVAILABLE_ACTIONS_RESULTS,
                        payload=json.dumps(payload),
                    )
                ]

        return []


class HandleThree(BaseHandler):
    """Third handler for prescribe command available actions events."""

    RESPONDS_TO = EventType.Name(EventType.PRESCRIBE_COMMAND__AVAILABLE_ACTIONS)

    def compute(self) -> list[Effect]:
        """Filter available actions for specific patient and command state."""
        cmd = Command.objects.get(id=self.target)
        actions = self.context["actions"]

        if cmd.note.patient.id == "7c81b0768ccf4938be3df1d5c7a97369" and cmd.state == "in_review":
            actions = [
                action
                for action in actions
                if action["name"] == "sign_action" or action["name"] == "make_changes"
            ]

        return [
            Effect(type=EffectType.COMMAND_AVAILABLE_ACTIONS_RESULTS, payload=json.dumps(actions))
        ]


class HandleTwo(BaseHandler):
    """Handler for history of present illness command post-update events."""

    RESPONDS_TO = EventType.Name(EventType.HISTORY_OF_PRESENT_ILLNESS_COMMAND__POST_UPDATE)

    def compute(self) -> list[Effect]:
        """Create prescribe commands based on narrative content."""
        narrative = self.context["fields"]["narrative"]

        if narrative == "empty":
            p = PrescribeCommand()
            p.note_uuid = self.event.context["note"]["uuid"]
            return [p.originate()]

        if narrative == "fdb code":
            command = PrescribeCommand(
                note_uuid=self.event.context["note"]["uuid"],
                fdb_code="216092",
                icd10_codes=["R51"],
                sig="Take one tablet daily after meals",
                days_supply=30,
                quantity_to_dispense=30,
                type_to_dispense=ClinicalQuantity(
                    representative_ndc="12843016128", ncpdp_quantity_qualifier_code="C48542"
                ),
                refills=3,
                substitutions=PrescribeCommand.Substitutions.ALLOWED,
                pharmacy="1655458",
                prescriber_id="provider_123",
                supervising_provider_id="provider_456",
                note_to_pharmacist="Please verify patient's insurance before processing.",
            )

            return [command.originate()]

        if narrative == "existing compound":
            # Get an existing compound medication (let's assume it exists in the database)
            compound_med = CompoundMedicationModel.objects.filter(active=True).first()

            command = PrescribeCommand(
                note_uuid=self.event.context["note"]["uuid"],
                compound_medication_id=str(compound_med.id),
                icd10_codes=["R51"],
                sig="Take one tablet daily after meals",
                days_supply=30,
                quantity_to_dispense=30,
                type_to_dispense=ClinicalQuantity(
                    representative_ndc="12843016128", ncpdp_quantity_qualifier_code="C48542"
                ),
                refills=3,
                substitutions=PrescribeCommand.Substitutions.ALLOWED,
                pharmacy="1655458",
                prescriber_id="provider_123",
                supervising_provider_id="provider_456",
                note_to_pharmacist="Please verify patient's insurance before processing.",
            )

            return [command.originate()]

        if narrative == "new compound":
            compound_medication_data = CompoundMedicationData(
                formulation="Testosterone 200mg/mL in Grapeseed Oil",
                potency_unit_code=CompoundMedication.PotencyUnits.GRAM,
                controlled_substance=CompoundMedication.ControlledSubstanceOptions.SCHEDULE_III,
                controlled_substance_ndc="12345678901",
                active=True,
            )

            command = PrescribeCommand(
                note_uuid=self.event.context["note"]["uuid"],
                compound_medication_data=compound_medication_data,
                icd10_codes=["M79.3"],
                sig="Apply thin layer to affected area twice daily",
                days_supply=30,
                quantity_to_dispense=30,
                type_to_dispense=ClinicalQuantity(
                    representative_ndc="12843016128", ncpdp_quantity_qualifier_code="C48542"
                ),
                refills=3,
                substitutions=PrescribeCommand.Substitutions.ALLOWED,
                pharmacy="1655458",
                prescriber_id="provider_123",
                supervising_provider_id="provider_456",
                note_to_pharmacist="Please verify patient's insurance before processing.",
            )

            return [command.originate()]

        return []
