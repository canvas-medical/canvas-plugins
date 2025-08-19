import uuid
from datetime import datetime

from canvas_sdk.commands import PlanCommand
from canvas_sdk.effects import Effect
from canvas_sdk.effects.note.note import Note
from canvas_sdk.handlers.action_button import ActionButton
from canvas_sdk.v1.data.note import NoteType


class ButtonOne(ActionButton):
    """First test: Note UUID generation."""
    BUTTON_TITLE = "Note Creator 1"
    BUTTON_KEY = "NOTE_CREATOR_1"
    BUTTON_LOCATION = ActionButton.ButtonLocation.NOTE_HEADER

    def handle(self) -> list[Effect]:
        """
        Handle the button click event.
        """
        context = self.event.context
        note_uuid = uuid.uuid4()

        note_type = NoteType.objects.get(name="Office visit")

        note_effect = Note(
            instance_id=note_uuid,
            note_type_id=note_type.id,
            datetime_of_service=datetime.datetime.now(),
            patient_id=context.patient_id,
            practice_location_id=context.practice_location_id,
            provider_id=context.provider_id,
            title=f"Note - {note_uuid} from plugin generated UUID"
        )

        new_plan = PlanCommand(note_uuid=note_uuid, narrative='new plan!')

        return [note_effect.create(), new_plan.originate()]
