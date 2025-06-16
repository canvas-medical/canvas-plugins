from http import HTTPStatus
from typing import cast

import arrow

from canvas_sdk.effects import Effect
from canvas_sdk.effects.patient import Patient, PatientExternalIdentifier
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api import Credentials, SimpleAPI, api
from canvas_sdk.v1.data.common import PersonSex
from logger import log

BRIDGE_SANDBOX = "https://app.usebridge.xyz"


class PatientCreateApi(SimpleAPI):
    """API for bidirectional patient sync."""

    def authenticate(self, credentials: Credentials) -> bool:
        """Authenticate with the provided credentials."""
        # TODO: fix this before merging
        # api_key = self.secrets["my_canvas_api_key"]
        # log.info(f'PatientCreateApi.post: authenticating with API key {api_key}')
        return True

    # https://docs.canvasmedical.com/sdk/handlers-simple-api-http/
    # https://<instance-name>.canvasmedical.com/plugin-io/api/example_patient_sync/patients
    @api.post("/patients")
    def post(self) -> list[Response | Effect]:
        """Handle POST requests for patient sync."""
        json_body = self.request.json()
        log.info(f"PatientCreateApi.post: {json_body}")

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

        # this supports the first external identifier but could be extended to support multiple
        external_identifiers = json_body.get("externalIdentifiers")
        if (
            isinstance(external_identifiers, list)
            and external_identifiers
            and isinstance(external_identifiers[0], dict)
        ):
            ext_id_dict = external_identifiers[0]
        else:
            ext_id_dict = {}

        external_id = PatientExternalIdentifier(
            system=str(ext_id_dict.get("system", "Bridge")),
            value=str(ext_id_dict.get("value", "")),
        )

        patient = Patient(
            birthdate=birthdate,
            first_name=str(json_body.get("firstName")),
            last_name=str(json_body.get("lastName")),
            sex_at_birth=sex_at_birth,
            external_identifiers=[external_id],
        )
        log.info(f"PatientCreateApi.post: patient={patient}")

        return [
            patient.create(),
            JSONResponse(content=str(patient), status_code=HTTPStatus.ACCEPTED).apply(),
        ]
