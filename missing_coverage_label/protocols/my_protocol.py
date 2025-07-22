
import json

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.note import RemoveAppointmentLabel
from canvas_sdk.effects.note.appointment import AddAppointmentLabel
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from logger import log
from canvas_sdk.v1.data import AppointmentLabel


class Protocol(BaseProtocol):
    """You should put a helpful description of this protocol's behavior here."""

    RESPONDS_TO = EventType.Name(EventType.APPOINTMENT_CREATED)

    def compute(self) -> list[Effect]:

        # TEST TO FETCH ALL AVAILABLE LABELS FROM HOME-APP SERVICE --> PASSED
        # all_labels = AppointmentLabel.objects.all()
        # log.info(f"Found {len(all_labels)} appointment labels in total.")
        # for label in all_labels:
        #     log.info(
        #         f"  Label ID: {label.id}, Name: {label.name}, Color: {label.color}, Active: {label.active}"
        #     )


        #---------------------------------------------------------------------
        # TEST TO ADD LABEL FOR SPECIFIC APPOINTMENT, FOR THIS WE NEED TO HARDCODE THE APPOINTMENT_ID (7c39862e-3b02-4d25-b474-2ffa3cf9af5a)
        # appointment_id = "7c39862e-3b02-4d25-b474-2ffa3cf9af5a"
        # # The list of labels you want to add.
        # labels_to_add = ["High Priority", "Follow-up Required", "Low Priority"]
        # try:
        #     # 1. Create an instance of the AddAppointmentLabel effect class.
        #     add_label_effect_instance = AddAppointmentLabel(
        #         appointment_id=appointment_id,
        #         labels=labels_to_add,
        #     )
        #
        #     # 2. Call the .apply() method to generate the final Effect object.
        #     # This automatically runs the validation logic (like the 3-label limit)
        #     effect = add_label_effect_instance.apply()
        #     log.info(f"Effect in all of its glory:  {effect}")
        #     return [effect]
        # except Exception as e:
        #     log.error(f"Failed to create AddAppointmentLabel effect: {e}")
        #     return []

        # ---------------------------------------------------------------------
        # TEST TO REMOVE THE EXISTING LABEL
        appointment_id = "7c39862e-3b02-4d25-b474-2ffa3cf9af5a"
        # The list of labels you want to add.
        labels_to_remove = ["High Priority"]
        try:
            # 1. Create an instance of the AddAppointmentLabel effect class.
            remove_label_effect_instance = RemoveAppointmentLabel(
                appointment_id=appointment_id,
                labels=labels_to_remove,
            )

            # 2. Call the .apply() method to generate the final Effect object.
            # This automatically runs the validation logic (like the 3-label limit)
            effect = remove_label_effect_instance.apply()
            log.info(f"Effect in all of its glory:  {effect}")
            return [effect]
        except Exception as e:
            log.error(f"Failed to create RemoveAppointmentLabel effect: {e}")
            return []

