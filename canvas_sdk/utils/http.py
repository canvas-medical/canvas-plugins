import concurrent
import functools
import time
from collections.abc import Callable, Iterable, Mapping
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from typing import Any, Literal, TypeVar, cast

import requests
import statsd

F = TypeVar("F", bound=Callable)


class BatchedRequest:
    """Representation of a request that will be executed in parallel with other requests."""

    def __init__(
        self, method: Literal["GET", "POST", "PUT", "PATCH"], url: str, *args: Any, **kwargs: Any
    ) -> None:
        self._method = method
        self._url = url
        self._args = args
        self._kwargs = kwargs

    def fn(self, session: requests.Session) -> Callable:
        """
        Return a callable constructed from the session object, method, URL, args, and kwargs.

        This callable is passed to the ThreadPoolExecutor.
        """
        match self._method:
            case "GET":
                instance_method = session.get
            case "POST":
                instance_method = session.post
            case "PUT":
                instance_method = session.put
            case "PATCH":
                instance_method = session.patch
            case _:
                raise RuntimeError(f"HTTP method {self._method} is not supported")

        return functools.partial(instance_method, self._url, *self._args, **self._kwargs)


class Http:
    """A helper class for completing HTTP calls with metrics tracking."""

    def __init__(self) -> None:
        self.session = requests.Session()
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
            self.statsd_client.timing(f"http_{fn.__name__}", timing)
            return result

        return cast(F, wrapper)

    @measure_time
    def get(
        self, url: str, headers: Mapping[str, str | bytes | None] | None = None
    ) -> requests.Response:
        """Sends a GET request."""
        if headers is None:
            headers = {}
        return self.session.get(url, headers=headers)

    @measure_time
    def post(
        self,
        url: str,
        json: dict | None = None,
        data: dict | str | list | bytes | None = None,
        headers: Mapping[str, str | bytes | None] | None = None,
    ) -> requests.Response:
        """Sends a POST request."""
        return self.session.post(url, json=json, data=data, headers=headers)

    @measure_time
    def put(
        self,
        url: str,
        json: dict | None = None,
        data: dict | str | list | bytes | None = None,
        headers: Mapping[str, str | bytes | None] | None = None,
    ) -> requests.Response:
        """Sends a PUT request."""
        return self.session.put(url, json=json, data=data, headers=headers)

    @measure_time
    def patch(
        self,
        url: str,
        json: dict | None = None,
        data: dict | str | list | bytes | None = None,
        headers: Mapping[str, str | bytes | None] | None = None,
    ) -> requests.Response:
        """Sends a PATCH request."""
        return self.session.patch(url, json=json, data=data, headers=headers)

    def batch_requests(
        self,
        batched_requests: Iterable[BatchedRequest],
        max_workers: int | None = None,
        timeout: int | None = None,
    ) -> list[requests.Response]:
        """
        Execute requests in parallel.

        Wait for the responses to complete, and then return a list of the responses.
        """
        futures = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for request in batched_requests:
                futures.append(executor.submit(request.fn(self.session)))

            # TODO: Is there a need to expose return_when or specify a different default value? https://docs.python.org/3.12/library/concurrent.futures.html#concurrent.futures.wait
            concurrent.futures.wait(futures, timeout=timeout)

        return [future.result() for future in futures]
