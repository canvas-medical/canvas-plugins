import json
from typing import Annotated, Any
from uuid import UUID

from django.db.models import Count
from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.base import _BaseEffect
from canvas_sdk.effects.note.base import AppointmentABC
from canvas_sdk.v1.data import Appointment as AppointmentDataModel
from canvas_sdk.v1.data import AppointmentLabel, NoteType, Patient
from canvas_sdk.v1.data.note import NoteTypeCategories


class ScheduleEvent(AppointmentABC):
    """
    Effect to create a schedule event.

    Attributes:
        note_type_id (UUID | str | None): The ID of the note type.
        patient_id (str | None): The ID of the patient, if applicable.
        description (str | None): The description of the schedule event, if applicable.
    """

    class Meta:
        effect_type = "SCHEDULE_EVENT"

    note_type_id: UUID | str | None = None
    patient_id: str | None = None
    description: str | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """
        Validates the schedule event note type and returns a list of error details if validation fails.

        Args:
            method (Any): The method being validated.

        Returns:
            list[InitErrorDetails]: A list of error details for invalid schedule event note types.
        """
        errors = super()._get_error_details(method)

        # note_type_id is required for create
        if method == "create" and not self.note_type_id:
            errors.append(
                self._create_error_detail(
                    "missing",
                    "Field 'note_type_id' is required to create a schedule event.",
                    None,
                )
            )
            return errors

        if self.note_type_id:
            note_type = (
                NoteType.objects.values("category", "is_patient_required", "allow_custom_title")
                .filter(id=self.note_type_id)
                .first()
            )

            if not note_type:
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Note type with ID {self.note_type_id} does not exist.",
                        self.note_type_id,
                    )
                )
                return errors

            if note_type["category"] != NoteTypeCategories.SCHEDULE_EVENT:
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Schedule event note type must be of type: {NoteTypeCategories.SCHEDULE_EVENT}.",
                        self.note_type_id,
                    )
                )

            if note_type["is_patient_required"] and not self.patient_id:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Patient ID is required for this note type.",
                        self.note_type_id,
                    )
                )

            if not note_type["allow_custom_title"] and self.description:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Description is not allowed for this note type.",
                        self.note_type_id,
                    )
                )

        # Validate patient exists if provided
        if self.patient_id and not Patient.objects.filter(id=self.patient_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Patient with ID {self.patient_id} does not exist.",
                    self.patient_id,
                )
            )

        return errors

    def delete(self) -> Effect:
        """Send a DELETE effect for the schedule event."""
        self._validate_before_effect("delete")
        return Effect(
            type=f"DELETE_{self.Meta.effect_type}",
            payload=json.dumps(
                {
                    "data": self.values,
                }
            ),
        )


