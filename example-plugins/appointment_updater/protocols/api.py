from http import HTTPStatus

from canvas_sdk.effects import Effect
from canvas_sdk.effects.note.appointment import Appointment
from canvas_sdk.effects.simple_api import Response
from canvas_sdk.handlers.simple_api import APIKeyAuthMixin, Credentials, SimpleAPIRoute
from canvas_sdk.v1.data.appointment import Appointment as AppointmentData

# PUT /plugin-io/api/appointment_updater/appointments/<id>
# Headers: "Authorization <your value for 'my-api-key'>"

# Authentication is handled by the APIKeyAuthMixin, which checks the API key in the request headers
# https://docs.canvasmedical.com/sdk/handlers-simple-api-http/#api-key-1

class AppointmentAPI(APIKeyAuthMixin, SimpleAPIRoute):
    """API for managing appointments."""
    PATH = "/appointments/<id>"

    def put(self) -> list[Response | Effect]:
        """Update an existing appointment."""
        note_dbid = self.request.path_params.get("id")
        body = self.request.json()

        meeting_link = str(body.get("meetingLink"))

        appointments = AppointmentData.objects.filter(note_id=note_dbid)
        # or this can be a UUID if you have it
        # appointment = AppointmentData.objects.get(note__id=note_uuid)
        if not appointments:
            return [Response(status_code=HTTPStatus.NOT_FOUND, content={"error": "Appointment not found"})]

        # the current appointment is the last one after any reschedules / updates
        appointment = appointments.last()
        if not appointment:
            return [Response(status_code=HTTPStatus.NOT_FOUND, content={"error": "Appointment not found"})]

        appointment_effect = Appointment(instance_id=appointment.id)
        appointment_effect.meeting_link = meeting_link

        return [appointment_effect.update(), Response(status_code=HTTPStatus.ACCEPTED)]
