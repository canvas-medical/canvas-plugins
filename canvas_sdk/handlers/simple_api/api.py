from collections.abc import Callable
from inspect import ismethod
from typing import Any
from urllib.parse import parse_qs

from canvas_sdk.effects import Effect
from canvas_sdk.events import Event, EventType
from canvas_sdk.handlers.base import BaseHandler


# TODO: Error handling (duplicate routes)
# TODO: Test error conditions on install/reload
# TODO: Request: repeated headers
# TODO: Request: body
# TODO: Response object
class Request:
    """Request class for incoming requests to the API."""

    def __init__(self, event: Event) -> None:
        self.headers = event.context["headers"]
        self.method = event.context["method"]
        self.path = event.context["path"]
        self.query_string = event.context["query-string"]
        self.query_params = parse_qs(self.query_string)


RouteHandler = Callable[[Request], list[Effect]]


def get(path: str) -> Callable[[RouteHandler], RouteHandler]:
    """Decorator for adding API GET routes."""
    return _handler_decorator("GET", path)


def post(path: str) -> Callable[[RouteHandler], RouteHandler]:
    """Decorator for adding API POST routes."""
    return _handler_decorator("POST", path)


def put(path: str) -> Callable[[RouteHandler], RouteHandler]:
    """Decorator for adding API PUT routes."""
    return _handler_decorator("PUT", path)


def delete(path: str) -> Callable[[RouteHandler], RouteHandler]:
    """Decorator for adding API DELETE routes."""
    return _handler_decorator("DELETE", path)


def patch(path: str) -> Callable[[RouteHandler], RouteHandler]:
    """Decorator for adding API PATCH routes."""
    return _handler_decorator("PATCH", path)


def _handler_decorator(method: str, path: str) -> Callable[[RouteHandler], RouteHandler]:
    def decorator(handler: RouteHandler) -> RouteHandler:
        handler.route = (method, path)  # type: ignore[attr-defined]

        return handler

    return decorator


class SimpleAPI(BaseHandler):
    """Base class for HTTP APIs."""

    RESPONDS_TO = EventType.Name(EventType.SIMPLE_API_REQUEST)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self._routes = {}

        prefix = self.PREFIX if hasattr(self, "PREFIX") else ""

        for name in dir(self):
            attr = getattr(self, name)
            if ismethod(attr) and hasattr(attr, "route"):
                method, path = attr.route
                self._routes[(method, f"{prefix}{path}")] = attr

    def compute(self) -> list[Effect]:
        """Route the incoming request to the handler based on the HTTP method and path."""
        request = Request(self.event)

        handler = self._routes.get((request.method, request.path))
        if not handler:
            return []

        return handler(request)
