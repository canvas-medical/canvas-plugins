import concurrent
import functools
import logging
import os
import ssl
import urllib.parse
from collections.abc import Callable, Iterable, Mapping
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Literal, Protocol, TypeVar

import requests
from requests.adapters import HTTPAdapter
from requests.utils import DEFAULT_CA_BUNDLE_PATH

from canvas_sdk.utils.metrics import measured

F = TypeVar("F", bound=Callable)

logger = logging.getLogger("plugin_runner_logger")


class _BatchableRequest:
    """Representation of a request that will be executed in parallel with other requests."""

    def __init__(
        self,
        method: Literal["GET", "POST", "PUT", "PATCH"],
        url: str,
        **kwargs: Any,
    ) -> None:
        self._method = method
        self._url = url
        self._kwargs = kwargs

    def fn(self, client: "Http") -> Callable:
        """
        Return a callable constructed from an Http object and the method, URL, and kwargs.

        The callable is passed to the ThreadPoolExecutor.
        """
        client_method: Callable
        match self._method:
            case "GET":
                client_method = client.get
            case "POST":
                client_method = client.post
            case "PUT":
                client_method = client.put
            case "PATCH":
                client_method = client.patch
            case _:
                raise ValueError(f"HTTP method {self._method} is not supported")

        return functools.partial(client_method, self._url, **self._kwargs)


class BatchableRequest(Protocol):
    """Protocol for batchable requests."""

    def fn(self, client: "Http") -> Callable:
        """
        Return a callable that can be passed to the ThreadPoolExecutor.
        """
        ...


def batch_get(
    url: str,
    headers: Mapping[str, str | bytes | None] | None = None,
) -> BatchableRequest:
    """Return a batchable GET request."""
    return _BatchableRequest("GET", url, headers=headers)


def batch_post(
    url: str,
    json: dict | None = None,
    data: dict | str | list | bytes | None = None,
    headers: Mapping[str, str | bytes | None] | None = None,
) -> BatchableRequest:
    """Return a batchable POST request."""
    return _BatchableRequest("POST", url, json=json, data=data, headers=headers)


def batch_put(
    url: str,
    json: dict | None = None,
    data: dict | str | list | bytes | None = None,
    headers: Mapping[str, str | bytes | None] | None = None,
) -> BatchableRequest:
    """Return a batchable PUT request."""
    return _BatchableRequest("PUT", url, json=json, data=data, headers=headers)


def batch_patch(
    url: str,
    json: dict | None = None,
    data: dict | str | list | bytes | None = None,
    headers: Mapping[str, str | bytes | None] | None = None,
) -> BatchableRequest:
    """Return a batchable PATCH request."""
    return _BatchableRequest("PATCH", url, json=json, data=data, headers=headers)


_DEFAULT_PORTS = {"http": 80, "https": 443}

# The Surescripts root and subordinate CAs, the same bundle the pharmacy service loads from
# its SURESCRIPTS_CERTIFICATE_CA setting.
SURESCRIPTS_CA_BUNDLE = os.path.join(os.path.dirname(__file__), "surescripts-ca.pem")


class _SurescriptsTrustAdapter(HTTPAdapter):
    """Verifies TLS against the public roots `requests` uses plus the Surescripts CAs.

    The production pharmacy service presents a certificate issued by Surescripts' own CA,
    which no public trust store carries; the staging service presents a public one.
    """

    def __init__(self) -> None:
        self.ssl_context = ssl.create_default_context(cafile=DEFAULT_CA_BUNDLE_PATH)
        self.ssl_context.load_verify_locations(cafile=SURESCRIPTS_CA_BUNDLE)
        super().__init__()

    def init_poolmanager(
        self,
        connections: int,
        maxsize: int,
        block: bool = False,
        **pool_kwargs: Any,
    ) -> None:
        pool_kwargs["ssl_context"] = self.ssl_context
        super().init_poolmanager(connections, maxsize, block, **pool_kwargs)  # type: ignore[no-untyped-call]


def _origin(parts: urllib.parse.SplitResult) -> tuple[str, str | None, int | None]:
    return (
        parts.scheme,
        parts.hostname,
        parts.port or _DEFAULT_PORTS.get(parts.scheme),
    )


