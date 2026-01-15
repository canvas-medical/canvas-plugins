import datetime
import json
from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects import Effect
from canvas_sdk.effects.note.base import NoteOrAppointmentABC
from canvas_sdk.v1.data import Note as NoteModel
from canvas_sdk.v1.data import NoteType, Patient
from canvas_sdk.v1.data.note import NoteStates, NoteTypeCategories

TRANSITION_STATE_MATRIX = {
    NoteStates.NEW: [NoteStates.LOCKED, NoteStates.PUSHED],
    NoteStates.LOCKED: [NoteStates.SIGNED, NoteStates.UNLOCKED],
    NoteStates.UNLOCKED: [NoteStates.LOCKED, NoteStates.PUSHED],
    NoteStates.SIGNED: [NoteStates.UNLOCKED, NoteStates.SIGNED],
    NoteStates.PUSHED: [NoteStates.LOCKED, NoteStates.PUSHED],
}

ACTION_STATE_MATRIX = {
    "lock": NoteStates.LOCKED,
    "unlock": NoteStates.UNLOCKED,
    "sign": NoteStates.SIGNED,
    "push_charges": NoteStates.PUSHED,
    "check_in": NoteStates.CONVERTED,
    "no_show": NoteStates.NOSHOW,
}


class Note(NoteOrAppointmentABC):
    """
    Effect to create a visit note.

    Attributes:
        note_type_id (UUID | str): The ID of the note type.
        datetime_of_service (datetime.datetime): The date and time of the service.
        patient_id (str): The ID of the patient.
    """

    class Meta:
        effect_type = "NOTE"

    note_type_id: UUID | str | None = None
    datetime_of_service: datetime.datetime | None = None
    patient_id: str | None = None
    title: str | None = None

    def push_charges(self) -> Effect:
        """Pushes BillingLineItems from the Note to the associated Claim. Identicial to clicking the Push Charges button in the note footer."""
        self._validate_before_effect("push_charges")
        return Effect(
            type=EffectType.PUSH_NOTE_CHARGES,
            payload=json.dumps({"data": {"note": str(self.instance_id)}}),
        )

    def unlock(self) -> Effect:
        """Unlocks the note to allow further edits."""
        self._validate_before_effect("unlock")
        return Effect(
            type=EffectType.UNLOCK_NOTE,
            payload=json.dumps({"data": {"note": str(self.instance_id)}}),
        )

    def lock(self) -> Effect:
        """Locks the note to prevent further edits."""
        self._validate_before_effect("lock")
        return Effect(
            type=EffectType.LOCK_NOTE,
            payload=json.dumps({"data": {"note": str(self.instance_id)}}),
        )

    def sign(self) -> Effect:
        """Signs the note."""
        self._validate_before_effect("sign")
        return Effect(
            type=EffectType.SIGN_NOTE,
            payload=json.dumps({"data": {"note": str(self.instance_id)}}),
        )

    def check_in(self) -> Effect:
        """Mark the note as checked-in."""
        self._validate_before_effect("check_in")
        return Effect(
            type=EffectType.CHECK_IN_NOTE,
            payload=json.dumps({"data": {"note": str(self.instance_id)}}),
        )

    def no_show(self) -> Effect:
        """Mark the note as no-show."""
        self._validate_before_effect("no_show")
        return Effect(
            type=EffectType.NO_SHOW_NOTE,
            payload=json.dumps({"data": {"note": str(self.instance_id)}}),
        )

    def _validate_state_transition(
        self, note: NoteModel, next_state: NoteStates
    ) -> tuple[bool, InitErrorDetails | None]:
        """Validates state transitions for the note."""
        current_state = note.current_state.state if note.current_state else None

        if not current_state:
            return False, self._create_error_detail(
                "value", "Unsupported state transitions", next_state
            )

        is_sig_required = note.note_type_version.is_sig_required
        if next_state == NoteStates.SIGNED and not is_sig_required:
            return False, self._create_error_detail(
                "value", "Cannot sign a note that does not require a signature.", next_state
            )

        if (
            next_state == NoteStates.CONVERTED or next_state == NoteStates.NOSHOW
        ) and note.note_type_version.category != NoteTypeCategories.APPOINTMENT:
            return False, self._create_error_detail(
                "value",
                "Only appointments can be checked in or marked as no-show.",
                next_state,
            )

        return True, None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """
        Validates the note type category and returns a list of error details if validation fails.

        Args:
            method (Any): The method being validated.

        Returns:
            list[InitErrorDetails]: A list of error details for invalid note type categories.
        """
        errors = super()._get_error_details(method)

        if method in ACTION_STATE_MATRIX:
            if not self.instance_id:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'instance_id' is required.",
                        None,
                    )
                )
                return errors
            elif not (note := NoteModel.objects.filter(id=self.instance_id).first()):
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Note with ID {self.instance_id} does not exist.",
                        self.instance_id,
                    )
                )
                return errors

            if note.note_type_version.category in (
                NoteTypeCategories.LETTER,
                NoteTypeCategories.MESSAGE,
            ):
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Note with note type {note.note_type_version.name} cannot perform action '{method}'.",
                        note.note_type_version,
                    )
                )
                return errors

            if method == "push_charges" and (
                not note.note_type_version or not note.note_type_version.is_billable
            ):
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Note with note type {note.note_type_version} is not billable and has no associated claim.",
                        note.note_type_version,
                    )
                )
                return errors

            if method in ACTION_STATE_MATRIX:
                _, error = self._validate_state_transition(note, ACTION_STATE_MATRIX[method])

                if error:
                    errors.append(error)

            return errors

        if method == "create":
            if not self.note_type_id:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'note_type_id' is required to create a note.",
                        None,
                    )
                )

            if not self.datetime_of_service:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'datetime_of_service' is required to create a note.",
                        None,
                    )
                )

            if not self.patient_id:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'patient_id' is required to create a note.",
                        None,
                    )
                )

            if self.instance_id and NoteModel.objects.filter(id=self.instance_id).exists():
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Note with ID {self.instance_id} already exists.",
                        self.instance_id,
                    )
                )

        elif method == "update":
            if self.note_type_id:
                errors.append(
                    self._create_error_detail(
                        "invalid",
                        "Field 'note_type_id' cannot be updated for a note.",
                        self.note_type_id,
                    )
                )
            if self.patient_id:
                errors.append(
                    self._create_error_detail(
                        "invalid",
                        "Field 'patient_id' cannot be updated for a note.",
                        self.patient_id,
                    )
                )

            if self.instance_id and not NoteModel.objects.filter(id=self.instance_id).exists():
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Note with ID {self.instance_id} does not exist.",
                        self.instance_id,
                    )
                )

        if self.note_type_id:
            note_type_category = (
                NoteType.objects.values_list("category", flat=True)
                .filter(id=self.note_type_id)
                .first()
            )

            if not note_type_category:
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Note type with ID {self.note_type_id} does not exist.",
                        self.note_type_id,
                    )
                )
            elif note_type_category in (
                NoteTypeCategories.APPOINTMENT,
                NoteTypeCategories.SCHEDULE_EVENT,
                NoteTypeCategories.MESSAGE,
                NoteTypeCategories.LETTER,
            ):
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Visit note type cannot be of type: {note_type_category}.",
                        self.note_type_id,
                    )
                )

        if self.patient_id and not Patient.objects.filter(id=self.patient_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Patient with ID {self.patient_id} does not exist.",
                    self.patient_id,
                )
            )

        return errors


__exports__ = ("Note",)
