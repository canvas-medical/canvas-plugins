import inspect
import json
import re
from abc import ABC
from base64 import b64decode
from collections.abc import Callable
from functools import cached_property
from http import HTTPStatus
from typing import Any, ClassVar, Protocol, TypeVar, cast
from urllib.parse import parse_qsl

import sentry_sdk

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.simple_api import JSON, JSONResponse, Response
from canvas_sdk.events import Event, EventType
from canvas_sdk.handlers.base import BaseHandler
from logger import log
from plugin_runner.exceptions import PluginError

from .exceptions import AuthenticationError, InvalidCredentialsError
from .security import Credentials
from .tools import CaseInsensitiveMultiDict, MultiDict, separate_headers


class FormPart(Protocol):
    """
    Protocol for representing a form part in the body of a multipart/form-data request.

    A form part can represent a simple string value, or a file with a content type.
    """

    @staticmethod
    def is_file() -> bool:
        """Return True or False depending on whether the form part represents a file."""
        ...


class StringFormPart(FormPart):
    """Class for representing a form part that is a simple string value."""

    def __init__(self, name: str, value: str) -> None:
        self.name = name
        self.value = value

    @staticmethod
    def is_file() -> bool:
        """Return True or False depending on whether the form part represents a file."""
        return False

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FileFormPart):
            return False

        if not isinstance(other, StringFormPart):
            return NotImplemented

        return self.name == other.name and self.value == other.value


class FileFormPart(FormPart):
    """Class for representing a form part that is a file."""

    def __init__(
        self, name: str, filename: str, content: bytes, content_type: str | None = None
    ) -> None:
        self.name = name
        self.filename = filename
        self.content = content
        self.content_type = content_type

    @staticmethod
    def is_file() -> bool:
        """Return True or False depending on whether the form part represents a file."""
        return True

    def __eq__(self, other: object) -> bool:
        if isinstance(other, StringFormPart):
            return False

        if not isinstance(other, FileFormPart):
            return NotImplemented

        return all(
            (
                self.name == other.name,
                self.filename == other.filename,
                self.content == other.content,
                self.content_type == other.content_type,
            )
        )


class UploadedFilePart(FormPart):
    """Form part for a file that home-app uploaded to S3 before invoking the plugin.

    The bytes are not available — they live in S3 only. Use ``key`` to reference the
    file in subsequent effects. Consumer code (FHIR, message viewer, etc.) generates a
    fresh presigned URL on read.

    Returned by ``Request.form_data()`` for file fields when the matched route was
    declared with ``upload_files=True`` on its decorator.
    """

    def __init__(
        self,
        name: str,
        filename: str,
        content_type: str | None,
        size: int,
        key: str,
    ) -> None:
        self.name = name
        self.filename = filename
        self.content_type = content_type
        self.size = size
        self.key = key

    @staticmethod
    def is_file() -> bool:
        """Return True or False depending on whether the form part represents a file."""
        return True

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UploadedFilePart):
            return NotImplemented
        return (
            self.name == other.name
            and self.filename == other.filename
            and self.content_type == other.content_type
            and self.size == other.size
            and self.key == other.key
        )


def parse_multipart_form(form: bytes, boundary: str) -> MultiDict[str, FormPart]:
    """Parse a multipart form and return a dict of string to list of form parts."""
    form_data: list[tuple[str, FormPart]] = []

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
                # Files will have a content type, so grab it
                content_type = header.split(":")[1].strip()

        if not name or not value:
            raise RuntimeError("Invalid multipart/form-data request body")

        # Strip off the trailing newline characters from the value
        value = value[:-2]

        # Now we have all the data, so append it to the list of form data
        if filename:
            # Because a filename was provided, we know it's a file and not a simple string value
            form_data.append(
                (
                    name,
                    FileFormPart(
                        name=name, filename=filename, content=value, content_type=content_type
                    ),
                )
            )
        else:
            # Decode the string before adding it
            form_data.append((name, StringFormPart(name, value.decode())))

    return MultiDict(form_data)


