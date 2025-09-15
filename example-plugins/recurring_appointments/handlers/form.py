from canvas_sdk.handlers import BaseHandler
from canvas_sdk.effects.appointments_metadata import (
    FormField,
    InputType,
    AppointmentsMetadataCreateFormEffect,
)
from canvas_sdk.events import EventType
from canvas_sdk.effects import Effect
from recurring_appointments.utils.constants import RecurrenceEnum, FIELD_RECURRENCE_KEY


class AppointmentFormFields(BaseHandler):
    RESPONDS_TO = EventType.Name(EventType.APPOINTMENT__FORM__GET_ADDITIONAL_FIELDS)

    def compute(self) -> list[Effect]:
        # recurrence form field
        recurrence_form_field = FormField(
            key=FIELD_RECURRENCE_KEY,
            label="Recurrence",
            type=InputType.SELECT,
            required=False,
            options=[item.value for item in RecurrenceEnum],

        )

        return [
            AppointmentsMetadataCreateFormEffect(
                form_fields=[
                  recurrence_form_field
                ]
            ).apply()
        ]