from abc import ABCMeta
from collections.abc import Callable
from typing import Any

from canvas_sdk.effects import Effect
from canvas_sdk.events import Event, EventType
from canvas_sdk.handlers.base import BaseHandler


# TODO: Model this after existing request classes (FastAPI, Django)
# TODO: Provide parsed query string
# TODO: Test repeated headers
class Request:
    """Request class for incoming requests to the custom API."""

    def __init__(self, event: Event) -> None:
        self.headers = event.context["headers"]
        self.method = event.context["method"]
        self.path = event.context["path"]
        self.query_string = event.context["query-string"]


RouteMethod = Callable[[Request], list[Effect]]


class _RouteRegistry:
    def __init__(self) -> None:
        self._registry: dict[tuple[str, str], str] = {}

    def route_method_name(self, method: str, path: str) -> str | None:
        return self._registry.get((method, path))

    # TODO: Add other HTTP verbs
    def get(self, path: str) -> Callable[[RouteMethod], RouteMethod]:
        def decorator(method: RouteMethod) -> RouteMethod:
            if ("GET", path) in self._registry:
                raise RuntimeError(f"Custom API route GET {path} defined more than once")

            self._registry[("GET", path)] = method.__name__
            method.route = ("GET", path)  # type: ignore[attr-defined]

            return method

        return decorator


api = _RouteRegistry()


class CustomAPI(BaseHandler):
    """Base class for custom APIs."""

    RESPONDS_TO = EventType.Name(EventType.CUSTOM_API_REQUEST)

    def compute(self) -> list[Effect]:
        """Route the incoming request to the handler based on the HTTP method and path."""
        request = Request(self.event)

        route_method_name = api.route_method_name(request.method, request.path)
        if not route_method_name:
            return []

        try:
            handler = getattr(self, route_method_name)
            if handler.route != (request.method, request.path):
                return []
        except AttributeError:
            return []

        return handler(request)


class CustomAPIDjangoStyleMeta(ABCMeta):
    """Metaclass for the CustomAPIDjangoStyle class."""

    def __new__(cls, name: str, bases: tuple, namespace: dict, **kwargs: Any) -> type:
        """Automatically adds the get, post, etc. methods to the route registry."""
        for attr_name, attr_value in namespace.items():
            if not callable(attr_value):
                continue

            match attr_name:
                case "get":
                    namespace[attr_name] = api.get(namespace["ROUTE"])(attr_value)

        return super().__new__(cls, name, bases, namespace, **kwargs)


class CustomAPIDjangoStyle(CustomAPI, metaclass=CustomAPIDjangoStyleMeta):
    """Base class for custom APIs written in the style of the Django REST Framework."""

    pass