class Request:
    """Request class for incoming requests to the API."""

    def __init__(
        self,
        event: Event,
        path_pattern: re.Pattern,
        upload_files: bool = False,
    ) -> None:
        self.method = event.context["method"]
        self.path = event.context["path"]
        self.query_string = event.context["query_string"]
        self._body = event.context["body"]
        self.headers = CaseInsensitiveMultiDict(separate_headers(event.context["headers"]))
        self._upload_files = upload_files

        match = path_pattern.fullmatch(event.context["path"])
        self.path_params = match.groupdict() if match else {}

        self.query_params = MultiDict(parse_qsl(self.query_string))

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

    @cached_property
    def body(self) -> bytes:
        """Decode and return the response body."""
        return b64decode(self._body)

    def json(self) -> JSON:
        """Return the response body as a JSON dict."""
        return json.loads(self.body)

    def text(self) -> str:
        """Return the response body as plain text."""
        return self.body.decode()

    def form_data(self) -> MultiDict[str, FormPart]:
        """Return the response body as a dict of string to list of FormPart objects.

        When the matched route was declared with ``upload_files=True`` on its decorator,
        home-app has already uploaded any file fields to S3 and replaced the body with a
        JSON envelope. In that case file fields are returned as :class:`UploadedFilePart`
        (with ``key`` instead of ``content``); non-file fields stay as
        :class:`StringFormPart`.

        Otherwise the body is parsed as ``application/x-www-form-urlencoded`` or
        ``multipart/form-data`` and file fields are returned as :class:`FileFormPart`.
        """
        form_data: MultiDict[str, FormPart]

        if self._upload_files:
            # Home-app intercepted the multipart, uploaded files to S3, and rewrote the body
            # as a JSON envelope.
            envelope = json.loads(self.body)
            entries: list[tuple[str, FormPart]] = []
            for field in envelope.get("form_fields", []):
                entries.append((field["name"], StringFormPart(field["name"], field["value"])))
            for upload in envelope.get("uploaded_files", []):
                entries.append(
                    (
                        upload["name"],
                        UploadedFilePart(
                            name=upload["name"],
                            filename=upload["filename"],
                            content_type=upload.get("content_type"),
                            size=upload["size"],
                            key=upload["key"],
                        ),
                    )
                )
            form_data = MultiDict(entries)
        elif self.content_type == "application/x-www-form-urlencoded":
            # For request bodies that are URL-encoded, just parse them and return them as simple
            # form parts
            form_data = MultiDict(
                (name, StringFormPart(name, value)) for name, value in parse_qsl(self.body.decode())
            )
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


def post(path: str, *, upload_files: bool = False) -> Callable[[RouteHandler], RouteHandler]:
    """Decorator for adding API POST routes.

    When ``upload_files=True``, home-app intercepts ``multipart/form-data`` requests:
    file parts are uploaded to S3 before the plugin runs, and the plugin receives an
    :class:`UploadedFilePart` (with ``key`` instead of ``content``) for each file
    field via ``request.form_data()``. Default is ``False`` — file bytes flow through
    to the plugin as today.
    """
    return _handler_decorator("POST", path, upload_files=upload_files)


def put(path: str, *, upload_files: bool = False) -> Callable[[RouteHandler], RouteHandler]:
    """Decorator for adding API PUT routes. See :func:`post` for ``upload_files`` semantics."""
    return _handler_decorator("PUT", path, upload_files=upload_files)


def delete(path: str, *, upload_files: bool = False) -> Callable[[RouteHandler], RouteHandler]:
    """Decorator for adding API DELETE routes."""
    return _handler_decorator("DELETE", path, upload_files=upload_files)


def patch(path: str, *, upload_files: bool = False) -> Callable[[RouteHandler], RouteHandler]:
    """Decorator for adding API PATCH routes. See :func:`post` for ``upload_files`` semantics."""
    return _handler_decorator("PATCH", path, upload_files=upload_files)


def _handler_decorator(
    method: str, path: str, *, upload_files: bool = False
) -> Callable[[RouteHandler], RouteHandler]:
    if not path.startswith("/"):
        raise PluginError(f"Route path '{path}' must start with a forward slash")

    def decorator(handler: RouteHandler) -> RouteHandler:
        """Mark the handler with the HTTP method, path, and upload-mode flag."""
        handler.route = (method, path)  # type: ignore[attr-defined]
        handler.upload_files = upload_files  # type: ignore[attr-defined]

        return handler

    return decorator


