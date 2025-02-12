import json
from abc import ABC, ABCMeta, abstractmethod
from base64 import b64decode
from collections.abc import Callable, Iterable
from inspect import ismethod
from typing import Any
from urllib.parse import parse_qs

from requests.structures import CaseInsensitiveDict

from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import Response
from canvas_sdk.events import Event, EventType
from canvas_sdk.handlers.base import BaseHandler
from plugin_runner.exceptions import PluginError

# TODO: Routing by path regex?
# TODO: Do we need to handle repeated header names? Django concatenates; other platforms handle them as lists
# TODO: Discuss moving "apply" handling up the chain and the interface ramifications
# TODO: Are other helpers needed on request class?
# TODO: Support charset in responses and text helper on request? Or only support utf-8?
# TODO: Name for endpoint class: "Route" or "Endpoint"?
# TODO: What should happen to other effects if the user returns two response objects from a route?
# TODO: Interface — request as an argument to handlers or helper on the handler
# TODO: Discuss a durable way to get the plugin name
# TODO: Explicitly disallow multipart/form-data, or enable it?
# TODO: Aesthetics — plugin-like route should maybe have PATH and METHOD
# TODO: Discuss single response rather than list

# TODO: How to handle authz/authn?
#   * Risk of having a completely open endpoint — DOS?
#   * Auth is mandatory; must be a default mechanism
#   * Default auth strategy: disallow access and return 401
#   * Auth strategies: Set some constant
#     * custom: provide a callable
# TODO: Handle 404s: Make changes higher up the chain, or require handlers to return a response object
#       The challenge is that I can't distinguish between all handlers legitimately returning nothing no handlers taking the request
# TODO: Discuss whether the response effects should inherit from the base effects

# TODO: Sanity check — test the handlers with an installed plugin
# TODO: Consistent handling of empty string vs. None with query string and body
# TODO: Get the xfail test to pass

JSONValue = dict[str, "JSONValue"] | list["JSONValue"] | int | float | str | bool | None
JSON = dict[str, JSONValue] | list[JSONValue] | int | float | str | bool


class Request:
    """Request class for incoming requests to the API."""

    def __init__(self, event: Event) -> None:
        self.method = event.context["method"]
        self.path = event.context["path"]
        self.query_string = event.context["query_string"]
        self.body = b64decode(event.context["body"]) if event.context["body"] is not None else None
        self.headers: CaseInsensitiveDict = CaseInsensitiveDict(event.context["headers"])

        self.query_params = parse_qs(self.query_string)
        self.content_type = self.headers.get("Content-Type")

    def json(self) -> JSON:
        """Return the response JSON."""
        return json.loads(self.body)  # type: ignore[arg-type]

    def text(self) -> str:
        """Return the response body as plain text."""
        return self.body.decode("utf-8")  # type: ignore[union-attr]


RouteHandler = Callable[[Request], Response | list[Response | Effect]]


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
        """Mark the handler with the HTTP method and path."""
        handler.route = (method, path)  # type: ignore[attr-defined]

        return handler

    return decorator


class SimpleAPIBase(BaseHandler, ABC):
    """Abstract base class for HTTP APIs."""

    RESPONDS_TO = EventType.Name(EventType.SIMPLE_API_REQUEST)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        # Build the registry of routes so that requests can be routed to the correct handler
        self._routes: dict[tuple[str, str], Callable] = {}
        for name in dir(self):
            attr = getattr(self, name)
            if ismethod(attr) and hasattr(attr, "route"):
                method, relative_path = attr.route
                plugin_name = self._plugin_name()

                if plugin_name:
                    prefix = f"/{plugin_name}{self._path_prefix()}"
                else:
                    prefix = self._path_prefix()

                route = (method, f"{prefix}{relative_path}")
                self._routes[route] = attr

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Prevent developer-defined route methods from clashing with base class methods."""
        super().__init_subclass__(**kwargs)

        route_handler_method_names = {
            name
            for name, value in cls.__dict__.items()
            if callable(value) and hasattr(value, "route")
        }
        for superclass in cls.__mro__[1:]:
            if names := route_handler_method_names.intersection(superclass.__dict__):
                raise PluginError(
                    f"{SimpleAPI.__name__} subclass route handler methods are overriding base "
                    f"class attributes: {', '.join(f"{cls.__name__}.{name}" for name in names)}"
                )

    def _plugin_name(self) -> str:
        return self.__class__.__module__.split(".", maxsplit=1)[0]

    @abstractmethod
    def _path_prefix(self) -> str: ...

    def compute(self) -> list[Effect]:
        """Route the incoming request to the handler based on the HTTP method and path."""
        request = Request(self.event)

        # Get the handler method
        handler = self._routes.get((request.method, request.path))
        if not handler:
            return []

        # Handle the request
        effects = handler(request)
        if not isinstance(effects, Iterable):
            effects = [effects]

        # Transform any API responses into effects if they aren't already effects
        for index, effect in enumerate(effects):
            if isinstance(effect, Response):
                effects[index] = effect.apply()

        return effects


class SimpleAPI(SimpleAPIBase):
    """Base class for HTTP APIs."""

    def _path_prefix(self) -> str:
        return self.PREFIX if hasattr(self, "PREFIX") and self.PREFIX else ""


class SimpleAPIRouteMeta(ABCMeta):
    """Metaclass for the SimpleAPIRoute class."""

    def __new__(cls, name: str, bases: tuple, namespace: dict, **kwargs: Any) -> type:
        """Automatically marks the get, post, put, delete, and match methods as handler methods."""
        for attr_name, attr_value in namespace.items():
            if not callable(attr_value):
                continue

            if attr_name in {"get", "post", "put", "delete", "patch"} and "PATH" not in namespace:
                raise PluginError(f"PATH must be specified on a {SimpleAPIRoute.__name__}")

            match attr_name:
                case "get":
                    namespace[attr_name] = get(namespace["PATH"])(attr_value)
                case "post":
                    namespace[attr_name] = post(namespace["PATH"])(attr_value)
                case "put":
                    namespace[attr_name] = put(namespace["PATH"])(attr_value)
                case "delete":
                    namespace[attr_name] = delete(namespace["PATH"])(attr_value)
                case "patch":
                    namespace[attr_name] = patch(namespace["PATH"])(attr_value)

        return super().__new__(cls, name, bases, namespace, **kwargs)


class SimpleAPIRoute(SimpleAPIBase, metaclass=SimpleAPIRouteMeta):
    """Base class for HTTP API routes."""

    def __init_subclass__(cls, **kwargs: Any) -> None:
        if hasattr(cls, "PREFIX"):
            raise PluginError(
                f"Setting a PREFIX value on a {SimpleAPIRoute.__name__} is not allowed"
            )

        super().__init_subclass__(**kwargs)

    def _path_prefix(self) -> str:
        return ""
