from http import HTTPStatus

from canvas_sdk.commands.commands.prescribe import PrescribeCommand
from canvas_sdk.commands.commands.refill import RefillCommand
from canvas_sdk.commands.constants import ClinicalQuantity
from canvas_sdk.effects import Effect
from canvas_sdk.effects.launch_modal import LaunchModalEffect
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api.api import SimpleAPIRoute
from canvas_sdk.handlers.simple_api.security import PatientSessionAuthMixin
from canvas_sdk.v1.data.medication import Medication, Status
from canvas_sdk.v1.data.patient import Patient
from logger import log


class MedicationsHandler(PatientSessionAuthMixin, SimpleAPIRoute):
    """Handler for the Medications plugin."""
    PATH = "/medications/<id>"

    def get(self) -> list[Response | Effect]:
        """Serve the main HTML page for the Medications plugin."""
        internal_patient_id = self.request.headers.get("canvas-logged-in-user-id", None)

        log.info(f"MedicationsHandler GET request for patient ID: {internal_patient_id})")

        if not internal_patient_id:
            return [JSONResponse({"error": "Patient ID is required"}, status_code=HTTPStatus.BAD_REQUEST)]

        try:
            medications = Medication.objects.filter(
                patient__id=internal_patient_id,
                deleted=False,
                status=Status.ACTIVE,
            ).order_by("-start_date")
            medications_ids = [str(med.id) for med in medications]
        except Patient.DoesNotExist:
            return [JSONResponse({"error": "Patient not found"}, status_code=HTTPStatus.NOT_FOUND)]

        return [
            JSONResponse({
                "message": "Welcome to the Medications plugin!",
                "patient_id": internal_patient_id,
                "medications": medications_ids,
            }, status_code=HTTPStatus.OK),
            LaunchModalEffect(
                url="http://localhost:8000/app/messaging",
                content=None,
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
        command = RefillCommand(
            fdb_code="216092",
            icd10_codes=["R51"],
            sig="Take one tablet daily after meals",
            days_supply=30,
            quantity_to_dispense=30,
            type_to_dispense=ClinicalQuantity(
                representative_ndc="12843016128",
                ncpdp_quantity_qualifier_code="C48542"
            ),
            refills=3,
            substitutions=PrescribeCommand.Substitutions.ALLOWED,
            pharmacy="Main Street Pharmacy",
            prescriber_id="provider_123",
            supervising_provider_id="provider_456",
            note_to_pharmacist="Please verify patient's insurance before processing."
        )

        return JSONResponse(
            {
                "message": "Medication refill request processed successfully.",
            },
            status_code=HTTPStatus.OK
        )

