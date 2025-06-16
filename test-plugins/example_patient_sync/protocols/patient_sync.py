import json
from typing import Any

from canvas_sdk.effects import Effect
from canvas_sdk.effects.banner_alert import AddBannerAlert
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from canvas_sdk.utils import Http
from canvas_sdk.v1.data.patient import Patient
from logger import log

BRIDGE_SANDBOX = "https://app.usebridge.xyz"


class PatientSync(BaseProtocol):
    """Protocol for synchronizing patient data between systems."""

    RESPONDS_TO = [
        EventType.Name(EventType.PATIENT_CREATED),
        EventType.Name(EventType.PATIENT_UPDATED),
    ]

    @property
    def bridge_api_base_url(self) -> str:
        """Return the base URL for the Bridge API."""
        return self.sanitize_url(self.secrets["BRIDGE_API_BASE_URL"] or f"{BRIDGE_SANDBOX}/api")

    @property
    def bridge_ui_base_url(self) -> str:
        """Return the base URL for the Bridge UI."""
        return self.sanitize_url(self.secrets["BRIDGE_UI_BASE_URL"] or BRIDGE_SANDBOX)

    @property
    def bridge_request_headers(self) -> dict[str, str]:
        """Return the request headers for Bridge API requests."""
        bridge_secret_api_key = self.secrets["BRIDGE_SECRET_API_KEY"]
        return {"X-API-Key": bridge_secret_api_key}

    @property
    def bridge_patient_metadata(self) -> dict[str, str | None]:
        """Return metadata for the Bridge patient."""
        metadata = {"canvasPatientId": self.get_patient_id()}

        canvas_url = self.secrets["CANVAS_BASE_URL"]
        if canvas_url:
            metadata["canvasUrl"] = canvas_url

        return metadata

    def get_patient_id(self) -> str | None:
        """Get the patient ID from the event."""
        if self.event.type in [EventType.PATIENT_CREATED, EventType.PATIENT_UPDATED]:
            return self.target
        return None

    def get_system_id(self, canvas_patient: Patient, system: str) -> str | None:
        """Get the system ID for a given patient and system."""
        # If the patient already has a system external identifier, use the first one
        if canvas_patient.external_identifiers.filter(system=system).count() > 0:
            return canvas_patient.external_identifiers.filter(system=system)[0].value
        return None

    def system_patient_lookup(self, canvas_patient_id: str) -> Any:
        """Look up a patient in the external system."""
        http = Http()
        return http.get(
            f"{self.bridge_api_base_url}/patients/v2/{canvas_patient_id}",
            headers=self.bridge_request_headers,
        )

    def compute(self) -> list[Effect]:
        """Compute the sync actions for the patient."""
        event_type = self.event.type
        canvas_patient_id = self.get_patient_id()

        log.info(f">>> PatientSync.compute {EventType.Name(event_type)} for {canvas_patient_id}")

        http = Http()

        canvas_patient = Patient.objects.get(id=canvas_patient_id)

        existing_system_id = self.get_system_id(canvas_patient, "Bridge")
        system_patient_id = existing_system_id if existing_system_id else None
        log.info(f">>> Existing system patient ID: {system_patient_id}")

        update_patient_external_identifier = False
        # if it's a patient update, check if external system ID exists and needs to be added to the model
        if (
            event_type in [EventType.PATIENT_UPDATED]
            and not system_patient_id
            and canvas_patient_id is not None
        ):
            # Get the third party ID by seeing if they exist in third party
            get_system_patient = self.system_patient_lookup(canvas_patient_id)

            system_patient_id = (
                get_system_patient.json()["id"] if get_system_patient.status_code == 200 else None
            )
            update_patient_external_identifier = bool(system_patient_id)

        # Great, now we know if the patient has a third party ID and if we need to update it.
        # At this point it can be 3 values: None, value from Canvas, or value from third party
        # all stored in `system_patient_id` with a bool call to action: `update_patient_external_identifier`

        # If they still don't have a third party ID, they don't exist and we need to create them.
        # So existing plugin says to change the event type. (?)
        if not system_patient_id and event_type in [EventType.PATIENT_UPDATED]:
            log.info(">>> Missing third party patient for update; trying create instead")
            event_type = EventType.PATIENT_CREATED

        # Generate the payload for creating or updating the patient in third party API
        # regardless of the event type (create or update)
        bridge_payload = {
            "externalId": canvas_patient.id,
            "firstName": canvas_patient.first_name,
            "lastName": canvas_patient.last_name,
            "dateOfBirth": canvas_patient.birth_date.isoformat(),
        }

        if event_type == EventType.PATIENT_CREATED:
            # Add placeholder email when creating the Bridge patient since it's required
            bridge_payload["email"] = "patient_" + canvas_patient.id + "@canvasmedical.com"
            bridge_payload["metadata"] = json.dumps(self.bridge_patient_metadata)

        base_request_url = f"{self.bridge_api_base_url}/patients/v2"

        # If we HAVE a Bridge patient id, we know this is an update, so we'll append it to the request URL
        request_url = (
            f"{base_request_url}/{system_patient_id}" if system_patient_id else base_request_url
        )

        log.info(f">>> Bridge request URL: {request_url}")
        log.info(f">>> Bridge patient payload: json={bridge_payload}")
        log.info(f">>> Bridge request headers: headers={self.bridge_request_headers}")

        resp = http.post(request_url, json=bridge_payload, headers=self.bridge_request_headers)

        bridge_patient_exists = resp.status_code == 409

        if event_type == EventType.PATIENT_CREATED and bridge_patient_exists:
            log.info(f">>> Bridge patient already exists for {canvas_patient_id}")
            return []
        elif update_patient_external_identifier:
            # TODO: enable this functionality when KOALA-2956 is implemented
            # queue up an effect to update the patient in canvas and add the external ID
            log.info(
                f">>> Call PatientExternalIdentifierEffect to add system external identifier {system_patient_id} to patient"
            )
            # external_id = PatientExternalIdentifierEffect(
            #     patient_id=canvas_patient.id
            #     system="Bridge"
            #     value=system_patient_id
            # )
            # external_id.create()

        # If the post is unsuccessful, notify end users
        # TODO: implement workflow to remedy this,
        # TODO: e.g. end user manually completes a questionnaire with the Bridge link?
        if resp.status_code != 200:
            log.error(f"bridge-patient-sync FAILED with status {resp.status_code}")
            log.info(resp.text)
            sync_warning = AddBannerAlert(
                patient_id=canvas_patient.id,
                key="bridge-patient-sync",
                narrative="No link to patient in Bridge",
                placement=[
                    AddBannerAlert.Placement.CHART,
                    AddBannerAlert.Placement.APPOINTMENT_CARD,
                    AddBannerAlert.Placement.SCHEDULING_CARD,
                    AddBannerAlert.Placement.PROFILE,
                ],
                intent=AddBannerAlert.Intent.WARNING,
            )
            return [sync_warning.apply()]

        # Otherwise, get the resulting patient info and build the link to Bridge
        bridge_patient_data = resp.json()
        log.info(f">>> Bridge patient data: {bridge_patient_data}")

        sync_banner = AddBannerAlert(
            patient_id=canvas_patient.id,
            key="bridge-patient-sync",
            narrative="View patient in Bridge",
            placement=[
                AddBannerAlert.Placement.CHART,
                AddBannerAlert.Placement.APPOINTMENT_CARD,
                AddBannerAlert.Placement.SCHEDULING_CARD,
                AddBannerAlert.Placement.PROFILE,
            ],
            intent=AddBannerAlert.Intent.INFO,
            href=f"{self.bridge_ui_base_url}/patients/{bridge_patient_data['id']}",
        )

        return [sync_banner.apply()]

    def sanitize_url(self, url: str) -> str:
        """Remove a trailing slash from a URL if present."""
        # Remove a trailing forward slash since our request paths will start with '/'
        return url[:-1] if url[-1] == "/" else url