class SimpleAPIBase(BaseHandler, ABC):
    """Abstract base class for HTTP APIs."""

    RESPONDS_TO = [
        EventType.Name(EventType.SIMPLE_API_AUTHENTICATE),
        EventType.Name(EventType.SIMPLE_API_REQUEST),
    ]

    _ROUTES: ClassVar[dict[str, list[tuple[re.Pattern, RouteHandler]]]]
    _PATH_PARAM_REGEX = re.compile("<([a-zA-Z_][a-zA-Z0-9_]*)>")

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        # Build the registry of routes so that requests can be routed to the correct handler. This
        # is done by iterating over the methods on the class and looking for methods that have been
        # marked by the handler decorators (get, post, etc.).
        cls._ROUTES = {}
        for attr in cls.__dict__.values():
            if callable(attr) and (route := getattr(attr, "route", None)):
                method, relative_path = route
                path = f"{cls._path_prefix()}{relative_path}"

                # Convert the path to a regular expression pattern so that any path parameters can
                # be extracted later
                try:
                    path_pattern = re.compile(path.replace("<", "(?P<").replace(">", ">[^/]+)"))
                except re.error as error:
                    raise PluginError(
                        f"Path parameter names in route '{path}' must be unique"
                    ) from error

                cls._ROUTES.setdefault(method, [])
                cls._ROUTES[method].append((path_pattern, attr))

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        # Determine the first handler that matches the path based on the path pattern
        self._path_pattern = None
        self._handler = None
        for path_pattern, handler in self._ROUTES.get(self.event.context["method"], ()):
            if path_pattern.fullmatch(self.event.context["path"]):
                self._path_pattern = path_pattern
                self._handler = handler
                break

    @classmethod
    def _path_prefix(cls) -> str:
        return ""

    @cached_property
    def request(self) -> Request:
        """Return the request object from the event."""
        upload_files = bool(getattr(self._handler, "upload_files", False))
        return Request(
            self.event,
            cast(re.Pattern, self._path_pattern),
            upload_files=upload_files,
        )

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
            log.exception(f"Error handling '{EventType.Name(self.event.type)}' event")

            sentry_sdk.capture_exception(exception)

            return [Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR).apply()]

    def _authenticate(self) -> list[Effect]:
        """Authenticate the request."""
        try:
            # Create the credentials object
            credentials_cls = inspect.get_annotations(self.authenticate, eval_str=True).get(
                "credentials"
            )

            if not credentials_cls or not issubclass(credentials_cls, Credentials):
                raise PluginError(
                    f"Cannot determine authentication scheme for {self.request.path}; "
                    "please specify the type of credentials your endpoint requires"
                )
            credentials = credentials_cls(self.request)

            # Pass the credentials object into the developer-defined authenticate method. If
            # authentication succeeds, return a 200 back to home-app, otherwise return a response
            # with the error.
            #
            # The auth-success effect carries the matched route's ``upload_files`` flag in its
            # JSON payload (alongside the standard headers/body/status_code). home-app reads it
            # to decide whether to intercept multipart uploads before sending the request event.
            if self.authenticate(credentials):
                upload_files = bool(getattr(self._handler, "upload_files", False))
                payload = {
                    "headers": {},
                    "body": "",
                    "status_code": int(HTTPStatus.OK),
                    "upload_files": upload_files,
                }
                return [Effect(type=EffectType.SIMPLE_API_RESPONSE, payload=json.dumps(payload))]
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
        # Handle the request
        effects = cast(RouteHandler, self._handler)(self)

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

            if cast(Effect, effects[index]).type == EffectType.SIMPLE_API_RESPONSE:
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
                    return [cast(Effect, effects[index])]

        return cast(list[Effect], effects)

    def accept_event(self) -> bool:
        """Ignore the event if the handler does not implement the route."""
        return self._handler is not None

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

    @classmethod
    def _path_prefix(cls) -> str:
        # getattr needs a default else it will raise an exception. We also need to ensure that the
        # final value is a string if the user specifies "None" as the prefix because this value gets
        # prepended to the URL path
        return getattr(cls, "PREFIX", "") or ""


class SimpleAPIRoute(SimpleAPIBase, ABC):
    """Base class for HTTP API routes.

    Set ``UPLOAD_FILES = True`` as a class attribute to opt this route into multipart
    upload interception. See :func:`post` for the semantics.
    """

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Automatically mark the get, post, put, delete, and patch methods as handler methods."""
        if hasattr(cls, "PREFIX"):
            raise PluginError(
                f"Setting a PREFIX value on a {SimpleAPIRoute.__name__} is not allowed"
            )

        upload_files = bool(getattr(cls, "UPLOAD_FILES", False))

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

            # GET routes are body-less by HTTP semantics, so the @get decorator does not
            # accept upload_files. Skip the kwarg for GET; pass it through for the rest.
            # mypy can't narrow the union-typed `decorator` past the ``is get`` check, so
            # the call-arg ignore is required on the else branch.
            if decorator is get:
                decorator(path)(attr_value)
            else:
                decorator(path, upload_files=upload_files)(attr_value)  # type: ignore[call-arg]

        super().__init_subclass__(**kwargs)

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


__exports__ = (
    "FormPart",
    "StringFormPart",
    "FileFormPart",
    "UploadedFilePart",
    "parse_multipart_form",
    "Request",
    "SimpleAPIType",
    "RouteHandler",
    "get",
    "post",
    "put",
    "delete",
    "patch",
    "SimpleAPIBase",
    "SimpleAPI",
    "SimpleAPIRoute",
    # Not defined here but used in an existing plugin
    "Credentials",
)