def _is_under(url: str, base_url: str) -> bool:
    """Whether `url` is on the same origin as `base_url` and at or under its path."""
    url_parts = urllib.parse.urlsplit(url)
    base_parts = urllib.parse.urlsplit(base_url)

    if url_parts.username is not None or url_parts.password is not None:
        return False

    if _origin(url_parts) != _origin(base_parts):
        return False

    base_path = base_parts.path.rstrip("/")

    return url_parts.path == base_path or url_parts.path.startswith(f"{base_path}/")


def _require_service_path(path: str) -> None:
    """Refuse anything but a plain path on the client's own service.

    Applies to the service clients: no scheme or host of its own, no backslashes, and no
    dot segments, encoded or not, that a server could resolve to a different endpoint.
    """
    parts = urllib.parse.urlsplit(path)

    if parts.scheme or parts.netloc or path.startswith("//") or "\\" in path:
        raise ValueError("Only a path on this service may be requested with this client.")

    if any(urllib.parse.unquote(segment) in (".", "..") for segment in parts.path.split("/")):
        raise ValueError("Only a path on this service may be requested with this client.")


class Http:
    """A helper class for completing HTTP calls with metrics tracking."""

    _MAX_REQUEST_TIMEOUT_SECONDS = 30

    _base_url: str
    _session: requests.Session

    def join_url(self, url: str) -> str:
        """
        Join a URL to the base_url.

        With a base URL, the result must share its scheme, host and port, carry no
        userinfo, and sit at or under its path.
        """
        joined = urllib.parse.urljoin(self._base_url, url)

        if self._base_url and not _is_under(joined, self._base_url):
            raise ValueError("You may not access other URLs using this client.")

        return joined

    def __init__(self, base_url: str = "") -> None:
        self._base_url = base_url
        self._session = requests.Session()

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "_MAX_REQUEST_TIMEOUT_SECONDS":
            logger.warning(
                "Overriding %s._MAX_REQUEST_TIMEOUT_SECONDS is deprecated and will be "
                "forbidden in a future release. Use the timeout parameter on individual "
                "requests instead.",
                type(self).__name__,
            )
        super().__setattr__(name, value)

    @measured(track_plugins_usage=True)
    def get(
        self,
        url: str,
        headers: Mapping[str, str | bytes | None] | None = None,
    ) -> requests.Response:
        """Sends a GET request."""
        if headers is None:
            headers = {}
        return self._session.get(
            self.join_url(url),
            headers=headers,
            timeout=self._MAX_REQUEST_TIMEOUT_SECONDS,
        )

    @measured(track_plugins_usage=True)
    def post(
        self,
        url: str,
        json: dict | None = None,
        data: dict | str | list | bytes | None = None,
        headers: Mapping[str, str | bytes | None] | None = None,
    ) -> requests.Response:
        """Sends a POST request."""
        return self._session.post(
            self.join_url(url),
            json=json,
            data=data,
            headers=headers,
            timeout=self._MAX_REQUEST_TIMEOUT_SECONDS,
        )

    @measured(track_plugins_usage=True)
    def put(
        self,
        url: str,
        json: dict | None = None,
        data: dict | str | list | bytes | None = None,
        headers: Mapping[str, str | bytes | None] | None = None,
    ) -> requests.Response:
        """Sends a PUT request."""
        return self._session.put(
            self.join_url(url),
            json=json,
            data=data,
            headers=headers,
            timeout=self._MAX_REQUEST_TIMEOUT_SECONDS,
        )

    @measured(track_plugins_usage=True)
    def patch(
        self,
        url: str,
        json: dict | None = None,
        data: dict | str | list | bytes | None = None,
        headers: Mapping[str, str | bytes | None] | None = None,
    ) -> requests.Response:
        """Sends a PATCH request."""
        return self._session.patch(
            self.join_url(url),
            json=json,
            data=data,
            headers=headers,
            timeout=self._MAX_REQUEST_TIMEOUT_SECONDS,
        )

    @measured(track_plugins_usage=True)
    def delete(
        self,
        url: str,
        headers: Mapping[str, str | bytes | None] | None = None,
    ) -> requests.Response:
        """Sends a DELETE request."""
        if headers is None:
            headers = {}
        return self._session.delete(
            self.join_url(url),
            headers=headers,
            timeout=self._MAX_REQUEST_TIMEOUT_SECONDS,
        )

    @measured(track_plugins_usage=True)
    def batch_requests(
        self,
        batch_requests: Iterable[BatchableRequest],
        timeout: int | None = None,
    ) -> list[requests.Response]:
        """
        Execute requests in parallel.

        Wait for the responses to complete, and then return a list of the responses in the same
        ordering as the requests.
        """
        if timeout is None:
            timeout = self._MAX_REQUEST_TIMEOUT_SECONDS
        elif timeout < 1 or timeout > self._MAX_REQUEST_TIMEOUT_SECONDS:
            raise ValueError(
                "Timeout value must be greater than 0 and less than or equal "
                f"to {self._MAX_REQUEST_TIMEOUT_SECONDS} seconds"
            )

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(request.fn(self)) for request in batch_requests]

            concurrent.futures.wait(futures, timeout=timeout)

            return [future.result() for future in futures]


