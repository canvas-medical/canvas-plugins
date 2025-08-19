from datetime import datetime

from canvas_sdk.commands import PlanCommand
from canvas_sdk.effects import Effect
from canvas_sdk.effects.note.note import Note
from canvas_sdk.handlers.action_button import ActionButton
from canvas_sdk.v1.data.note import NoteType


class ButtonThree(ActionButton):
    """Third test: Note generation no UUID."""
    BUTTON_TITLE = "Note Creator 3"
    BUTTON_KEY = "NOTE_CREATOR_3"
    BUTTON_LOCATION = ActionButton.ButtonLocation.NOTE_HEADER

    def handle(self) -> list[Effect]:
        """
        Handle the button click event.
        """
        context = self.event.context

        # set the static UUID to the current time by minute
        note_uuid = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        note_type = NoteType.objects.get(name="Office visit")

        note_effect = Note(
            instance_id=None,
            note_type_id=note_type.id,
            datetime_of_service=datetime.datetime.now(),
            patient_id=context.patient_id,
            practice_location_id=context.practice_location_id,
            provider_id=context.provider_id,
            title=f"Note from plugin generated with static UUID {note_uuid}"
        )

        new_plan = PlanCommand(note_uuid=note_uuid, narrative='new plan! the time is ' + note_uuid )

        return [note_effect.create(), new_plan.originate()]
