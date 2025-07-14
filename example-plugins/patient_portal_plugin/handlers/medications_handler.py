import json
from http import HTTPStatus

from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api.api import SimpleAPIRoute
from canvas_sdk.handlers.simple_api.security import PatientSessionAuthMixin
from canvas_sdk.templates.utils import render_to_string
from canvas_sdk.v1.data.medication import Medication
from canvas_sdk.v1.data.patient import Patient
from logger import log


class MedicationsHandler(PatientSessionAuthMixin, SimpleAPIRoute):
    """Handler for the Medications plugin."""
    PATH = "/medications/<id>"

    DEFAULT_BACKGROUND_COLOR = "#17634d"

    def get(self) -> list[Response | Effect]:
        """Serve the main HTML page for the Medications plugin."""
        internal_patient_id = self.request.headers.get("canvas-logged-in-user-id", None)

        log.info(f"MedicationsHandler GET request for patient ID: {internal_patient_id})")

        if not internal_patient_id:
            return [JSONResponse({"error": "Patient ID is required"}, status_code=HTTPStatus.BAD_REQUEST)]

        try:
            medications = Medication.objects.for_patient(internal_patient_id)

            for medication in medications:
                for coding in medication.codings.all():
                    log.info(f"system:  {coding.system}")
                    log.info(f"code:    {coding.code}")
                    log.info(f"display: {coding.display}")

        except Patient.DoesNotExist:
            return [JSONResponse({"error": "Patient not found"}, status_code=HTTPStatus.NOT_FOUND)]
        except Medication.DoesNotExist:
            return [JSONResponse({"error": "No medications found for this patient"}, status_code=HTTPStatus.NOT_FOUND)]

        return [
            JSONResponse({
                "message": "Welcome to the Medications plugin!",
                "patient_id": internal_patient_id,
                # "medications": medications,
            }, status_code=HTTPStatus.OK),
            LaunchModalEffect(
                content=render_to_string(
                    "templates/refill_form.html",
                    {
                        "patient_id": internal_patient_id,
                        "medications": [medication.codings.first() for medication in medications],
                        "background_color": self.background_color,
                    }
                ),
                target=LaunchModalEffect.TargetType.DEFAULT_MODAL,
                title="Medications Information",
                patient_id=internal_patient_id,
            ).apply()
        ]

    def post(self) -> list[Response | Effect]:
        """Handle POST requests to the Medications plugin."""
        internal_patient_id = self.request.headers.get("canvas-logged-in-user-id", None)

        if not internal_patient_id:
            return [JSONResponse({"error": "Unauthorized"}, status_code=HTTPStatus.UNAUTHORIZED)]

        # Here you would handle the logic for creating or updating medications.
        # For now, we just return a success message.
        return [
            JSONResponse({
                "message": "Medication successfully created/updated!",
                "patient_id": internal_patient_id,
            }, status_code=HTTPStatus.CREATED),
        ]

    def _refill(self) -> Response:
        """Handle medication refill requests."""
        return JSONResponse({
            "message": "Medication refill request processed successfully.",
        }, status_code=HTTPStatus.OK)

    @property
    def background_color(self) -> str:
        """Get the background color from secrets, defaulting to a specific color if not set."""
        return self.secrets.get("BACKGROUND_COLOR") or self.DEFAULT_BACKGROUND_COLOR

