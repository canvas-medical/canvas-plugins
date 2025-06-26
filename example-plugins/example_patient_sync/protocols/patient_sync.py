from typing import Any

from canvas_sdk.effects import Effect
from canvas_sdk.effects.patient import CreatePatientExternalIdentifier
from canvas_sdk.effects.banner_alert import AddBannerAlert
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from canvas_sdk.utils import Http
from canvas_sdk.v1.data.patient import Patient
from logger import log

PARTNER_URL_BASE = "https://app.usebridge.xyz"
SYSTEM_URL = "https://canvas.app.usebridge.xyz"


class PatientSync(BaseProtocol):
    """Protocol for synchronizing patient data between systems."""

    RESPONDS_TO = [
        EventType.Name(EventType.PATIENT_CREATED),
    ]

    @property
    def partner_api_base_url(self) -> str:
        """Return the base URL for the external partner API."""
        return self.sanitize_url(self.secrets["PARTNER_API_BASE_URL"] or f"{PARTNER_URL_BASE}/api")

    @property
    def partner_ui_base_url(self) -> str:
        """Return the base URL for the external partner UI."""
        return self.sanitize_url(self.secrets["PARTNER_UI_BASE_URL"] or PARTNER_URL_BASE)

    @property
    def partner_request_headers(self) -> dict[str, str]:
        """Return the request headers for external partner API requests."""
        partner_secret_api_key = self.secrets["PARTNER_SECRET_API_KEY"]
        return {"X-API-Key": partner_secret_api_key}

    @property
    def partner_patient_metadata(self) -> Any:
        """Return metadata for creation of the patient on external partner platform."""
        metadata = {"canvasPatientId": self.target}

        canvas_url = self.secrets["CANVAS_BASE_URL"]
        if canvas_url:
            metadata["canvasUrl"] = canvas_url

        return metadata

    def get_system_id(self, canvas_patient: Patient, system: str) -> str | None:
        """Get the system ID for a given patient and system from Canvas."""
        # If the patient already has a external identifier for the partner platform, identified by the system url, use the first one
        return (
            canvas_patient.external_identifiers.filter(system=system)
            .values_list("value", flat=True)
            .first()
        )

    def system_patient_lookup(self, canvas_patient_id: str) -> Any:
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

        existing_partner_id = self.get_system_id(canvas_patient, SYSTEM_URL)
        partner_patient_id = existing_partner_id
        update_patient_external_identifier = False

        # check if partner external ID already exists and needs to be added to the model
        if not existing_partner_id and canvas_patient_id is not None:
            # Get the partner external ID by seeing if they have a record in partner platform
            get_system_patient = self.system_patient_lookup(canvas_patient_id)

            partner_patient_id = (
                get_system_patient.json()["id"] if get_system_patient.status_code == 200 else None
            )
            update_patient_external_identifier = bool(partner_patient_id)

        # Great, now we know 1) if the patient is assigned a partner external ID and 2) if we need to update it.
        # At this point it can be 3 values: value we have stored in Canvas, value we just got from our GET API lookup, or None
        # all stored in `partner_patient_id` with a bool call to action: `update_patient_external_identifier`

        # Generate the payload for creating or updating the patient in partner platform API
        # regardless of the event type (create or update)
        partner_payload = {
            "externalId": canvas_patient.id,
            "firstName": canvas_patient.first_name,
            "lastName": canvas_patient.last_name,
            "dateOfBirth": canvas_patient.birth_date.isoformat(),
        }
        # Add placeholder email when creating the patient if it's required
        partner_payload["email"] = f"patient_{canvas_patient.id}@canvasmedical.com"
        partner_payload["metadata"] = self.partner_patient_metadata

        base_request_url = f"{self.partner_api_base_url}/patients/v2"

        # If we HAVE a patient's partner external id, we know this is an update, so we'll append it to the request URL
        request_url = (
            f"{base_request_url}/{partner_patient_id}" if partner_patient_id else base_request_url
        )

        log.info(f">>> Partner platform API request URL: {request_url}")
        log.info(f">>> Partner platform API patient payload: json={partner_payload}")
        log.info(
            f">>> Partner platform API request headers: headers={self.partner_request_headers}"
        )

        resp = http.post(request_url, json=partner_payload, headers=self.partner_request_headers)

        partner_patient_exists = resp.status_code == 409

        if partner_patient_exists:
            log.info(
                f">>> Patient already exists in {PARTNER_URL_BASE} for Canvas Patient ID {canvas_patient_id}"
            )
            return []
        elif update_patient_external_identifier:
            # queue up an effect to update the patient in canvas and add the external ID
            external_id = CreatePatientExternalIdentifier(
                patient_id=canvas_patient.id,
                system=PARTNER_URL_BASE,
                value=str(partner_patient_id)
            )
            return [external_id.create()]
        else:
            return [] # Done


    def sanitize_url(self, url: str) -> str:
        """Remove a trailing slash from a URL if present."""
        # Remove a trailing forward slash since our request paths will start with '/'
        return url[:-1] if url[-1] == "/" else url
