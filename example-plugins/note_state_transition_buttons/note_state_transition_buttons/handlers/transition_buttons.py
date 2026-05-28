from abc import abstractmethod

from pydantic import ValidationError

from canvas_sdk.commands.commands.custom_command import CustomCommand
from canvas_sdk.effects import Effect
from canvas_sdk.effects.note.appointment import Appointment
from canvas_sdk.effects.note.note import Note
from canvas_sdk.handlers.action_button import ActionButton

LOG_SCHEMA_KEY = "note_state_transition_log"


def _log(note_uuid: str, message: str) -> Effect:
    return CustomCommand(
        note_uuid=note_uuid,
        schema_key=LOG_SCHEMA_KEY,
        content=message,
    ).originate(commit=True)


class _TransitionButton(ActionButton):
    BUTTON_LOCATION = ActionButton.ButtonLocation.NOTE_FOOTER

    TRANSITION_LABEL: str = ""

    @abstractmethod
    def _build_transition_effect(self, note_uuid: str) -> Effect:
        """Build the SDK effect for this transition. May raise ValidationError."""
        raise NotImplementedError

    def handle(self) -> list[Effect]:
        note_uuid = self.context.get("note_id")
        if not note_uuid:
            return []
        try:
            transition = self._build_transition_effect(note_uuid)
        except ValidationError as exc:
            return [_log(note_uuid, f"{self.TRANSITION_LABEL} failed validation: {exc}")]
        return [
            transition,
            _log(note_uuid, f"{self.TRANSITION_LABEL} transition applied."),
        ]


class LockNoteButton(_TransitionButton):
    BUTTON_TITLE = "Test: Lock"
    BUTTON_KEY = "NSTL_LOCK"
    PRIORITY = 10
    TRANSITION_LABEL = "Lock"

    def _build_transition_effect(self, note_uuid: str) -> Effect:
        return Note(instance_id=note_uuid).lock()


class UnlockNoteButton(_TransitionButton):
    BUTTON_TITLE = "Test: Unlock"
    BUTTON_KEY = "NSTL_UNLOCK"
    PRIORITY = 11
    TRANSITION_LABEL = "Unlock"

    def _build_transition_effect(self, note_uuid: str) -> Effect:
        return Note(instance_id=note_uuid).unlock()


class SignNoteButton(_TransitionButton):
    BUTTON_TITLE = "Test: Sign"
    BUTTON_KEY = "NSTL_SIGN"
    PRIORITY = 12
    TRANSITION_LABEL = "Sign"

    def _build_transition_effect(self, note_uuid: str) -> Effect:
        return Note(instance_id=note_uuid).sign()


class PushChargesNoteButton(_TransitionButton):
    BUTTON_TITLE = "Test: Push charges"
    BUTTON_KEY = "NSTL_PUSH_CHARGES"
    PRIORITY = 13
    TRANSITION_LABEL = "Push charges"

    def _build_transition_effect(self, note_uuid: str) -> Effect:
        return Note(instance_id=note_uuid).push_charges()


class CheckInNoteButton(_TransitionButton):
    BUTTON_TITLE = "Test: Check in"
    BUTTON_KEY = "NSTL_CHECK_IN"
    PRIORITY = 14
    TRANSITION_LABEL = "Check in"

    def _build_transition_effect(self, note_uuid: str) -> Effect:
        return Note(instance_id=note_uuid).check_in()


class NoShowNoteButton(_TransitionButton):
    BUTTON_TITLE = "Test: No show"
    BUTTON_KEY = "NSTL_NO_SHOW"
    PRIORITY = 15
    TRANSITION_LABEL = "No show"

    def _build_transition_effect(self, note_uuid: str) -> Effect:
        return Note(instance_id=note_uuid).no_show()


class DeleteNoteButton(_TransitionButton):
    BUTTON_TITLE = "Test: Delete"
    BUTTON_KEY = "NSTL_DELETE"
    PRIORITY = 16
    TRANSITION_LABEL = "Delete"

    def _build_transition_effect(self, note_uuid: str) -> Effect:
        return Note(instance_id=note_uuid).delete()


class UndeleteNoteButton(_TransitionButton):
    BUTTON_TITLE = "Test: Restore"
    BUTTON_KEY = "NSTL_UNDELETE"
    PRIORITY = 17
    TRANSITION_LABEL = "Restore"

    def _build_transition_effect(self, note_uuid: str) -> Effect:
        return Note(instance_id=note_uuid).undelete()


class DischargeNoteButton(_TransitionButton):
    BUTTON_TITLE = "Test: Discharge"
    BUTTON_KEY = "NSTL_DISCHARGE"
    PRIORITY = 18
    TRANSITION_LABEL = "Discharge"

    def _build_transition_effect(self, note_uuid: str) -> Effect:
        return Note(instance_id=note_uuid).discharge()


class CancelAppointmentButton(_TransitionButton):
    BUTTON_TITLE = "Test: Cancel appointment"
    BUTTON_KEY = "NSTL_CANCEL_APPOINTMENT"
    PRIORITY = 19
    TRANSITION_LABEL = "Cancel appointment"

    def _build_transition_effect(self, note_uuid: str) -> Effect:
        return Appointment(instance_id=note_uuid).cancel()


class RevertAppointmentButton(_TransitionButton):
    BUTTON_TITLE = "Test: Revert appointment"
    BUTTON_KEY = "NSTL_REVERT_APPOINTMENT"
    PRIORITY = 20
    TRANSITION_LABEL = "Revert appointment"

    def _build_transition_effect(self, note_uuid: str) -> Effect:
        return Appointment(instance_id=note_uuid).revert()
