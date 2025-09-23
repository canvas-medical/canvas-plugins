from http import HTTPStatus
from typing import cast

import arrow

from canvas_sdk.effects import Effect
from canvas_sdk.effects.patient import Patient, PatientExternalIdentifier
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api import APIKeyAuthMixin, SimpleAPI, api
from canvas_sdk.v1.data.common import PersonSex


# Authentication is handled by the APIKeyAuthMixin, which checks the API key in the request headers
# https://docs.canvasmedical.com/sdk/handlers-simple-api-http/#api-key-1
class PatientCreateApi(APIKeyAuthMixin, SimpleAPI):
    """API endpoint for use by third-party system to create patients in Canvas when that system is the point of origination for that patient record."""

    # Docs: https://docs.canvasmedical.com/sdk/handlers-simple-api-http/
    # POST https://<instance-name>.canvasmedical.com/plugin-io/api/example_patient_sync/patients
    @api.post("/patients")
    def post(self) -> list[Response | Effect]:
        """Handle POST requests for patient sync."""
        json_body = self.request.json()

        if not isinstance(json_body, dict):
            return [
                JSONResponse(
                    content="Invalid JSON body.", status_code=HTTPStatus.BAD_REQUEST
                ).apply()
            ]
        birthdate = None
        date_of_birth_str = json_body.get("dateOfBirth")
        if isinstance(date_of_birth_str, str) and date_of_birth_str:
            birthdate = arrow.get(date_of_birth_str).date()

        sex_at_birth = None
        sex_at_birth_str = json_body.get("sexAtBirth")
        if sex_at_birth_str:
            s = cast(str, sex_at_birth_str).strip().upper()
            if s in ("F", "FEMALE"):
                sex_at_birth = PersonSex.SEX_FEMALE
            elif s in ("M", "MALE"):
                sex_at_birth = PersonSex.SEX_MALE
            elif s in ("O", "OTHER"):
                sex_at_birth = PersonSex.SEX_OTHER
            elif s in ("U", "UNKNOWN"):
                sex_at_birth = PersonSex.SEX_UNKNOWN
            else:
                sex_at_birth = None

        partner_id = str(json_body.get("partnerId"))

        external_id = PatientExternalIdentifier(
            system=self.secrets['PARTNER_URL_BASE'],
            value=partner_id,
        )

        patient = Patient(
            birthdate=birthdate,
            first_name=str(json_body.get("firstName")),
            last_name=str(json_body.get("lastName")),
            sex_at_birth=sex_at_birth,
            external_identifiers=[external_id],
        )

        response = {"external_identifier": {"system": self.secrets['PARTNER_URL_BASE'], "value": partner_id}}

        return [
            patient.create(),
            JSONResponse(content=response, status_code=HTTPStatus.ACCEPTED).apply(),
        ]
