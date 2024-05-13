import time
from functools import wraps
from typing import Any, Callable, TypeVar

import requests
import statsd

F = TypeVar("F", bound=Callable)


class Http:
    """A helper class for completing HTTP calls with metrics tracking."""

    def __init__(self) -> None:
        self.session = requests.Session()
        self.statsd_client = statsd.StatsClient()

    @staticmethod
    def measure_time(fn: F | None = None) -> Callable[[F], F] | F:
        """A decorator to store timing of HTTP calls."""

        def _decorator(fn: F) -> F:
            @wraps(fn)
            def wrapper(self: "Http", *args: Any, **kwargs: Any) -> Any:
                start_time = time.time()
                result = fn(self, *args, **kwargs)
                end_time = time.time()
                timing = int((end_time - start_time) * 1000)
                self.statsd_client.timing(f"http_{fn.__name__}", timing)
                return result

            return wrapper

        return _decorator(fn) if fn else _decorator

    @measure_time
    def get(self, url: str, headers: dict = {}) -> requests.Response:
        """Sends a GET request."""
        return self.session.get(url, headers=headers)

    @measure_time
    def post(
        self,
        url: str,
        json: dict | None = None,
        data: dict | str | list | bytes | None = None,
        headers: dict = {},
    ) -> requests.Response:
        """Sends a POST request."""
        return self.session.post(url, json=json, data=data, headers=headers)

    @measure_time
    def put(
        self,
        url: str,
        json: dict | None = None,
        data: dict | str | list | bytes | None = None,
        headers: dict = {},
    ) -> requests.Response:
        """Sends a PUT request."""
        return self.session.put(url, json=json, data=data, headers=headers)

    @measure_time
    def patch(
        self,
        url: str,
        json: dict | None = None,
        data: dict | str | list | bytes | None = None,
        headers: dict = {},
    ) -> requests.Response:
        """Sends a PATCH request."""
        return self.session.patch(url, json=json, data=data, headers=headers)
