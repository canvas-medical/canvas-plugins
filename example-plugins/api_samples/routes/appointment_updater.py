from http import HTTPStatus

from canvas_sdk.effects import Effect
from canvas_sdk.effects.note.appointment import Appointment
from canvas_sdk.effects.note.base import AppointmentIdentifier
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api import APIKeyAuthMixin, SimpleAPIRoute
from canvas_sdk.v1.data.appointment import Appointment as AppointmentData

# PUT /plugin-io/api/api_samples/appointments/<id>
# Headers: "Authorization <your value for 'my-api-key'>"

# Authentication is handled by the APIKeyAuthMixin, which checks the API key in the request headers
# https://docs.canvasmedical.com/sdk/handlers-simple-api-http/#api-key-1

class AppointmentAPI(APIKeyAuthMixin, SimpleAPIRoute):
    """API for managing appointment updates."""
    PATH = "/appointments/<id>"

    def put(self) -> list[Response | Effect]:
        """Update an existing appointment."""
        note_dbid = self.request.path_params.get("id")
        body = self.request.json()

        meeting_link = str(body.get("meetingLink"))

        appointments = AppointmentData.objects.filter(note_id=note_dbid)
        # or this can be a UUID if you have it
        # appointment = AppointmentData.objects.get(note__id=note_uuid)
        # the current appointment is the last one after any reschedules / updates
        appointment = appointments.last()

        if not appointment:
            return [JSONResponse(status_code=HTTPStatus.NOT_FOUND, content={"error": "Appointment not found"})]

        # set up the meeting effect to update the appointment
        appointment_effect = Appointment(instance_id=appointment.id)

        # add the meeting link to the appointment
        appointment_effect.meeting_link = meeting_link

        # let's also add some external identifiers for fun
        # for example, this could be an ID from an external scheduling system
        external_identifiers=[
            AppointmentIdentifier(system="https://www.example.com", value="123TEST")
        ]

        appointment_effect.external_identifiers = external_identifiers

        return [appointment_effect.update(), Response(status_code=HTTPStatus.ACCEPTED)]
