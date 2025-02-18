import json
from abc import ABC, ABCMeta
from base64 import b64decode
from collections.abc import Callable
from functools import cached_property
from http import HTTPStatus
from inspect import ismethod
from typing import Any
from urllib.parse import parse_qs

from requests.structures import CaseInsensitiveDict

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.simple_api import Response
from canvas_sdk.events import Event, EventType
from canvas_sdk.handlers.base import BaseHandler
from logger import log
from plugin_runner.exceptions import PluginError

# TODO: Routing by path regex?
# TODO: Support multipart/form-data by adding helpers to the request class
# TODO: How to handle authz/authn?
#   * Risk of having a completely open endpoint — DOS?
#   * Auth is mandatory; must be a default mechanism
#   * Default auth strategy: disallow access and return 401
#   * Auth strategies: Set some constant
#     * custom: provide a callable
# - start with postman auth options
# - bring up security concerns about having an open endpoint
# - look into rejecting requests that do not match a plugin
# - auth is mandatory; default response is 401
# - require definition of auth methods on classes
# - basic, bearer, API key, and custom for first release; digest and JWT later
# - should be some difference between something specific and custom
# TODO: What should happen to other effects if the user returns two response objects from a route?
# - Look into wrapping everything in a transaction and rolling back on any error
# - Rollback should occur if error was detected in the handler or in home-app

# TODO: Discuss a durable way to get the plugin name
# - talk to Jose
# TODO: HTTPMethod enum or string?

# TODO: Discuss whether the response effects should inherit from the base effects
# - use this as a learning opportunity for how to create effects with (or without) pydantic
# TODO: Handle 404s: Make changes higher up the chain, or require handlers to return a response object
# - implement general event filtering on handlers to solve this problem
# - not general handling; only pre-built filtering
# - 404s will require detection in the main event loop

# TODO: Sanity check — test the handlers with an installed plugin
# TODO: Get the xfail test to pass

JSON = dict[str, "JSON"] | list["JSON"] | int | float | str | bool | None


class Request:
    """Request class for incoming requests to the API."""

    def __init__(self, event: Event) -> None:
        self.method = event.context["method"]
        self.path = event.context["path"]
        self.query_string = event.context["query_string"]
        self.body = b64decode(event.context["body"])
        self.headers: CaseInsensitiveDict = CaseInsensitiveDict(event.context["headers"])

        self.query_params = parse_qs(self.query_string)
        self.content_type = self.headers.get("Content-Type")

    def json(self) -> JSON:
        """Return the response JSON."""
        return json.loads(self.body)

    def text(self) -> str:
        """Return the response body as plain text."""
        return self.body.decode()


RouteHandler = Callable[[], Response | list[Response | Effect]]


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
                    f"class attributes: {', '.join(f'{cls.__name__}.{name}' for name in names)}"
                )

    def _plugin_name(self) -> str:
        return self.__class__.__module__.split(".", maxsplit=1)[0]

    def _path_prefix(self) -> str:
        return ""

    @cached_property
    def request(self) -> Request:
        """Return the request object from the event."""
        return Request(self.event)

    def compute(self) -> list[Effect]:
        """Route the incoming request to the handler based on the HTTP method and path."""
        # Get the handler method
        handler = self._routes.get((self.request.method, self.request.path))
        if not handler:
            return []

        # Handle the request
        effects = handler()

        # Transform any API responses into effects if they aren't already effects
        response_count = 0
        for index, effect in enumerate(effects):
            if isinstance(effect, Response):
                effects[index] = effect.apply()
            if effects[index].type == EffectType.SIMPLE_API_RESPONSE:
                response_count += 1

        # If there is more than one response, remove the responses and return an error response
        # instead. Allow non-response effects to pass through unaffected.
        if response_count > 1:
            log.error(f"Multiple responses provided by f{SimpleAPI.__name__} handler")

            effects = [
                effect for effect in effects if effect.type != EffectType.SIMPLE_API_RESPONSE
            ]
            effects.append(Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR).apply())

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
