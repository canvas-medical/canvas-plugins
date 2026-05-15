from canvas_sdk.effects import Effect
from canvas_sdk.effects.appointments_metadata import (
    AppointmentsMetadataCreateFormEffect,
    FormField,
    InputType,
)
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from recurring_appointments.utils.constants import (
    FIELD_RECURRENCE_INTERVAL_KEY,
    FIELD_RECURRENCE_STOP_AFTER_KEY,
    FIELD_RECURRENCE_TYPE_KEY,
    RecurrenceEnum,
)


class AppointmentFormFields(BaseHandler):
    """Handler for providing additional appointment form fields for recurring appointments."""

    RESPONDS_TO = EventType.Name(EventType.APPOINTMENT__FORM__GET_ADDITIONAL_FIELDS)

    def compute(self) -> list[Effect]:
        """Compute and return form fields for recurring appointment configuration."""
        interval_form_field = FormField(
            key=FIELD_RECURRENCE_INTERVAL_KEY,
            label="Every",
            type=InputType.SELECT,
            required=False,
            options=[f"{i}" for i in range(1, 9)],
        )

        # recurrence form field
        recurrence_form_field = FormField(
            key=FIELD_RECURRENCE_TYPE_KEY,
            label="Recurrence",
            type=InputType.SELECT,
            required=False,
            options=[item.value for item in RecurrenceEnum if item != RecurrenceEnum.NONE],
        )

        stop_after_form_field = FormField(
            key=FIELD_RECURRENCE_STOP_AFTER_KEY,
            label="Ends After X Events",
            type=InputType.TEXT,
            required=False,
        )

        return [
            AppointmentsMetadataCreateFormEffect(
                form_fields=[interval_form_field, recurrence_form_field, stop_after_form_field]
            ).apply()
        ]