class Appointment(AppointmentABC):
    """
    Effect to create or update an appointment.

    Attributes:
        appointment_note_type_id (UUID | str | None): The ID of the appointment note type.
        meeting_link (str | None): The meeting link for the appointment, if any.
        patient_id (str | None): The ID of the patient.
        labels (conset[str] | None): A set of label names to apply to the appointment.
    """

    class Meta:
        effect_type = "APPOINTMENT"

    appointment_note_type_id: UUID | str | None = None
    meeting_link: str | None = None
    patient_id: str | None = None
    labels: (
        Annotated[
            set[Annotated[str, Field(min_length=1, max_length=50)]],
            Field(min_length=1, max_length=3),
        ]
        | None
    ) = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """
        Validates the appointment note type and returns a list of error details if validation fails.

        Args:
            method (Any): The method being validated.

        Returns:
            list[InitErrorDetails]: A list of error details for invalid appointment note types or missing patient IDs.
        """
        errors = super()._get_error_details(method)

        if method == "create":
            if not self.appointment_note_type_id:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'appointment_note_type_id' is required to create an appointment.",
                        None,
                    )
                )
            if not self.patient_id:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'patient_id' is required to create an appointment.",
                        None,
                    )
                )

        if method == "update" and self.patient_id:
            errors.append(
                self._create_error_detail(
                    "value",
                    "Field 'patient_id' cannot be updated for an existing appointment.",
                    None,
                )
            )

        if self.patient_id and not Patient.objects.filter(id=self.patient_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    "Patient with ID {self.patient_id} does not exist.",
                    self.patient_id,
                )
            )

        if self.appointment_note_type_id:
            try:
                category, is_scheduleable = NoteType.objects.values_list(
                    "category", "is_scheduleable"
                ).get(id=self.appointment_note_type_id)
                if category != NoteTypeCategories.ENCOUNTER:
                    errors.append(
                        self._create_error_detail(
                            "value",
                            f"Appointment note type must be of type, {NoteTypeCategories.ENCOUNTER} but got: {category}.",
                            self.appointment_note_type_id,
                        )
                    )

                if not is_scheduleable:
                    errors.append(
                        self._create_error_detail(
                            "value",
                            "Appointment note type must be scheduleable.",
                            self.appointment_note_type_id,
                        )
                    )
            except NoteType.DoesNotExist:
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Note type with ID {self.appointment_note_type_id} does not exist.",
                        self.appointment_note_type_id,
                    )
                )

        if method == "update" and self.labels and self.instance_id:
            existing_count = AppointmentLabel.objects.filter(
                appointment__id=self.instance_id
            ).count()
            if existing_count + len(self.labels) > 3:
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Limit reached: Only 3 appointment labels allowed. Attempted to add {len(self.labels)} label(s) to appointment with {existing_count} existing label(s).",
                        sorted(self.labels),
                    )
                )

        return errors

    @property
    def values(self) -> dict:
        """
        Returns a dictionary of modified attributes with type-specific transformations.
        """
        values = super().values
        # Convert labels set to list for JSON serialization
        # This is necessary because:
        # 1. The labels field is defined as a conset (constrained set) for validation
        # 2. JSON cannot serialize Python sets directly - it only supports lists, dicts, strings, numbers, booleans, and None
        # 3. When the effect payload is serialized to JSON in the base Effect class, it would fail with:
        #    "TypeError: Object of type set is not JSON serializable"
        # 4. Converting to list maintains the same data while making it JSON-compatible
        # 5. Sort the labels to ensure consistent ordering for tests and API responses
        if self.labels is not None:
            values["labels"] = sorted(self.labels)
        return values

    def cancel(self) -> Effect:
        """Send a CANCEL effect for the appointment."""
        self._validate_before_effect("cancel")
        return Effect(
            type=f"CANCEL_{self.Meta.effect_type}",
            payload=json.dumps(
                {
                    "data": self.values,
                }
            ),
        )


class _AppointmentLabelBase(_BaseEffect, TrackableFieldsModel):
    """
    Base class for appointment label effects.

    Attributes:
        appointment_id (UUID | str): The ID of the appointment.
        labels (conset[str]): A set of label names (1-3 labels allowed).
    """

    appointment_id: str
    labels: Annotated[set[str], Field(min_length=1, max_length=3)]

    @property
    def values(self) -> dict:
        """The effect's values."""
        result = {
            "appointment_id": str(self.appointment_id),
            "labels": sorted(self.labels),
        }
        return result


class AddAppointmentLabel(_AppointmentLabelBase):
    """
    Effect to add one or more labels to an appointment.
    """

    class Meta:
        effect_type = EffectType.ADD_APPOINTMENT_LABEL

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """Validate that the appointment does not exceed the 3-label limit."""
        errors = super()._get_error_details(method)

        appointment_label_count = (
            AppointmentDataModel.objects.filter(id=self.appointment_id)
            .annotate(label_count=Count("labels"))
            .values_list("label_count", flat=True)
            .first()
        )

        # note that appointment_label_count will be None if the appointment doesn't exist
        # and appointment_label_count will be 0 if the appointment exists but has no labels
        if appointment_label_count is None:
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Appointment {self.appointment_id} does not exist",
                    self.appointment_id,
                )
            )
        elif appointment_label_count + len(self.labels) > 3:
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Limit reached: Only 3 appointment labels allowed. "
                    f"Attempted to add {len(self.labels)} label(s) to appointment with "
                    f"{appointment_label_count} existing label(s).",
                    sorted(self.labels),
                )
            )
        return errors


class RemoveAppointmentLabel(_AppointmentLabelBase):
    """
    Effect to remove one or more labels from an appointment.

    Attributes:
        appointment_id (UUID | str): The ID of the appointment to remove labels from.
        labels (list[str]): A list of label names to remove.
    """

    class Meta:
        effect_type = EffectType.REMOVE_APPOINTMENT_LABEL


__exports__ = (
    "ScheduleEvent",
    "Appointment",
    "AddAppointmentLabel",
    "RemoveAppointmentLabel",
)
