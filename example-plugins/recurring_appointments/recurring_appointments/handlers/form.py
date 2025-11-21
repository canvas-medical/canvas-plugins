from canvas_sdk.handlers import BaseHandler
from canvas_sdk.effects.appointments_metadata import (
    FormField,
    InputType,
    AppointmentsMetadataCreateFormEffect,
)
from canvas_sdk.events import EventType
from canvas_sdk.effects import Effect
from recurring_appointments.utils.constants import (
    RecurrenceEnum,
    FIELD_RECURRENCE_TYPE_KEY,
    FIELD_RECURRENCE_INTERVAL_KEY,
    FIELD_RECURRENCE_STOP_AFTER_KEY,
)


class AppointmentFormFields(BaseHandler):
    RESPONDS_TO = EventType.Name(EventType.APPOINTMENT__FORM__GET_ADDITIONAL_FIELDS)

    def compute(self) -> list[Effect]:
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
