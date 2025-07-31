"""
FHIR Client for Canvas Medical API Integration
"""

import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from logger import log
from canvas_sdk.v1.data import PracticeLocation

# [Chat: 2025-01-31] Created FHIR client for future Canvas Medical API integration


class FHIRClient:
    """
    FHIR client for interacting with Canvas Medical FHIR API endpoints.
    """

    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        """
        Initialize FHIR client.

        Args:
            base_url: The base URL for the FHIR API
            api_key: Bearer token for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout
        self.headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {api_key}",
            "content-type": "application/json",
        }
        log.info(f"PDMP3: FHIR Client initialized for {self.base_url}")

    def _make_request(
        self, method: str, resource: str, data: Optional[Dict] = None, params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make a FHIR API request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            resource: FHIR resource path
            data: Request payload data
            params: Query parameters

        Returns:
            Dict containing response data and metadata
        """
        url = self.base_url + resource.lstrip("/")

        log.info(f"PDMP3: Making {method} request to {url}")
        log.debug(f"PDMP3: Request headers: {self.headers}")

        try:
            if method.upper() == "GET":
                response = requests.get(
                    url, headers=self.headers, params=params, timeout=self.timeout
                )
            elif method.upper() == "POST":
                response = requests.post(
                    url, json=data, headers=self.headers, params=params, timeout=self.timeout
                )
            elif method.upper() == "PUT":
                response = requests.put(
                    url, json=data, headers=self.headers, params=params, timeout=self.timeout
                )
            elif method.upper() == "DELETE":
                response = requests.delete(
                    url, headers=self.headers, params=params, timeout=self.timeout
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            log.info(f"PDMP3: FHIR {method} request completed - Status: {response.status_code}")

            result = {
                "status": "success" if 200 <= response.status_code < 300 else "error",
                "status_code": response.status_code,
                "response_headers": dict(response.headers),
                "url": url,
                "method": method,
            }

            # Try to parse JSON response
            try:
                result["data"] = response.json()
            except ValueError:
                result["response_text"] = response.text

            return result

        except Exception as e:
            log.error(f"PDMP3: FHIR {method} request failed: {e}")
            return {"status": "error", "error": str(e), "url": url, "method": method}

    def get_patient(self, patient_id: str) -> Dict[str, Any]:
        """
        Get patient resource by ID.

        Args:
            patient_id: Canvas patient ID

        Returns:
            Dict containing patient data or error information
        """
        return self._make_request("GET", f"Patient/{patient_id}")

    def search_patients(self, **search_params) -> Dict[str, Any]:
        """
        Search for patients using FHIR search parameters.

        Args:
            **search_params: FHIR search parameters (name, birthdate, etc.)

        Returns:
            Dict containing search results or error information
        """
        return self._make_request("GET", "Patient", params=search_params)

    def create_appointment(
        self,
        patient_id: str,
        practitioner_id: str,
        start_time: Optional[datetime] = None,
        duration_minutes: int = 20,
        reason_for_visit: str = "PDMP consultation",
    ) -> Dict[str, Any]:
        """
        Create an appointment resource.

        Args:
            patient_id: Canvas patient ID
            practitioner_id: Canvas practitioner ID
            start_time: Appointment start time (defaults to now)
            duration_minutes: Appointment duration in minutes
            reason_for_visit: Reason for the visit

        Returns:
            Dict containing appointment creation response
        """
        if start_time is None:
            start_time = datetime.now(timezone.utc)

        formatted_start_time = start_time.strftime("%Y-%m-%dT%H:%M:00.000Z")
        formatted_end_time = (start_time + timedelta(minutes=duration_minutes)).strftime(
            "%Y-%m-%dT%H:%M:00.000Z"
        )

        # Get location from Canvas
        try:
            location_id = str(PracticeLocation.objects.filter(active=True).first().id)
        except Exception as e:
            log.warning(f"PDMP3: Could not get practice location: {e}")
            location_id = "1"  # Default fallback

        payload = {
            "resourceType": "Appointment",
            "status": "booked",
            "appointmentType": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "308335008",
                        "display": "Office visit",
                    }
                ]
            },
            "reasonCode": [{"text": reason_for_visit}],
            "supportingInformation": [{"reference": f"Location/{location_id}"}],
            "start": formatted_start_time,
            "end": formatted_end_time,
            "participant": [
                {"actor": {"reference": f"Patient/{patient_id}"}, "status": "accepted"},
                {"actor": {"reference": f"Practitioner/{practitioner_id}"}, "status": "accepted"},
            ],
        }

        log.debug(f"PDMP3: Creating appointment with payload: {payload}")
        return self._make_request("POST", "Appointment", data=payload)

    def create_encounter(
        self, patient_id: str, practitioner_id: str, encounter_type: str = "Office visit"
    ) -> Dict[str, Any]:
        """
        Create an encounter resource.

        Args:
            patient_id: Canvas patient ID
            practitioner_id: Canvas practitioner ID
            encounter_type: Type of encounter

        Returns:
            Dict containing encounter creation response
        """
        # Get location from Canvas
        try:
            location_id = str(PracticeLocation.objects.filter(active=True).first().id)
        except Exception as e:
            log.warning(f"PDMP3: Could not get practice location: {e}")
            location_id = "1"  # Default fallback

        start_time = datetime.now(timezone.utc)
        formatted_start_time = start_time.strftime("%Y-%m-%dT%H:%M:00.000Z")

        payload = {
            "resourceType": "Encounter",
            "status": "in-progress",
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "AMB",
                "display": "ambulatory",
            },
            "type": [
                {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": "308335008",
                            "display": encounter_type,
                        }
                    ]
                }
            ],
            "subject": {"reference": f"Patient/{patient_id}"},
            "participant": [{"individual": {"reference": f"Practitioner/{practitioner_id}"}}],
            "period": {"start": formatted_start_time},
            "serviceProvider": {"reference": f"Organization/{location_id}"},
        }

        log.debug(f"PDMP3: Creating encounter with payload: {payload}")
        return self._make_request("POST", "Encounter", data=payload)

    def get_practitioner(self, practitioner_id: str) -> Dict[str, Any]:
        """
        Get practitioner resource by ID.

        Args:
            practitioner_id: Canvas practitioner ID

        Returns:
            Dict containing practitioner data or error information
        """
        return self._make_request("GET", f"Practitioner/{practitioner_id}")

    def search_observations(self, patient_id: str, code: Optional[str] = None) -> Dict[str, Any]:
        """
        Search for observations for a specific patient.

        Args:
            patient_id: Canvas patient ID
            code: Optional observation code to filter by

        Returns:
            Dict containing observation search results
        """
        search_params = {"patient": patient_id}
        if code:
            search_params["code"] = code

        return self._make_request("GET", "Observation", params=search_params)


