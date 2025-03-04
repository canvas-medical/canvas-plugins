import json
import traceback
from abc import ABC
from base64 import b64decode
from collections.abc import Callable
from functools import cached_property
from http import HTTPStatus
from typing import Any, TypeVar
from urllib.parse import parse_qs

from requests.structures import CaseInsensitiveDict

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.events import Event, EventType
from canvas_sdk.handlers.base import BaseHandler
from logger import log
from plugin_runner.exceptions import PluginError

from .exceptions import AuthenticationError, InvalidCredentialsError
from .security import Credentials

# TODO: Routing by path regex?
# TODO: Log requests in a format similar to other API frameworks (probably need effect metadata)
# TODO: Support Effect metadata that is separate from payload
# TODO: Encode event payloads with MessagePack instead of JSON


JSON = dict[str, "JSON"] | list["JSON"] | int | float | str | bool | None


class FormPart:
    """
    Class for representing a form part in the body of a multipart/form-data request.

    A form part can represent a simple string value, or a file with a content type.
    """

    def __init__(
        self,
        name: str,
        value: str | bytes,
        filename: str | None = None,
        content_type: str | None = None,
    ) -> None:
        self.name = name
        self.value = value
        self.filename = filename
        self.content_type = content_type

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FormPart):
            return NotImplemented

        return all(
            (
                self.name == other.name,
                self.value == other.value,
                self.filename == other.filename,
                self.content_type == other.content_type,
            )
        )


def parse_multipart_form(form: bytes, boundary: str) -> dict[str, list[FormPart]]:
    """Parse a multipart form and return a dict of string to list of form parts."""
    form_data: dict[str, list[FormPart]] = {}

    # Split the body by the boundary value and iterate over the parts. The first and last
    # parts can be skipped because there are delimiters on at the start and end of the body
    parts = form.split(f"--{boundary}".encode())
    for part in parts[1:-1]:
        # Each part may be either a simple string value or a file. Simple string values
        # will just have a name and a value, whereas files will have a name, content type,
        # filename, and value.
        name = None
        content_type = None
        filename = None

        # Split the part into the headers and the value (i.e. the content)
        value: str | bytes
        headers, value = part.split(b"\r\n\r\n", maxsplit=1)

        # Iterate over the headers and extract the name, filename, and content type
        for header in headers.decode().split("\r\n"):
            # There are only two possible headers: Content-Disposition and Content-Type
            if header.lower().startswith("content-disposition: form-data;"):
                # Iterate over the content disposition parameters to get the form name and
                # filename
                for parameter in header.split(";")[1:]:
                    parameter_name, parameter_value = parameter.strip().split("=")

                    # Strip the quotes from the value
                    parameter_value = parameter_value[1:-1]

                    if parameter_name == "name":
                        name = parameter_value
                    elif parameter_name == "filename":
                        filename = parameter_value
            elif header.lower().startswith("content-type"):
                # Files will have a content type, so grab the content type value
                content_type = header.split(":")[1].strip()

        if not name or not value:
            raise RuntimeError("Invalid multipart/form-data request body")

        # Strip off the trailing newline characters from the value, and if the value is not a file,
        # decode it to a string
        value = value[:-2]
        if not filename:
            value = value.decode()

        # Now we have all the data, so append it to the list in the form data dict using the
        # part name as the key
        form_data.setdefault(name, [])
        form_data[name].append(FormPart(name, value, filename, content_type))

    return form_data


class Request:
    """Request class for incoming requests to the API."""

    def __init__(self, event: Event) -> None:
        self.method = event.context["method"]
        self.path = event.context["path"]
        self.query_string = event.context["query_string"]
        self._body = event.context["body"]
        self._body_is_decoded = False
        self.headers: CaseInsensitiveDict = CaseInsensitiveDict(event.context["headers"])

        self.query_params = parse_qs(self.query_string)

        # Parse the content type and any included content type parameters
        content_type = self.headers.get("Content-Type")
        self._content_type_parameters = {}
        if content_type:
            content_type, *parameters = content_type.split(";")
            self.content_type = content_type.strip()
            for parameter in parameters:
                name, value = parameter.strip().split("=")
                self._content_type_parameters[name] = value
        else:
            self.content_type = None

    @property
    def body(self) -> bytes:
        """Decode and return the raw response body as bytes."""
        if not self._body_is_decoded:
            self._body = b64decode(self._body)
            self._body_is_decoded = True

        return self._body

    def json(self) -> JSON:
        """Return the response body as a JSON dict."""
        return json.loads(self.body)

    def text(self) -> str:
        """Return the response body as plain text."""
        return self.body.decode()

    def form_data(self) -> dict[str, list[FormPart]]:
        """Return the response body as a dict of string to list of FormPart objects."""
        if self.content_type == "application/x-www-form-urlencoded":
            # For request bodies that are URL-encoded, just parse them and return them as simple
            # form parts
            form_data = {
                name: [FormPart(name=name, value=v) for v in value]
                for name, value in parse_qs(self.body.decode()).items()
            }
        elif self.content_type == "multipart/form-data":
            # Parse request bodies that are multipart forms
            form_data = parse_multipart_form(self.body, self._content_type_parameters["boundary"])
        else:
            raise RuntimeError(f"Cannot parse content type {self.content_type} as form data")

        return form_data


SimpleAPIType = TypeVar("SimpleAPIType", bound="SimpleAPIBase")

RouteHandler = Callable[[SimpleAPIType], list[Response | Effect]]


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
    if not path.startswith("/"):
        raise PluginError(f"Route path '{path}' must start with a forward slash")

    def decorator(handler: RouteHandler) -> RouteHandler:
        """Mark the handler with the HTTP method and path."""
        handler.route = (method, path)  # type: ignore[attr-defined]

        return handler

    return decorator


