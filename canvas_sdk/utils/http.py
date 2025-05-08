import concurrent
import functools
import os
import urllib.parse
from collections.abc import Callable, Iterable, Mapping
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Literal, Protocol, TypeVar

import requests

from canvas_sdk.utils.metrics import measured

F = TypeVar("F", bound=Callable)


class _BatchableRequest:
    """Representation of a request that will be executed in parallel with other requests."""

    def __init__(
        self, method: Literal["GET", "POST", "PUT", "PATCH"], url: str, **kwargs: Any
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
    url: str, headers: Mapping[str, str | bytes | None] | None = None
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
    return _BatchableRequest("POST", url, json=json, data=data, headeres=headers)


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


class Http:
    """A helper class for completing HTTP calls with metrics tracking."""

    _MAX_REQUEST_TIMEOUT_SECONDS = 30

    _base_url: str
    _session: requests.Session

    def join_url(self, url: str) -> str:
        """
        Join a URL to the base_url.
        """
        joined = urllib.parse.urljoin(self._base_url, url)

        if not joined.startswith(self._base_url):
            raise ValueError("You may not access other URLs using this client.")

        return joined

    def __init__(self, base_url: str = "") -> None:
        self._base_url = base_url
        self._session = requests.Session()

    @measured(track_plugins_usage=True)
    def get(
        self, url: str, headers: Mapping[str, str | bytes | None] | None = None
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


class JsonOnlyHttp(Http):
    def get(
        self,
        url: str,
        headers: Mapping[str, str | bytes | None] | None = None,
    ) -> requests.Response:
        raise NotImplementedError

    def get_json(
        self,
        url: str,
        headers: Mapping[str, str | bytes | None] | None = None,
    ) -> JsonOnlyResponse:
        return JsonOnlyResponse(super().get(url, headers))

    def post(
        self,
        url: str,
        json: dict | None = None,
        data: dict | str | list | bytes | None = None,
        headers: Mapping[str, str | bytes | None] | None = None,
    ) -> requests.Response:
        raise NotImplementedError

    def put(
        self,
        url: str,
        json: dict | None = None,
        data: dict | str | list | bytes | None = None,
        headers: Mapping[str, str | bytes | None] | None = None,
    ) -> requests.Response:
        raise NotImplementedError

    def patch(
        self,
        url: str,
        json: dict | None = None,
        data: dict | str | list | bytes | None = None,
        headers: Mapping[str, str | bytes | None] | None = None,
    ) -> requests.Response:
        raise NotImplementedError


class OntologiesHttp(JsonOnlyHttp):
    """
    An HTTP client for the ontologies service.
    """

    def __init__(self) -> None:
        super().__init__(base_url="https://ontologies.canvasmedical.com")

        self._session.headers.update({"Authorization": os.getenv("PRE_SHARED_KEY", "")})


class ScienceHttp(JsonOnlyHttp):
    """
    An HTTP client for the ontologies service.
    """

    def __init__(self) -> None:
        super().__init__(base_url="https://science.canvasmedical.com")

        self._session.headers.update({"Authorization": os.getenv("PRE_SHARED_KEY", "")})


ontologies_http = OntologiesHttp()
science_http = ScienceHttp()

__all__ = __exports__ = (
    "ThreadPoolExecutor",
    "Http",
    "ontologies_http",
    "science_http",
    "batch_get",
    "batch_post",
    "batch_put",
    "batch_patch",
)
