from datetime import datetime

from canvas_sdk.effects import Effect
from canvas_sdk.effects.note.note import Note
from canvas_sdk.handlers.action_button import ActionButton
from canvas_sdk.v1.data.note import NoteType


class ButtonTwo(ActionButton):
    """Second test: Note generation no UUID."""
    BUTTON_TITLE = "Note Creator 2"
    BUTTON_KEY = "NOTE_CREATOR_2"
    BUTTON_LOCATION = ActionButton.ButtonLocation.NOTE_HEADER

    def handle(self) -> list[Effect]:
        """
        Handle the button click event.
        """
        context = self.event.context

        note_type = NoteType.objects.get(name="Office visit")

        note_effect = Note(
            note_type_id=note_type.id,
            datetime_of_service=datetime.datetime.now(),
            patient_id=context.patient_id,
            practice_location_id=context.practice_location_id,
            provider_id=context.provider_id,
            title="Note from plugin generated with no UUID"
        )



        return [note_effect.create()]
