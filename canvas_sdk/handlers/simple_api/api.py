from collections.abc import Callable, Iterable
from inspect import ismethod
from typing import Any
from urllib.parse import parse_qs

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.simple_api import SimpleAPIResponse
from canvas_sdk.events import Event, EventType
from canvas_sdk.handlers.base import BaseHandler
from plugin_runner.exceptions import PluginError

# TODO: Auth requirements on the home-app side?
# TODO: Do we need to handle routing based on path regex (i.e. path parameters)?
# TODO: Do we need to handle repeated header names? Django concatenates; other platforms handle them as lists
# TODO: Do we need to handle non-JSON request and response bodies? Maybe not; we would have to Base64 encode complex data to send to gRPC anyway; a user could do the same in a JSON body (like in FHIR).
# TODO: 404 Not Found
# TODO: Error handling for duplicate routes; test install/reload


class SimpleAPIRequest:
    """Request class for incoming requests to the API."""

    def __init__(self, event: Event) -> None:
        self.headers = event.context["headers"]
        self.method = event.context["method"]
        self.path = event.context["path"]
        self.query_string = event.context["query_string"]
        self.body = event.context["body"]

        self.query_params = parse_qs(self.query_string)


RouteHandler = Callable[[SimpleAPIRequest], SimpleAPIResponse | list[SimpleAPIResponse | Effect]]


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


class SimpleAPI(BaseHandler):
    """Base class for HTTP APIs."""

    RESPONDS_TO = EventType.Name(EventType.SIMPLE_API_REQUEST)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        prefix = self.PREFIX if hasattr(self, "PREFIX") else ""

        # Build the registry of routes so that requests can be routed to the correct handler
        self._routes: dict[tuple[str, str], Callable] = {}
        for name in dir(self):
            attr = getattr(self, name)
            if ismethod(attr) and hasattr(attr, "route"):
                method, relative_path = attr.route
                route = (method, f"{prefix}{relative_path}")

                # We have to make sure that routes are only handled by one handler, but we can't do
                # that here given that other plugins may also implement routes. So the check for
                # duplicate routes has to happen elsewhere, external to the plugins that inherit
                # from this class.
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
                    f"{SimpleAPI.__name__} subclass route handler methods are overriding base class methods: {', '.join(f"{cls.__name__}.{name}" for name in names)}"
                )

    def compute(self) -> list[Effect]:
        """Route the incoming request to the handler based on the HTTP method and path."""
        request = SimpleAPIRequest(self.event)

        # Get the handler method
        handler = self._routes.get((request.method, request.path))
        if not handler:
            return []

        # Handle the request
        effects = handler(request)
        if not isinstance(effects, Iterable):
            effects = [effects]

        # Transform any API responses into effects if they aren't already effects
        response_count = 0
        for index, effect in enumerate(effects):
            if isinstance(effect, SimpleAPIResponse):
                effects[index] = effect.apply()
            if effects[index].type == EffectType.SIMPLE_API_RESPONSE:
                response_count += 1

        # TODO: What should the behavior be for non-response effects if this error condition occurs?
        # If there is more than one response, remove the responses and return an error response
        # instead. Allow non-response effects to pass through unaffected.
        if response_count > 1:
            effects = [
                effect for effect in effects if effect.type != EffectType.SIMPLE_API_RESPONSE
            ]
            effects.append(
                SimpleAPIResponse(
                    content={"error": "Multiple responses provided"}, status_code=500
                ).apply()
            )

        return effects
