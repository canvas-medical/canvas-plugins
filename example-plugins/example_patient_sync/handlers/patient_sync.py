from typing import Any

from canvas_sdk.effects import Effect
from canvas_sdk.effects.patient import CreatePatientExternalIdentifier
from canvas_sdk.events import EventType
from canvas_sdk.handlers.base import BaseHandler
from canvas_sdk.utils import Http
from canvas_sdk.v1.data.patient import Patient
from logger import log

PARTNER_URL_BASE = "https://your-subdomain.example.com"

class PatientSync(BaseHandler):
    """Handler for synchronizing patient data between systems."""

    RESPONDS_TO = [
        EventType.Name(EventType.PATIENT_CREATED),
    ]

    @property
    def partner_api_base_url(self) -> str:
        """Return the base URL for the external partner API."""
        return self.secrets["PARTNER_API_BASE_URL"] or f"{PARTNER_URL_BASE}/api"

    @property
    def partner_request_headers(self) -> dict[str, str]:
        """Return the request headers for external partner API requests."""
        partner_secret_api_key = self.secrets["PARTNER_SECRET_API_KEY"]
        return {"X-API-Key": partner_secret_api_key}

    @property
    def partner_patient_metadata(self) -> Any:
        """Return metadata for creation of the patient on external partner platform."""
        metadata = {"canvasPatientId": self.target}

        subdomain = self.environment["CUSTOMER_IDENTIFIER"]
        canvas_url = f"https://{subdomain}.canvasmedical.com"

        if canvas_url:
            # This sets the canvas URL for the patient in the partner platform metadata
            # Combined with the canvasPatientId, this allows the partner platform to link back to the patient in Canvas
            metadata["canvasUrl"] = canvas_url

        return metadata

    def lookup_external_id_by_system_url(self, canvas_patient: Patient, system: str) -> str | None:
        """Get the system ID for a given patient and system from Canvas."""
        # If the patient already has a external identifier for the partner platform, identified by a matching system url, use the first one
        return (
            canvas_patient.external_identifiers.filter(system=system)
            .values_list("value", flat=True)
            .first()
        )

    def get_patient_from_system_api(self, canvas_patient_id: str) -> Any:
        """Look up a patient in the external system."""
        http = Http()
        return http.get(
            f"{self.partner_api_base_url}/patients/v2/{canvas_patient_id}",
            headers=self.partner_request_headers,
        )

    def compute(self) -> list[Effect]:
        """Compute the sync actions for the patient."""
        canvas_patient_id = self.target

        http = Http()

        canvas_patient = Patient.objects.get(id=canvas_patient_id)
        # by default assume we don't yet have a system patient ID
        # and that we need to update the patient in Canvas to add one
        system_patient_id = self.lookup_external_id_by_system_url(canvas_patient, PARTNER_URL_BASE)
        update_patient_external_identifier = system_patient_id is None

        # Here we check if the patient already has an external ID in Canvas for the partner platform
        if not system_patient_id:

            # Get the system external ID by making a GET request to the partner platform
            system_patient = self.get_patient_from_system_api(canvas_patient_id)

            system_patient_id = (
                system_patient.json()["id"] if system_patient.status_code == 200 else None
            )

        # Great, now we know if the patient is assigned a system external ID with the partner
        # platform, and if we need to update it. At this point the system_patient_id can be 3 possible values:
        # 1. value we already had stored in Canvas in an external identifier,
        # 2. value we just got from our partner GET API lookup, or
        # 3. None
        # And we have a true/false call to action telling us if we need to add
        # an external identifier to our Canvas patient: `update_patient_external_identifier`

        # Generate the payload for creating or updating the patient in partner platform API
        partner_payload = {
            "externalId": canvas_patient.id,
            "firstName": canvas_patient.first_name,
            "lastName": canvas_patient.last_name,
            "dateOfBirth": canvas_patient.birth_date.isoformat(),
        }

        base_request_url = f"{self.partner_api_base_url}/patients/v2"

        # If we have a patient's partner external id, we know this is an update, so we'll append it to the request URL
        request_url = (
            f"{base_request_url}/{system_patient_id}" if system_patient_id else base_request_url
        )
        resp = http.post(request_url, json=partner_payload, headers=self.partner_request_headers)

        # If your system's API returns the ID of the newly created record,
        # grab it from the response so we can add it to the Canvas patient record
        if system_patient_id is None:
            system_patient_id = resp.json().get("id")

        duplicate_patient_attempt = resp.status_code == 409

        if duplicate_patient_attempt:
            # If your system's API can let you know when a duplicate record was attempted to be added,
            # you can use that information to return early here.
            return []
        elif update_patient_external_identifier:
            # Queue up an effect to update the patient in Canvas and add the external identifier
            external_id = CreatePatientExternalIdentifier(
                patient_id=canvas_patient.id,
                system=PARTNER_URL_BASE,
                value=str(system_patient_id)
            )
            return [external_id.create()]
        else:
            return [] # Done!