class JsonOnlyResponse:
    """
    A very simple Response analog that only allows access to the json() method
    and the status_code.

    If we returned the response directly the user could look at the request
    headers on the response object and see any authentication headers we sent
    on their behalf.
    """

    _json: dict[str, Any] | None
    status_code: int

    def __init__(self, response: requests.Response):
        self.status_code = response.status_code

        try:
            self._json = response.json()
        except Exception:
            self._json = None

    def json(self) -> dict[str, Any] | None:
        return self._json


class ServiceClient:
    """
    Base for the SDK clients that call Canvas services with service credentials.

    The `Http` client is held privately rather than inherited, so plugin code reaches only
    the purpose-built methods each subclass lists in `__exports__`. Requests go only to plain
    paths on the service, and a failed request is re-raised as a plain `RequestException`.
    """

    __exports__: tuple[str, ...] = ()

    _http_client: Http

    def __init__(self, base_url: str) -> None:
        http_client = Http(base_url=base_url)
        http_client._session.headers.update({"Authorization": os.getenv("PRE_SHARED_KEY", "")})
        object.__setattr__(self, "_http_client", http_client)

    @property
    def _MAX_REQUEST_TIMEOUT_SECONDS(self) -> float:
        return self._http_client._MAX_REQUEST_TIMEOUT_SECONDS

    @_MAX_REQUEST_TIMEOUT_SECONDS.setter
    def _MAX_REQUEST_TIMEOUT_SECONDS(self, value: float) -> None:
        logger.warning(
            "Overriding %s._MAX_REQUEST_TIMEOUT_SECONDS is deprecated and will be "
            "forbidden in a future release. Use the timeout parameter on individual "
            "requests instead.",
            type(self).__name__,
        )
        object.__setattr__(self._http_client, "_MAX_REQUEST_TIMEOUT_SECONDS", value)

    @_MAX_REQUEST_TIMEOUT_SECONDS.deleter
    def _MAX_REQUEST_TIMEOUT_SECONDS(self) -> None:
        object.__delattr__(self._http_client, "_MAX_REQUEST_TIMEOUT_SECONDS")

    def _send(self, path: str, send: Callable[[str], requests.Response]) -> requests.Response:
        """Send a request for `path` with `send`, re-raising failures without the request."""
        _require_service_path(path)

        try:
            return send(path)
        except requests.RequestException as error:
            message = str(error)

        # Raised outside the except block, so the original error is not chained to this one.
        raise requests.RequestException(message)

    def _get_json(
        self,
        path: str,
        headers: Mapping[str, str | bytes | None] | None = None,
    ) -> JsonOnlyResponse:
        return JsonOnlyResponse(
            self._send(path, functools.partial(self._http_client.get, headers=headers))
        )

    def _post_json(
        self,
        path: str,
        json: dict[str, Any],
        headers: Mapping[str, str | bytes | None] | None = None,
    ) -> JsonOnlyResponse:
        return JsonOnlyResponse(
            self._send(path, functools.partial(self._http_client.post, json=json, headers=headers))
        )


