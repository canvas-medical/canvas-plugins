from http import HTTPStatus

from canvas_sdk.effects import Effect
from canvas_sdk.effects.patient.create_patient_preferred_pharmacies import (
    CreatePatientPreferredPharmacies,
)
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.effects.task.task import AddTask
from canvas_sdk.handlers.simple_api import api
from canvas_sdk.handlers.simple_api.api import SimpleAPI
from canvas_sdk.handlers.simple_api.security import PatientSessionAuthMixin
from canvas_sdk.utils.http import pharmacy_http
from canvas_sdk.v1.data.medication import Medication
from canvas_sdk.v1.data.patient import Patient
from logger import log


class PrescriptionsHandler(PatientSessionAuthMixin, SimpleAPI):
    """Handler for the Prescriptions plugin."""

    PREFIX = "/<id>"

    DEFAULT_BACKGROUND_COLOR = "#17634d"

    @api.get("/request-refill")
    def get_request_refill(self) -> list[Response | Effect]:
        """Serve the main HTML page for the Prescriptions plugin."""
        patient_id = self.request.headers.get("canvas-logged-in-user-id", None)

        log.info(f"PrescriptionsHandler GET request for patient ID: {patient_id})")

        if not patient_id:
            return [
                JSONResponse(
                    {"error": "Patient ID is required"}, status_code=HTTPStatus.BAD_REQUEST
                )
            ]

        try:
            medications = list(
                Medication.objects.for_patient(patient_id).filter(
                    committer__isnull=False,
                    entered_in_error__isnull=True,
                    deleted=False,
                ).values(
                    "id",
                    "quantity_qualifier_description",
                    "clinical_quantity_description",
                    "potency_unit_code",
                    "start_date",
                    "end_date",
                    "codings__code",
                    "codings__display",
                )
            )

            medications = [
                {
                    "id": str(med["id"]),
                    "start_date": str(med["start_date"]),
                    "end_date": str(med["end_date"]),
                    "codings": [
                        {
                            "code": med["codings__code"],
                            "display": med["codings__display"],
                        }
                    ],
                    "quantity_qualifier_description": med["quantity_qualifier_description"],
                    "clinical_quantity_description": med["clinical_quantity_description"],
                    "potency_unit_code": med["potency_unit_code"],
                }
                for med in medications
                if med["codings__display"]
            ]

        except Patient.DoesNotExist:
            return [JSONResponse({"error": "Patient not found"}, status_code=HTTPStatus.NOT_FOUND)]
        except Medication.DoesNotExist:
            return [
                JSONResponse(
                    {"error": "No medications found for this patient"},
                    status_code=HTTPStatus.NOT_FOUND,
                ),
            ]

        log.info(f"Medications found for patient {patient_id}: {medications}")

        return [
            JSONResponse(
                {
                    "medications": medications,
                    "patient_id": patient_id,
                },
                status_code=HTTPStatus.OK,
            ),
        ]

    @api.post("/request-refill")
    def post_request_refill(self) -> list[Response | Effect]:
        """Handle POST requests to the Medications plugin."""
        patient_id = self.request.headers.get("canvas-logged-in-user-id", None)
        form_data = self.request.form_data()

        if not patient_id or not form_data:
            return [JSONResponse({"error": "Invalid request"}, status_code=HTTPStatus.BAD_REQUEST)]

        medication_ids: list[str] = [
            str(part.value) for name, part in form_data.multi_items() if name == "medication"
        ]
        if not medication_ids:
            return [
                JSONResponse(
                    {"error": "No medications selected"}, status_code=HTTPStatus.BAD_REQUEST
                )
            ]

        medications = Medication.objects.filter(id__in=medication_ids, patient__id=patient_id)
        if not medications:
            return [
                JSONResponse(
                    {"error": "No valid medications found"}, status_code=HTTPStatus.NOT_FOUND
                )
            ]

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
            JSONResponse(
                {
                    "message": "Medication successfully created/updated!",
                    "patient_id": patient_id,
                },
                status_code=HTTPStatus.CREATED,
            ),
        ]

    @api.get("/update-pharmacy")
    def get_update_pharmacy(self) -> list[Response | Effect]:
        """Handle GET requests to update the preferred pharmacy."""
        patient_id = self.request.headers.get("canvas-logged-in-user-id", None)

        if not patient_id:
            return [
                JSONResponse(
                    {"error": "Patient ID is required"}, status_code=HTTPStatus.BAD_REQUEST
                )
            ]

        patient = Patient.objects.get(id=patient_id)
        preferred_pharmacy = patient.preferred_pharmacy

        # Logic to update the preferred pharmacy would go here.
        # For now, we just return a success message.
        return [
            JSONResponse(
                {
                    "message": f"Preferred pharmacy is: {preferred_pharmacy}",
                    "preferred_pharmacy": preferred_pharmacy,
                },
                status_code=HTTPStatus.OK,
            )
        ]

    @api.post("/search-pharmacy")
    def post_search_pharmacy(self) -> list[Response | Effect]:
        """Handle POST requests to search for pharmacies."""
        form_data = self.request.form_data()
        search_query = form_data["search_query"] if form_data and "search_query" in form_data else ""
        patient_id = self.request.headers.get("canvas-logged-in-user-id", None)

        log.info(f"Searching for pharmacies with query: {search_query}")

        if not patient_id:
            return [
                JSONResponse(
                    {"error": "Patient ID is required"}, status_code=HTTPStatus.BAD_REQUEST
                )
            ]

        patient = Patient.objects.get(id=patient_id)
        preferred_pharmacies = patient.preferred_pharmacies
        available_pharmacies = pharmacy_http.search_pharmacies(search_query)

        if not search_query:
            return [
                JSONResponse(
                    {"error": "Search query is required"}, status_code=HTTPStatus.BAD_REQUEST
                )
            ]

        return [
            JSONResponse(
                {"available_pharmacies": available_pharmacies, "preferred_pharmacies": preferred_pharmacies},
                status_code=HTTPStatus.OK,
            )
        ]

    @api.post("/update-pharmacy")
    def post_update_pharmacy(self) -> list[Response | Effect]:
        """Handle POST requests to update the preferred pharmacy."""
        patient_id = self.request.headers.get("canvas-logged-in-user-id", None)
        form_data = self.request.form_data()

        if not patient_id or not form_data:
            return [JSONResponse({"error": "Invalid request"}, status_code=HTTPStatus.BAD_REQUEST)]

        new_pharmacy = form_data.get("preferred_pharmacy")
        if not new_pharmacy:
            return [
                JSONResponse(
                    {"error": "Preferred pharmacy is required"}, status_code=HTTPStatus.BAD_REQUEST
                )
            ]

        patient = Patient.objects.get(id=patient_id)

        return [
            JSONResponse(
                {
                    "message": "Preferred pharmacy updated successfully!",
                    "preferred_pharmacy": new_pharmacy,
                },
                status_code=HTTPStatus.OK,
            ),
            CreatePatientPreferredPharmacies(
                pharmacies=[new_pharmacy],
                patient_id=patient_id,
            ).create(),
        ]

    @property
    def background_color(self) -> str:
        """Get the background color from secrets, defaulting to a specific color if not set."""
        return self.secrets.get("BACKGROUND_COLOR") or self.DEFAULT_BACKGROUND_COLOR

    @property
    def assigned_team(self) -> str | None:
        """Get the task assignment from secrets, defaulting to a specific value if not set."""
        return self.secrets.get("ASSIGNED_TEAM")
