from abc import abstractmethod

from pydantic import ValidationError

from canvas_sdk.effects import Effect
from canvas_sdk.effects.note.appointment import Appointment
from canvas_sdk.effects.note.note import Note
from canvas_sdk.handlers.action_button import ActionButton
from canvas_sdk.v1.data.appointment import Appointment as AppointmentModel
from canvas_sdk.v1.data.note import Note as NoteModel
from logger import log

LOG_PREFIX = "[NSTL]"


class _TransitionButton(ActionButton):
    """Base class for note/appointment state transition buttons."""

    BUTTON_LOCATION = ActionButton.ButtonLocation.NOTE_FOOTER

    TRANSITION_LABEL: str = ""

    @abstractmethod
    def _build_transition_effect(self, note: NoteModel) -> Effect:
        """Build the SDK effect for this transition. May raise ValidationError."""
        raise NotImplementedError

    def handle(self) -> list[Effect]:
        note_dbid = self.context.get("note_id")
        if not note_dbid:
            log.info(f"{LOG_PREFIX} {self.TRANSITION_LABEL}: no note_id in context")
            return []
        note = NoteModel.objects.filter(dbid=note_dbid).first()
        if not note:
            log.info(f"{LOG_PREFIX} {self.TRANSITION_LABEL}: note dbid={note_dbid} not found")
            return []
        try:
            transition = self._build_transition_effect(note)
        except (ValidationError, ValueError) as exc:
            log.info(f"{LOG_PREFIX} {self.TRANSITION_LABEL} failed for note {note.id}: {exc}")
            return []
        log.info(f"{LOG_PREFIX} {self.TRANSITION_LABEL} transition applied for note {note.id}")
        return [transition]


class LockNoteButton(_TransitionButton):
    """Test button that locks the current note."""

    BUTTON_TITLE = "Test: Lock"
    BUTTON_KEY = "NSTL_LOCK"
    PRIORITY = 10
    TRANSITION_LABEL = "Lock"

    def _build_transition_effect(self, note: NoteModel) -> Effect:
        return Note(instance_id=str(note.id)).lock()


class UnlockNoteButton(_TransitionButton):
    """Test button that unlocks the current note."""

    BUTTON_TITLE = "Test: Unlock"
    BUTTON_KEY = "NSTL_UNLOCK"
    PRIORITY = 11
    TRANSITION_LABEL = "Unlock"

    def _build_transition_effect(self, note: NoteModel) -> Effect:
        return Note(instance_id=str(note.id)).unlock()


class SignNoteButton(_TransitionButton):
    """Test button that signs the current note."""

    BUTTON_TITLE = "Test: Sign"
    BUTTON_KEY = "NSTL_SIGN"
    PRIORITY = 12
    TRANSITION_LABEL = "Sign"

    def _build_transition_effect(self, note: NoteModel) -> Effect:
        return Note(instance_id=str(note.id)).sign()


class PushChargesNoteButton(_TransitionButton):
    """Test button that pushes charges for the current note."""

    BUTTON_TITLE = "Test: Push charges"
    BUTTON_KEY = "NSTL_PUSH_CHARGES"
    PRIORITY = 13
    TRANSITION_LABEL = "Push charges"

    def _build_transition_effect(self, note: NoteModel) -> Effect:
        return Note(instance_id=str(note.id)).push_charges()


class CheckInNoteButton(_TransitionButton):
    """Test button that checks in the current appointment note."""

    BUTTON_TITLE = "Test: Check in"
    BUTTON_KEY = "NSTL_CHECK_IN"
    PRIORITY = 14
    TRANSITION_LABEL = "Check in"

    def _build_transition_effect(self, note: NoteModel) -> Effect:
        return Note(instance_id=str(note.id)).check_in()


class NoShowNoteButton(_TransitionButton):
    """Test button that marks the current appointment note as a no-show."""

    BUTTON_TITLE = "Test: No show"
    BUTTON_KEY = "NSTL_NO_SHOW"
    PRIORITY = 15
    TRANSITION_LABEL = "No show"

    def _build_transition_effect(self, note: NoteModel) -> Effect:
        return Note(instance_id=str(note.id)).no_show()


class DeleteNoteButton(_TransitionButton):
    """Test button that deletes the current note."""

    BUTTON_TITLE = "Test: Delete"
    BUTTON_KEY = "NSTL_DELETE"
    PRIORITY = 16
    TRANSITION_LABEL = "Delete"

    def _build_transition_effect(self, note: NoteModel) -> Effect:
        return Note(instance_id=str(note.id)).delete()


class UndeleteNoteButton(_TransitionButton):
    """Test button that restores a deleted note."""

    BUTTON_TITLE = "Test: Restore"
    BUTTON_KEY = "NSTL_UNDELETE"
    PRIORITY = 17
    TRANSITION_LABEL = "Restore"

    def _build_transition_effect(self, note: NoteModel) -> Effect:
        return Note(instance_id=str(note.id)).undelete()


class DischargeNoteButton(_TransitionButton):
    """Test button that discharges the current inpatient note."""

    BUTTON_TITLE = "Test: Discharge"
    BUTTON_KEY = "NSTL_DISCHARGE"
    PRIORITY = 18
    TRANSITION_LABEL = "Discharge"

    def _build_transition_effect(self, note: NoteModel) -> Effect:
        return Note(instance_id=str(note.id)).discharge()


class CancelAppointmentButton(_TransitionButton):
    """Test button that cancels the appointment associated with the current note."""

    BUTTON_TITLE = "Test: Cancel appointment"
    BUTTON_KEY = "NSTL_CANCEL_APPOINTMENT"
    PRIORITY = 19
    TRANSITION_LABEL = "Cancel appointment"

    def _build_transition_effect(self, note: NoteModel) -> Effect:
        appointment = AppointmentModel.objects.filter(note=note).first()
        if not appointment:
            raise ValueError(f"No appointment found for note {note.id}.")
        return Appointment(instance_id=str(appointment.id)).cancel()


class RevertAppointmentButton(_TransitionButton):
    """Test button that reverts the appointment associated with the current note."""

    BUTTON_TITLE = "Test: Revert appointment"
    BUTTON_KEY = "NSTL_REVERT_APPOINTMENT"
    PRIORITY = 20
    TRANSITION_LABEL = "Revert appointment"

    def _build_transition_effect(self, note: NoteModel) -> Effect:
        appointment = AppointmentModel.objects.filter(note=note).first()
        if not appointment:
            raise ValueError(f"No appointment found for note {note.id}.")
        return Appointment(instance_id=str(appointment.id)).revert()
