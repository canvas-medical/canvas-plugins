from typing import TypedDict, cast
from urllib.parse import urlencode

from canvas_sdk.caching.plugins import get_cache
from canvas_sdk.utils.http import Http


class Credentials(TypedDict):
    """Credentials for the Canvas FHIR API."""

    access_token: str
    expires_in: int
    refresh_token: str
    scope: str
    token_type: str


class CanvasFhir:
    """Client for interacting with the Canvas FHIR API."""

    def __init__(self, client_id: str, client_secret: str, customer_identifier: str):
        """Initializes the Canvas FHIR client."""
        self._client_id = client_id
        self._client_secret = client_secret
        self._customer_identifier = customer_identifier

        self._credentials = self._get_credentials()
        self._base_url = f"https://fumage-{self._customer_identifier}.canvasmedical.com"

    def create(self, resource_type: str, data: dict) -> dict:
        """Creates a resource via the FHIR API."""
        response = Http().post(
            f"{self._base_url}/{resource_type}",
            headers=self._get_headers(),
            json=data,
        )

        response.raise_for_status()

        return response.json()

    def read(self, resource_type: str, resource_id: str) -> dict:
        """Reads a resource via the FHIR API."""
        response = Http().get(
            f"{self._base_url}/{resource_type}/{resource_id}",
            headers=self._get_headers(),
        )

        response.raise_for_status()

        return response.json()

    def search(self, resource_type: str, parameters: dict) -> dict:
        """Searches for resources via the FHIR API."""
        query_string = urlencode(parameters)

        response = Http().get(
            f"{self._base_url}/{resource_type}?{query_string}",
            headers=self._get_headers(),
        )

        response.raise_for_status()

        return response.json()

    def update(self, resource_type: str, resource_id: str, data: dict) -> dict:
        """Updates a resource via the FHIR API."""
        response = Http().put(
            f"{self._base_url}/{resource_type}/{resource_id}",
            headers=self._get_headers(),
            json=data,
        )

        response.raise_for_status()

        return response.json()

    def _get_headers(self) -> dict:
        """Returns the headers for the FHIR API request."""
        return {
            "Authorization": f"Bearer {self._credentials['access_token']}",
            "Content-Type": "application/json",
        }

    def _get_credentials(self) -> Credentials:
        """Retrieves the credentials from the Canvas API."""
        cache = get_cache()
        key = f"canvas_fhir_credentials_{self._customer_identifier}"

        cached_credentials = cache.get(key)

        if cached_credentials:
            return cast(Credentials, cached_credentials)

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = urlencode(
            {
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            }
        )

        response = Http().post(
            f"https://{self._customer_identifier}.canvasmedical.com/auth/token/",
            headers=headers,
            data=data,
        )

        response.raise_for_status()

        response_json = response.json()

        cache.set(key, response_json, timeout_seconds=response_json["expires_in"] - 60)

        return cast(Credentials, response_json)


__exports__ = ("CanvasFhir",)
