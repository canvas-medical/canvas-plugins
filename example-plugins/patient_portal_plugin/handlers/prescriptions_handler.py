from http import HTTPStatus

from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.effects.task.task import AddTask
from canvas_sdk.handlers.simple_api.api import SimpleAPIRoute
from canvas_sdk.handlers.simple_api.security import PatientSessionAuthMixin
from canvas_sdk.templates.utils import render_to_string
from canvas_sdk.v1.data.medication import Medication
from canvas_sdk.v1.data.patient import Patient
from logger import log


class PrescriptionsHandler(PatientSessionAuthMixin, SimpleAPIRoute):
    """Handler for the Prescriptions plugin."""
    PATH = "/prescriptions/<id>"

    DEFAULT_BACKGROUND_COLOR = "#17634d"

    def get(self) -> list[Response | Effect]:
        """Serve the main HTML page for the Prescriptions plugin."""
        patient_id = self.request.headers.get("canvas-logged-in-user-id", None)

        log.info(f"PrescriptionsHandler GET request for patient ID: {patient_id})")

        if not patient_id:
            return [JSONResponse({"error": "Patient ID is required"}, status_code=HTTPStatus.BAD_REQUEST)]

        try:
            medications = Medication.objects.for_patient(patient_id)

            for medication in medications:
                for coding in medication.codings.all():
                    log.info(f"system:  {coding.system}")
                    log.info(f"code:    {coding.code}")
                    log.info(f"display: {coding.display}")

        except Patient.DoesNotExist:
            return [JSONResponse({"error": "Patient not found"}, status_code=HTTPStatus.NOT_FOUND)]
        except Medication.DoesNotExist:
            return [JSONResponse({"error": "No medications found for this patient"}, status_code=HTTPStatus.NOT_FOUND)]

        medications = [{ "id": medication.id, "coding": medication.codings.first() } for medication in medications]

        return [
            LaunchModalEffect(
                content=render_to_string(
                    "templates/refill_form.html",
                    {
                        "api_url": f"/plugin-io/api/patient_portal_plugin/prescriptions/{patient_id}",
                        "medications": medications,
                        "background_color": self.background_color,
                    }
                ),
                target=LaunchModalEffect.TargetType.DEFAULT_MODAL,
                title="Medications Information",
                patient_id=patient_id,
            ).apply()
        ]

    def post(self) -> list[Response | Effect]:
        """Handle POST requests to the Medications plugin."""
        patient_id = self.request.headers.get("canvas-logged-in-user-id", None)
        form_data = self.request.form_data()

        if not patient_id or not form_data:
            return [JSONResponse({"error": "Invalid request"}, status_code=HTTPStatus.BAD_REQUEST)]

        medication_ids: list[str] = [str(part.value) for name, part in form_data.multi_items() if name == "medication"]
        if not medication_ids:
            return [JSONResponse({"error": "No medications selected"}, status_code=HTTPStatus.BAD_REQUEST)]

        medications = Medication.objects.filter(id__in=medication_ids, patient__id=patient_id)
        if not medications:
            return [JSONResponse({"error": "No valid medications found"}, status_code=HTTPStatus.NOT_FOUND)]

        tasks = []
        for medication in medications:
            coding = medication.codings.first()
            log.info(f"Processing medication: {medication.id} - {coding.display}")
            tasks.append(
                AddTask(
                    title=f"Medication Refill Requested: {coding.display}",
                    patient_id=patient_id,
                    labels=["Refill Request"],
                    team_id=self.assigned_team,
                ).apply()
            )

        # Here you would handle the logic for creating or updating medications.
        # For now, we just return a success message.
        return [
            *tasks,
            JSONResponse({
                "message": "Medication successfully created/updated!",
                "patient_id": patient_id,
            }, status_code=HTTPStatus.CREATED),
        ]

    @property
    def background_color(self) -> str:
        """Get the background color from secrets, defaulting to a specific color if not set."""
        return self.secrets.get("BACKGROUND_COLOR") or self.DEFAULT_BACKGROUND_COLOR

    @property
    def assigned_team(self) -> str | None:
        """Get the task assignment from secrets, defaulting to a specific value if not set."""
        return self.secrets.get("ASSIGNED_TEAM")