class OntologiesHttp(ServiceClient):
    """
    An HTTP client for the ontologies service.
    """

    __exports__ = ("get_json",)

    def __init__(self) -> None:
        super().__init__(
            base_url=os.getenv("ONTOLOGIES_ENDPOINT", "https://ontologies.canvasmedical.com")
        )

    def get_json(
        self,
        url: str,
        headers: Mapping[str, str | bytes | None] | None = None,
    ) -> JsonOnlyResponse:
        """Send a GET request for a path on the ontologies service."""
        return self._get_json(url, headers)


class PharmacyHttp(ServiceClient):
    """
    An HTTP client for the pharmacy service.
    """

    __exports__ = ("search_pharmacies", "get_pharmacy_by_ncpdp_id")

    def __init__(self) -> None:
        super().__init__(
            base_url=os.getenv(
                "PHARMACY_SERVICE_ENDPOINT", "https://pharmacy-2017071.canvasmedical.com"
            )
        )

        self._http_client._session.mount("https://", _SurescriptsTrustAdapter())

    def search_pharmacies(
        self,
        search_term: str | None = " ",
        latitude: str | None = None,
        longitude: str | None = None,
        id: int | None = None,
        ncpdp_id: str | None = None,
        organization_name: str | None = None,
        specialty_type: str | None = None,
        state: str | None = None,
        zip_code_prefix: str | None = None,
    ) -> list[dict]:
        """Search for pharmacies by term and optional location.

        Args:
            search_term: Full-text search across multiple fields.
            latitude: Latitude for location-based ordering.
            longitude: Longitude for location-based ordering.
            id: Exact pharmacy ID match.
            ncpdp_id: Exact NCPDP ID match.
            organization_name: Case-insensitive contains match on organization name.
            specialty_type: Case-insensitive contains match on specialty type.
            state: Case-insensitive exact match on state.
            zip_code_prefix: One or more comma/space-separated zip code prefixes.
        """
        params: dict[str, str | int] = {}

        if search_term and search_term.strip():
            params["search"] = search_term

        if latitude and longitude:
            params["latitude"] = latitude
            params["longitude"] = longitude

        if id is not None:
            params["id"] = id
        if ncpdp_id is not None:
            params["ncpdp_id"] = ncpdp_id
        if organization_name is not None:
            params["organization_name__icontains"] = organization_name
        if specialty_type is not None:
            params["specialty_type__icontains"] = specialty_type
        if state is not None:
            params["state__iexact"] = state
        if zip_code_prefix is not None:
            params["zip_code_prefix_in"] = zip_code_prefix

        query_string = urllib.parse.urlencode(params)
        url = f"/surescripts/pharmacy/?{query_string}" if query_string else "/surescripts/pharmacy/"
        response = self._get_json(url)
        response_json = response.json()
        return response_json.get("results", []) if response_json else []

    def get_pharmacy_by_ncpdp_id(self, ncpdp_id: str) -> dict[str, Any] | None:
        """Lookup a pharmacy by its NCPDP ID.

        An NCPDP ID is all digits; any other value matches no pharmacy and sends nothing.
        """
        identifier = str(ncpdp_id)

        if not (identifier.isascii() and identifier.isdigit()):
            return None

        response = self._get_json(f"/surescripts/pharmacy/ncpdp_id/{identifier}/")
        return response.json()


class ScienceHttp(ServiceClient):
    """
    An HTTP client for the science service.
    """

    __exports__ = ("get_json",)

    def __init__(self) -> None:
        super().__init__(
            base_url=os.getenv("SCIENCE_ENDPOINT", "https://science.canvasmedical.com")
        )

    def get_json(
        self,
        url: str,
        headers: Mapping[str, str | bytes | None] | None = None,
    ) -> JsonOnlyResponse:
        """Send a GET request for a path on the science service."""
        return self._get_json(url, headers)


ontologies_http = OntologiesHttp()
science_http = ScienceHttp()
pharmacy_http = PharmacyHttp()

__all__ = __exports__ = (
    "ThreadPoolExecutor",
    "Http",
    "ontologies_http",
    "pharmacy_http",
    "science_http",
    "batch_get",
    "batch_post",
    "batch_put",
    "batch_patch",
)
