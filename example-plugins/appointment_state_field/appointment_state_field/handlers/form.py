import json

from appointment_state_field.utils.constants import FIELD_STATE_KEY, STATES, STATES_DICT
from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.appointments_metadata import (
    AppointmentsMetadataCreateFormEffect,
    FormField,
    InputType,
)
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from canvas_sdk.v1.data import Staff


class AppointmentFormFields(BaseHandler):
    """Handler for providing additional appointment form fields."""

    RESPONDS_TO = EventType.Name(EventType.APPOINTMENT__FORM__GET_ADDITIONAL_FIELDS)

    def compute(self) -> list[Effect]:
        """Compute and return form fields for appointment state selection."""
        state_form_field = FormField(
            key=FIELD_STATE_KEY,
            label="State",
            type=InputType.SELECT,
            required=False,
            options=STATES,
        )

        return [AppointmentsMetadataCreateFormEffect(form_fields=[state_form_field]).apply()]


class AppointmentProviderFormField(BaseHandler):
    """Handler for filtering providers based on appointment state field."""

    RESPONDS_TO = EventType.Name(EventType.APPOINTMENT__FORM__PROVIDERS__POST_SEARCH)

    def compute(self) -> list[Effect]:
        """Filter providers based on state licensing requirements."""
        providers = self.context.get("providers", [])
        selected_values = self.context.get("selected_values", {})
        additional_fields = selected_values["additional_fields"] or []

        state_field = next(
            (field for field in additional_fields if field.get("key") == FIELD_STATE_KEY), None
        )
        state_selected = (
            STATES_DICT[state_field["values"]]
            if state_field and state_field["values"] != ""
            else None
        )

        if state_selected:
            provider_options = []

            for provider in providers:
                if (
                    staff_provider := Staff.objects.filter(id=provider["value"]).first()
                ) and staff_provider.licenses.filter(state=state_selected).exists():
                    provider_options.append(provider)

            return [
                Effect(
                    type=EffectType.APPOINTMENT__FORM__PROVIDERS__POST_SEARCH_RESULTS,
                    payload=json.dumps({"providers": provider_options}),
                )
            ]

        return []
