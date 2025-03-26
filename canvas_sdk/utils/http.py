import concurrent
import functools
import time
import urllib.parse
from collections.abc import Callable, Iterable, Mapping
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from typing import Any, Literal, Protocol, TypeVar, cast

import requests
import statsd

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

    base_url: str
    session: requests.Session

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Prevent base_url or session from being updated after initialization.
        """
        if name in ("base_url", "session"):
            raise AttributeError(f"{name} is read-only")

        super().__setattr__(name, value)

    def join_url(self, url: str) -> str:
        """
        Join a URL to the base_url.
        """
        joined = urllib.parse.urljoin(self.base_url, url)

        if not joined.startswith(self.base_url):
            raise ValueError("You may not access other URLs using this client.")

        return joined

    def __init__(self, base_url: str = "") -> None:
        super().__setattr__("base_url", base_url)
        super().__setattr__("session", requests.Session())

        self.statsd_client = statsd.StatsClient()

    @staticmethod
    def measure_time(fn: F) -> F:
        """A decorator to store timing of HTTP calls."""

        @wraps(fn)
        def wrapper(self: "Http", *args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            result = fn(self, *args, **kwargs)
            end_time = time.time()
            timing = int((end_time - start_time) * 1000)
            self.statsd_client.timing(f"plugins.http_{fn.__name__}", timing)
            return result

        return cast(F, wrapper)

    @measure_time
    def get(
        self, url: str, headers: Mapping[str, str | bytes | None] | None = None
    ) -> requests.Response:
        """Sends a GET request."""
        if headers is None:
            headers = {}
        return self.session.get(
            self.join_url(url),
            headers=headers,
            timeout=self._MAX_REQUEST_TIMEOUT_SECONDS,
        )

    @measure_time
    def post(
        self,
        url: str,
        json: dict | None = None,
        data: dict | str | list | bytes | None = None,
        headers: Mapping[str, str | bytes | None] | None = None,
    ) -> requests.Response:
        """Sends a POST request."""
        return self.session.post(
            self.join_url(url),
            json=json,
            data=data,
            headers=headers,
            timeout=self._MAX_REQUEST_TIMEOUT_SECONDS,
        )

    @measure_time
    def put(
        self,
        url: str,
        json: dict | None = None,
        data: dict | str | list | bytes | None = None,
        headers: Mapping[str, str | bytes | None] | None = None,
    ) -> requests.Response:
        """Sends a PUT request."""
        return self.session.put(
            self.join_url(url),
            json=json,
            data=data,
            headers=headers,
            timeout=self._MAX_REQUEST_TIMEOUT_SECONDS,
        )

    @measure_time
    def patch(
        self,
        url: str,
        json: dict | None = None,
        data: dict | str | list | bytes | None = None,
        headers: Mapping[str, str | bytes | None] | None = None,
    ) -> requests.Response:
        """Sends a PATCH request."""
        return self.session.patch(
            self.join_url(url),
            json=json,
            data=data,
            headers=headers,
            timeout=self._MAX_REQUEST_TIMEOUT_SECONDS,
        )

    @measure_time
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


class OntologiesHttp(Http):
    """
    An HTTP client for the ontologies service.
    """

    def __init__(self) -> None:
        super().__init__(base_url="https://ontologies.canvasmedical.com")

        # import here to avoid making it exportable to module importers
        import os

        self.session.headers.update({"Authorization": os.getenv("PRE_SHARED_KEY", "")})


class ScienceHttp(Http):
    """
    An HTTP client for the ontologies service.
    """

    def __init__(self) -> None:
        super().__init__(base_url="https://science.canvasmedical.com")

        # import here to avoid making it exportable to module importers
        import os

        self.session.headers.update({"Authorization": os.getenv("PRE_SHARED_KEY", "")})


__all__ = [
    "Http",
    "OntologiesHttp",
    "ScienceHttp",
    "batch_get",
    "batch_post",
    "batch_put",
    "batch_patch",
]
