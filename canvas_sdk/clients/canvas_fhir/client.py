from typing import TypedDict, cast
from urllib.parse import urlencode

from requests import Response

from canvas_sdk.caching.plugins import get_cache
from canvas_sdk.utils.http import Http
from settings import CUSTOMER_IDENTIFIER


class Credentials(TypedDict):
    """Credentials for the Canvas FHIR API."""

    access_token: str
    expires_in: int
    refresh_token: str
    scope: str
    token_type: str


class CanvasFhir:
    """Client for interacting with the Canvas FHIR API."""

    def __init__(self, client_id: str, client_secret: str):
        """Initializes the Canvas FHIR client."""
        self._client_id = client_id
        self._client_secret = client_secret

        self._credentials = self._get_credentials()
        self._base_url = f"https://fumage-{CUSTOMER_IDENTIFIER}.canvasmedical.com"

    def create(self, resource_type: str, data: dict) -> dict:
        """Creates a resource via the FHIR API."""
        response = Http().post(
            f"{self._base_url}/{resource_type}",
            headers=self._get_headers(),
            json=data,
        )

        response.raise_for_status()

        return self._write_result(response)

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

        return self._write_result(response)

    @staticmethod
    def _write_result(response: Response) -> dict:
        """Return the response body, or the id from the ``Location`` header when it is empty.

        FHIR create/update respond with ``201``/``200`` and an empty body, putting the new
        resource id in the ``Location`` header (``/<type>/<id>``). Calling ``response.json()``
        on that empty content raises ``JSONDecodeError`` even though the write succeeded.
        """
        if response.content:
            parsed = response.json()
            if isinstance(parsed, dict):
                return parsed

        location = response.headers.get("Location", "")
        resource_id = location.rstrip("/").rsplit("/", 1)[-1] if location else ""
        return {"id": resource_id} if resource_id else {}

    def _get_headers(self) -> dict:
        """Returns the headers for the FHIR API request."""
        return {
            "Authorization": f"Bearer {self._credentials['access_token']}",
            "Content-Type": "application/json",
        }

    def _get_credentials(self) -> Credentials:
        """Retrieves the credentials from the Canvas API."""
        cache = get_cache()
        key = f"canvas_fhir_credentials_{self._client_id}"

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
            f"https://{CUSTOMER_IDENTIFIER}.canvasmedical.com/auth/token/",
            headers=headers,
            data=data,
        )

        response.raise_for_status()

        response_json = response.json()

        cache.set(key, response_json, timeout_seconds=response_json["expires_in"] - 60)

        return cast(Credentials, response_json)


__exports__ = ()