class CanvasAPIClient:
    """
    Client for Canvas Medical's proprietary API endpoints (non-FHIR).
    """

    def __init__(self, subdomain: str, client_id: str, client_secret: str):
        """
        Initialize Canvas API client.

        Args:
            subdomain: Canvas subdomain
            client_id: API client ID
            client_secret: API client secret
        """
        self.base_url = f"https://{subdomain}.canvasmedical.com/"
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None
        log.info(f"PDMP3: Canvas API Client initialized for {self.base_url}")

    def get_token(self) -> str:
        """
        Get OAuth token for Canvas API authentication.

        Returns:
            Access token string
        """
        if self.token:
            return self.token

        url = self.base_url + "auth/token/"
        payload = f"grant_type=client_credentials&client_id={self.client_id}&client_secret={self.client_secret}"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        log.info("PDMP3: Requesting Canvas API token")

        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            json_resp = response.json()
            self.token = json_resp["access_token"]
            log.info("PDMP3: Canvas API token obtained successfully")
            return self.token
        except Exception as e:
            log.error(f"PDMP3: Failed to get Canvas API token: {e}")
            raise

    def create_note(
        self, patient_id: str, practitioner_id: str, note_type: str = "Office visit"
    ) -> Dict[str, Any]:
        """
        Create a note via Canvas API.

        Args:
            patient_id: Canvas patient ID
            practitioner_id: Canvas practitioner ID
            note_type: Type of note to create

        Returns:
            Dict containing note creation response
        """
        url = self.base_url + "core/api/notes/v1/Note"
        headers = {
            "Authorization": f"Bearer {self.get_token()}",
            "Content-Type": "application/json",
        }

        # Get location from Canvas
        try:
            location_id = str(PracticeLocation.objects.filter(active=True).first().id)
        except Exception as e:
            log.warning(f"PDMP3: Could not get practice location: {e}")
            location_id = "1"  # Default fallback

        start_time = datetime.now(timezone.utc)
        formatted_start_time = start_time.strftime("%Y-%m-%dT%H:%M:00.000Z")

        payload = {
            "patientKey": patient_id,
            "providerKey": practitioner_id,
            "practiceLocationKey": location_id,
            "noteTypeName": note_type,
            "encounterStartTime": formatted_start_time,
        }

        log.info(f"PDMP3: Creating note via Canvas API")
        log.debug(f"PDMP3: Note payload: {payload}")

        try:
            response = requests.post(url, headers=headers, json=payload)
            return {
                "status": "success" if 200 <= response.status_code < 300 else "error",
                "status_code": response.status_code,
                "response_text": response.text,
                "response_headers": dict(response.headers),
            }
        except Exception as e:
            log.error(f"PDMP3: Failed to create note: {e}")
            return {"status": "error", "error": str(e)}
