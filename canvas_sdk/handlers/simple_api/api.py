import json
import traceback
from abc import ABC
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

from .security import Credentials

# TODO: Reject requests that do not match a plugin (on the home-app side)
# TODO: Raise exceptions in credential classes on error

# TODO: What should happen to other effects if the user returns two response objects from a route?
# - Look into wrapping everything in a transaction and rolling back on any error
# - Rollback should occur if error was detected in the handler or in home-app

# TODO: Discuss a durable way to get the plugin name
# - talk to Jose

# TODO: Look into making the response effects inherit from the base effects

# TODO: Sanity check — test plugin installation, updating, enabling, and disabling


# TODO: Security toolbox, auth mixins
# TODO: Routing by path regex?
# TODO: Support multipart/form-data by adding helpers to the request class


JSON = dict[str, "JSON"] | list["JSON"] | int | float | str | bool | None


class Request:
    """Request class for incoming requests to the API."""

    def __init__(self, event: Event) -> None:
        self.method = event.context["method"]
        self.path = event.context["path"]
        self.query_string = event.context["query_string"]
        self._body = event.context["body"]
        self.headers: CaseInsensitiveDict = CaseInsensitiveDict(event.context["headers"])

        self.query_params = parse_qs(self.query_string)
        self.content_type = self.headers.get("Content-Type")

    @cached_property
    def body(self) -> bytes:
        """Decode and return the response body."""
        return b64decode(self._body)

    def json(self) -> JSON:
        """Return the response JSON."""
        return json.loads(self.body)

    def text(self) -> str:
        """Return the response body as plain text."""
        return self.body.decode()


RouteHandler = Callable[["SimpleAPI"], Response | list[Response | Effect]]


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
            # Skip properties, because calling getattr on a property executes it. We don't want that
            # here, because we're only looking for methods that are marked as routes.
            if hasattr(self.__class__, name) and isinstance(
                getattr(self.__class__, name), property
            ):
                continue

            attr = getattr(self, name)
            route = getattr(attr, "route", None)
            if ismethod(attr) and route:
                method, relative_path = route
                plugin_name = self._plugin_name()

                if plugin_name:
                    prefix = f"/{plugin_name}{self._path_prefix()}"
                else:
                    prefix = self._path_prefix()

                route = (method, f"{prefix}{relative_path}")

                if route in self._routes:
                    raise PluginError(
                        f"The route {method} {relative_path} must only be handled by one route "
                        "handler"
                    )

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
        try:
            # Authenticate the request
            if not self._authenticate():
                return [Response(status_code=HTTPStatus.UNAUTHORIZED).apply()]

            # Get the handler method
            handler = self._routes[(self.request.method, self.request.path)]

            # Handle the request
            effects = handler()

            # Transform any API responses into effects if they aren't already effects
            response_count = 0
            for index, effect in enumerate(effects):
                if isinstance(effect, Response):
                    effects[index] = effect.apply()
                if effects[index].type == EffectType.SIMPLE_API_RESPONSE:
                    response_count += 1

            # Log an error if multiple responses are returned
            if response_count > 1:
                effects = [Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR).apply()]
                log.error(f"Multiple responses provided by f{SimpleAPI.__name__} handler")

            return effects
        except Exception as e:
            for error_line_with_newlines in traceback.format_exception(e):
                for error_line in error_line_with_newlines.split("\n"):
                    log.error(error_line)

            return [Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR).apply()]

    def ignore_event(self) -> bool:
        """Ignore the event if the handler does not implement the route."""
        return (self.request.method, self.request.path) not in self._routes

    def authenticate(self, credentials: Credentials) -> bool:
        """Authenticate the request."""
        return False

    def _authenticate(self) -> bool:
        # Create the credentials object and pass it into the developer-defined authenticate method
        credentials_cls = self.authenticate.__annotations__.get("credentials")
        if not credentials_cls or not issubclass(credentials_cls, Credentials):
            return False
        credentials = credentials_cls(self.request)

        return self.authenticate(credentials)


class SimpleAPI(SimpleAPIBase):
    """Base class for HTTP APIs."""

    def _path_prefix(self) -> str:
        return getattr(self, "PREFIX", None) or ""


class SimpleAPIRoute(SimpleAPIBase):
    """Base class for HTTP API routes."""

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Automatically mark the get, post, put, delete, and patch methods as handler methods."""
        if hasattr(cls, "PREFIX"):
            raise PluginError(
                f"Setting a PREFIX value on a {SimpleAPIRoute.__name__} is not allowed"
            )

        super().__init_subclass__(**kwargs)

        for attr_name, attr_value in cls.__dict__.items():
            decorator: Callable | None
            match attr_name:
                case "get":
                    decorator = get
                case "post":
                    decorator = post
                case "put":
                    decorator = put
                case "delete":
                    decorator = delete
                case "patch":
                    decorator = patch
                case _:
                    decorator = None

            if not callable(attr_value) or decorator is None:
                continue

            path = cls.__dict__.get("PATH")
            if not path:
                raise PluginError(f"PATH must be specified on a {SimpleAPIRoute.__name__}")

            decorator(path)(attr_value)

    def get(self) -> list[Response | Effect]:
        """Stub method for GET handler."""
        return []

    def post(self) -> list[Response | Effect]:
        """Stub method for POST handler."""
        return []

    def put(self) -> list[Response | Effect]:
        """Stub method for PUT handler."""
        return []

    def delete(self) -> list[Response | Effect]:
        """Stub method for DELETE handler."""
        return []

    def patch(self) -> list[Response | Effect]:
        """Stub method for PATCH handler."""
        return []