class SimpleAPIBase(BaseHandler, ABC):
    """Abstract base class for HTTP APIs."""

    RESPONDS_TO = [
        EventType.Name(EventType.SIMPLE_API_AUTHENTICATE),
        EventType.Name(EventType.SIMPLE_API_REQUEST),
    ]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        # Build the registry of routes so that requests can be routed to the correct handler. This
        # is done by iterating over the methods on the class instance and looking for methods that
        # have been marked by the handler decorators (get, post, etc.).
        self._routes: dict[tuple[str, str], Callable] = {}
        for attr in self.__class__.__dict__.values():
            if callable(attr) and (route := getattr(attr, "route", None)):
                method, relative_path = route
                path = f"{self._path_prefix()}{relative_path}"
                self._routes[(method, path)] = attr

    def _path_prefix(self) -> str:
        return ""

    @cached_property
    def request(self) -> Request:
        """Return the request object from the event."""
        return Request(self.event)

    def compute(self) -> list[Effect]:
        """Handle the authenticate or request event."""
        try:
            if self.event.type == EventType.SIMPLE_API_AUTHENTICATE:
                return self._authenticate()
            elif self.event.type == EventType.SIMPLE_API_REQUEST:
                return self._handle_request()
            else:
                raise AssertionError(f"Cannot handle event type {EventType.Name(self.event.type)}")
        except Exception as exception:
            for error_line_with_newlines in traceback.format_exception(exception):
                for error_line in error_line_with_newlines.split("\n"):
                    log.error(error_line)

            return [Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR).apply()]

    def _authenticate(self) -> list[Effect]:
        """Authenticate the request."""
        try:
            # Create the credentials object
            credentials_cls = self.authenticate.__annotations__.get("credentials")
            if not credentials_cls or not issubclass(credentials_cls, Credentials):
                raise PluginError(
                    "Cannot determine authentication scheme; please specify the type of "
                    "credentials your endpoint requires"
                )
            credentials = credentials_cls(self.request)

            # Pass the credentials object into the developer-defined authenticate method. If
            # authentication succeeds, return a 200 back to home-app, otherwise return a response
            # with the error
            if self.authenticate(credentials):
                return [Response(status_code=HTTPStatus.OK).apply()]
            else:
                raise InvalidCredentialsError
        except AuthenticationError as error:
            return [
                JSONResponse(
                    content={"error": str(error)}, status_code=HTTPStatus.UNAUTHORIZED
                ).apply()
            ]

    def _handle_request(self) -> list[Effect]:
        """Route the incoming request to the handler method based on the HTTP method and path."""
        # Get the handler method
        handler = self._routes[(self.request.method, self.request.path)]

        # Handle the request
        effects = handler(self)

        # Iterate over the returned effects and:
        # 1. Change any response objects to response effects
        # 2. Detect if the handler returned multiple responses, and if it did, log an error and
        #    return only a response effect with a 500 Internal Server Error.
        # 3. Detect if the handler returned an error response object, and if it did, return only
        #    the response effect.
        response_found = False
        for index, effect in enumerate(effects):
            # Change the response object to a response effect
            if isinstance(effect, Response):
                effects[index] = effect.apply()

            if effects[index].type == EffectType.SIMPLE_API_RESPONSE:
                # If a response has already been found, return an error response immediately
                if response_found:
                    log.error(f"Multiple responses provided by {SimpleAPI.__name__} handler")
                    return [Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR).apply()]
                else:
                    response_found = True

                # Get the status code of the response. If the initial response was an object and
                # not an effect, get it from the response object to avoid having to deserialize
                # the payload.
                if isinstance(effect, Response):
                    status_code = effect.status_code
                else:
                    status_code = json.loads(effect.payload)["status_code"]

                # If the handler returned an error response, return only that response effect
                # and omit any other included effects
                if 400 <= status_code <= 599:
                    return [effects[index]]

        return effects

    def accept_event(self) -> bool:
        """Ignore the event if the handler does not implement the route."""
        return (self.request.method, self.request.path) in self._routes

    def authenticate(self, credentials: Credentials) -> bool:
        """Method the user should override to authenticate requests."""
        return False


class SimpleAPI(SimpleAPIBase, ABC):
    """Base class for HTTP APIs."""

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """
        Detect errors the user makes when defining their handler.

        Prevent developers from defining multiple handlers for the same route, and from defining
        methods that clash with base class methods.
        """
        if (prefix := getattr(cls, "PREFIX", None)) and not prefix.startswith("/"):
            raise PluginError(f"Route prefix '{prefix}' must start with a forward slash")

        super().__init_subclass__(**kwargs)

        routes = set()
        route_handler_method_names = set()
        for name, value in cls.__dict__.items():
            if callable(value) and hasattr(value, "route"):
                if value.route in routes:
                    method, path = value.route
                    raise PluginError(
                        f"The route {method} {path} must only be handled by one route handler"
                    )
                routes.add(value.route)
                route_handler_method_names.add(name)

        for superclass in cls.__mro__[1:]:
            if names := route_handler_method_names.intersection(superclass.__dict__):
                raise PluginError(
                    f"{SimpleAPI.__name__} subclass route handler methods are overriding base "
                    f"class attributes: {', '.join(f'{cls.__name__}.{name}' for name in names)}"
                )

    def _path_prefix(self) -> str:
        return getattr(self, "PREFIX", None) or ""


class SimpleAPIRoute(SimpleAPIBase, ABC):
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

            if not callable(attr_value):
                continue

            if hasattr(attr_value, "route"):
                raise PluginError(
                    f"Using the api decorator on subclasses of {SimpleAPIRoute.__name__} is not "
                    "allowed"
                )

            if decorator is None:
                continue

            path = getattr(cls, "PATH", None)
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
