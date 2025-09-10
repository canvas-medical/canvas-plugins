import json

from canvas_sdk.handlers import BaseHandler
from canvas_sdk.v1.data import Staff
from canvas_sdk.effects.appointments_metadata import (
    FormField,
    InputType,
    AppointmentsMetadataCreateFormEffect,
)
from canvas_sdk.events import EventType
from canvas_sdk.effects import Effect, EffectType
from appointment_state_field.utils.constants import STATES, STATES_DICT, FIELD_STATE_KEY


class AppointmentFormFields(BaseHandler):
    RESPONDS_TO = EventType.Name(EventType.APPOINTMENT__FORM__GET_ADDITIONAL_FIELDS)

    def compute(self) -> list[Effect]:

        state_form_field = FormField(
            key=FIELD_STATE_KEY,
            label="State",
            type=InputType.SELECT,
            required=False,
            options=STATES,
        )

        return [
            AppointmentsMetadataCreateFormEffect(
                form_fields=[
                  state_form_field
                ]
            ).apply()
        ]


class AppointmentProviderFormField(BaseHandler):

    RESPONDS_TO = EventType.Name(EventType.APPOINTMENT__FORM__PROVIDERS__POST_SEARCH)

    def compute(self) -> list[Effect]:
        providers = self.context.get("providers", [])
        selected_values = self.context.get("selected_values", {})
        additional_fields = selected_values["additional_fields"] or []

        state_field = next((field for field in additional_fields if field.get("key") == FIELD_STATE_KEY), None)
        state_selected = STATES_DICT[state_field["values"]] if state_field and state_field["values"] != "" else None

        if state_selected:
            provider_options = []

            for provider in providers:
                if staff_provider := Staff.objects.filter(dbid=provider["value"]).first():
                    if staff_provider.licenses.filter(state=state_selected).exists():
                         provider_options.append(provider)

            return [Effect(type=EffectType.APPOINTMENT__FORM__PROVIDERS__POST_SEARCH_RESULTS, payload=json.dumps({"providers": provider_options}))]

        return []