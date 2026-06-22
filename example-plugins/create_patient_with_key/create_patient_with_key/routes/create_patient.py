from datetime import date

from canvas_sdk.effects import Effect
from canvas_sdk.effects.patient import Patient, generate_patient_key
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api import APIKeyCredentials, SimpleAPIRoute
from canvas_sdk.v1.data.common import PersonSex
from logger import log

# POST /plugin-io/api/create_patient_with_key/create-test-patient
# Headers: "Authorization: <your value for 'pre-shared-key'>"


class CreateTestPatientAPI(SimpleAPIRoute):
    """Create a patient whose key the plugin chooses up front, and return that key."""

    PATH = "/create-test-patient"

    def authenticate(self, credentials: APIKeyCredentials) -> bool:
        """Simple API key authentication."""
        return credentials.key == self.secrets["pre-shared-key"]

    def post(self) -> list[Response | Effect]:
        """Generate a patient key, create the patient with it, and return the key."""
        patient_key = generate_patient_key()
        log.info(f"Creating test patient with plugin-defined key {patient_key}")

        patient = Patient(
            patient_id=patient_key,
            first_name="Key",
            last_name="Tester",
            birthdate=date(1990, 1, 1),
            sex_at_birth=PersonSex.SEX_FEMALE,
        )

        return [
            patient.create(),
            JSONResponse(
                {
                    "patient_key": patient_key,
                    "message": "Patient created with this plugin-defined key.",
                }
            ),
        ]
