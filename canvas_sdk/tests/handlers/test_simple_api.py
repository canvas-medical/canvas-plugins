import json
from base64 import b64decode, b64encode
from collections.abc import Callable, Iterable, Mapping, Sequence
from http import HTTPStatus
from types import SimpleNamespace
from typing import Any
from urllib.parse import parse_qs
from uuid import uuid4

import pytest
from _pytest.fixtures import SubRequest

from canvas_sdk.effects.simple_api import (
    Effect,
    EffectType,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    Response,
)
from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.handlers.simple_api import api
from canvas_sdk.handlers.simple_api.api import Request, SimpleAPI, SimpleAPIBase, SimpleAPIRoute
from canvas_sdk.handlers.simple_api.security import (
    APIKeyAuthMixin,
    APIKeyCredentials,
    AuthSchemeMixin,
    BasicAuthMixin,
    BasicCredentials,
    BearerCredentials,
    Credentials,
)
from plugin_runner.exceptions import PluginError

REQUEST_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]
HEADERS = {"Canvas-Plugins-Test-Header": "test header"}


class NoAuthMixin:
    """Mixin to bypass authentication for tests that are not related to authentication."""

    def authenticate(self, credentials: Credentials) -> bool:
        """Authenticate the request."""
        return True


class RouteNoAuth(NoAuthMixin, SimpleAPIRoute):
    """Route class that bypasses authentication."""

    pass


class APINoAuth(NoAuthMixin, SimpleAPI):
    """API class that bypasses authentication."""

    pass


def make_event(
    event_type: EventType,
    method: str,
    path: str,
    query_string: str | None = None,
    body: bytes | None = None,
    headers: Mapping[str, str] | None = None,
) -> Event:
    """Make a SIMPLE_API_REQUEST event suitable for testing."""
    if event_type == EventType.SIMPLE_API_AUTHENTICATE:
        body = b""

    return Event(
        event_request=EventRequest(
            type=event_type,
            target=None,
            context=json.dumps(
                {
                    "method": method,
                    "path": path,
                    "query_string": query_string or "",
                    "body": b64encode(body or b"").decode(),
                    "headers": headers or {},
                },
                indent=None,
                separators=(",", ":"),
            ),
            target_type=None,
        )
    )


def handle_request(
    cls: type[SimpleAPIBase],
    method: str,
    path: str,
    query_string: str | None = None,
    body: bytes | None = None,
    headers: Mapping[str, str] | None = None,
) -> list[Effect]:
    """
    Mimic the two-pass request handling in home-app.

    First, handle the authentication event, and if it succeeds, handle the request event.
    """
    handler = cls(
        make_event(EventType.SIMPLE_API_AUTHENTICATE, method, path, query_string, body, headers)
    )
    effects = handler.compute()

    payload = json.loads(effects[0].payload)
    if payload["status_code"] != HTTPStatus.OK:
        return effects

    handler = cls(
        make_event(EventType.SIMPLE_API_REQUEST, method, path, query_string, body, headers)
    )

    return handler.compute()


@pytest.mark.parametrize(
    argnames="method,path,query_string,body,headers",
    argvalues=[
        ("GET", "/route", "value1=a&value2=b", b"", {}),
        (
            "POST",
            "/route",
            "value1=a&value2=b",
            b'{"message": "JSON request"}',
            {"Content-Type": "application/json"},
        ),
        (
            "POST",
            "/route",
            "value1=a&value2=b",
            b"plain text request",
            {"Content-Type": "text/plain"},
        ),
        ("POST", "/route", "value1=a&value2=b", b"<html></html>", {"Content-Type": "text/html"}),
    ],
    ids=["no body", "JSON", "plain text", "HTML"],
)
def test_request(
    method: str,
    path: str,
    query_string: str | None,
    body: bytes,
    headers: Mapping[str, str] | None,
) -> None:
    """Test the construction of a Request object and access to its attributes."""
    request = Request(
        make_event(EventType.SIMPLE_API_REQUEST, method, path, query_string, body, headers)
    )

    assert request.method == method
    assert request.path == path
    assert request.query_string == query_string
    assert request.body == body
    assert request.headers == headers

    assert request.query_params == parse_qs(query_string)
    assert request.content_type == headers.get("Content-Type")
    assert request.content_type == request.headers.get("CONTENT-TYPE")

    if request.content_type:
        if request.content_type == "application/json":
            assert request.json() == json.loads(body)
        elif request.content_type.startswith("text/"):
            assert request.text() == body.decode()


def response_body(effects: Iterable[Effect]) -> bytes:
    """Given a list of effects, find the response object and return the body."""
    for effect in effects:
        if effect.type == EffectType.SIMPLE_API_RESPONSE:
            payload = json.loads(effect.payload)
            return b64decode(payload["body"].encode())

    pytest.fail("No response effect was found in the list of effects")


def json_response_body(effects: Iterable[Effect]) -> Any:
    """Given a list of effects, find the response object and return the JSON body."""
    return json.loads(response_body(effects))


@pytest.mark.parametrize(argnames="method", argvalues=REQUEST_METHODS, ids=REQUEST_METHODS)
def test_request_routing_route(method: str) -> None:
    """Test request routing for SimpleAPIRoute plugins."""

    class Route(RouteNoAuth):
        PATH = "/route"

        def get(self) -> list[Response | Effect]:
            return [
                JSONResponse(
                    {"method": "GET"},
                )
            ]

        def post(self) -> list[Response | Effect]:
            return [
                JSONResponse(
                    {"method": "POST"},
                )
            ]

        def put(self) -> list[Response | Effect]:
            return [
                JSONResponse(
                    {"method": "PUT"},
                )
            ]

        def delete(self) -> list[Response | Effect]:
            return [
                JSONResponse(
                    {"method": "DELETE"},
                )
            ]

        def patch(self) -> list[Response | Effect]:
            return [
                JSONResponse(
                    {"method": "PATCH"},
                )
            ]

    effects = handle_request(Route, method, path="/route")
    body = json_response_body(effects)

    assert body["method"] == method


@pytest.mark.parametrize(
    argnames="path", argvalues=["/route1", "/route2"], ids=["route1", "route2"]
)
@pytest.mark.parametrize(
    argnames="prefix",
    argvalues=["/prefix", "", None],
    ids=["with prefix", "empty prefix", "no prefix"],
)
@pytest.mark.parametrize(
    argnames="decorator,method",
    argvalues=[
        (api.get, "GET"),
        (api.post, "POST"),
        (api.put, "PUT"),
        (api.delete, "DELETE"),
        (api.patch, "PATCH"),
    ],
    ids=REQUEST_METHODS,
)
def test_request_routing_api(
    decorator: Callable[[str], Callable], method: str, prefix: str | None, path: str
) -> None:
    """Test request routing for SimpleAPI plugins."""

    class API(APINoAuth):
        PREFIX = prefix

        @decorator("/route1")
        def route1(self) -> list[Response | Effect]:
            return [
                JSONResponse(
                    {"method": method},
                )
            ]

        @decorator("/route2")
        def route2(self) -> list[Response | Effect]:
            return [
                JSONResponse(
                    {"method": method},
                )
            ]

    effects = handle_request(API, method, path=f"{prefix or ''}{path}")
    body = json_response_body(effects)

    assert body["method"] == method


def test_request_lifecycle() -> None:
    """Test the request-response lifecycle."""

    class Route(RouteNoAuth):
        PATH = "/route"

        def post(self) -> list[Response | Effect]:
            return [
                JSONResponse(
                    {
                        "method": self.request.method,
                        "path": self.request.path,
                        "query_string": self.request.query_string,
                        "body": self.request.json(),
                        "headers": dict(self.request.headers),
                    },
                )
            ]

    effects = handle_request(
        Route,
        method="POST",
        path="/route",
        query_string="value1=a&value2=b",
        body=b'{"message": "JSON request"}',
        headers=HEADERS,
    )
    body = json_response_body(effects)

    assert body == {
        "body": {"message": "JSON request"},
        "headers": HEADERS,
        "method": "POST",
        "path": "/route",
        "query_string": "value1=a&value2=b",
    }


@pytest.mark.parametrize(
    argnames="response,expected_effects",
    argvalues=[
        (
            lambda: [
                Effect(type=EffectType.CREATE_TASK, payload="create task"),
                Effect(type=EffectType.ADD_BANNER_ALERT, payload="add banner alert"),
            ],
            [
                Effect(type=EffectType.CREATE_TASK, payload="create task"),
                Effect(type=EffectType.ADD_BANNER_ALERT, payload="add banner alert"),
            ],
        ),
        (
            lambda: [
                JSONResponse(
                    content={"message": "JSON response"},
                    status_code=HTTPStatus.ACCEPTED,
                    headers=HEADERS,
                ),
                Effect(type=EffectType.CREATE_TASK, payload="create task"),
            ],
            [
                JSONResponse(
                    content={"message": "JSON response"},
                    status_code=HTTPStatus.ACCEPTED,
                    headers=HEADERS,
                ).apply(),
                Effect(type=EffectType.CREATE_TASK, payload="create task"),
            ],
        ),
        (
            lambda: [
                JSONResponse(
                    content={"message": "JSON response"},
                    status_code=HTTPStatus.ACCEPTED,
                    headers=HEADERS,
                ).apply(),
                Effect(type=EffectType.CREATE_TASK, payload="create task"),
            ],
            [
                JSONResponse(
                    content={"message": "JSON response"},
                    status_code=HTTPStatus.ACCEPTED,
                    headers=HEADERS,
                ).apply(),
                Effect(type=EffectType.CREATE_TASK, payload="create task"),
            ],
        ),
        (lambda: [], []),
        (
            lambda: [Response(), Response()],
            [Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR).apply()],
        ),
        (
            lambda: [
                JSONResponse(
                    content={"message": "JSON response"},
                    status_code=HTTPStatus.BAD_REQUEST,
                    headers=HEADERS,
                ),
                Effect(type=EffectType.CREATE_TASK, payload="create task"),
            ],
            [
                JSONResponse(
                    content={"message": "JSON response"},
                    status_code=HTTPStatus.BAD_REQUEST,
                    headers=HEADERS,
                ).apply()
            ],
        ),
        (
            lambda: [
                JSONResponse(
                    content={"message": "JSON response"},
                    status_code=HTTPStatus.BAD_REQUEST,
                    headers=HEADERS,
                ).apply(),
                Effect(type=EffectType.CREATE_TASK, payload="create task"),
            ],
            [
                JSONResponse(
                    content={"message": "JSON response"},
                    status_code=HTTPStatus.BAD_REQUEST,
                    headers=HEADERS,
                ).apply()
            ],
        ),
        (
            lambda: [
                JSONResponse(content={"message": 1 / 0}, status_code=HTTPStatus.OK, headers=HEADERS)
            ],
            [Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR).apply()],
        ),
    ],
    ids=[
        "list of effects",
        "list of effects with response object",
        "list of effects with response effect",
        "no response",
        "multiple responses",
        "handler returns error response object",
        "handler returns error response effect",
        "exception in handler",
    ],
)
def test_response(response: Callable, expected_effects: Sequence[Effect]) -> None:
    """Test the construction and return of different kinds of responses."""

    class Route(RouteNoAuth):
        PATH = "/route"

        def get(self) -> list[Response | Effect]:
            return response()

    effects = handle_request(Route, method="GET", path="/route")

    assert effects == expected_effects


@pytest.mark.parametrize(
    argnames="response,expected_payload",
    argvalues=[
        (
            Response(
                content=b"%PDF-1.4\n%\xd3\xeb\xe9\xe1",
                status_code=HTTPStatus.ACCEPTED,
                headers=HEADERS,
                content_type="application/pdf",
            ),
            '{"headers": {"Canvas-Plugins-Test-Header": "test header", "Content-Type": '
            '"application/pdf"}, "body": "JVBERi0xLjQKJdPr6eE=", "status_code": 202}',
        ),
        (
            JSONResponse(
                content={"message": "JSON response"},
                status_code=HTTPStatus.ACCEPTED,
                headers=HEADERS,
            ),
            '{"headers": {"Canvas-Plugins-Test-Header": "test header", "Content-Type": '
            '"application/json"}, "body": "eyJtZXNzYWdlIjogIkpTT04gcmVzcG9uc2UifQ==", '
            '"status_code": 202}',
        ),
        (
            PlainTextResponse(
                content="plain text response", status_code=HTTPStatus.ACCEPTED, headers=HEADERS
            ),
            '{"headers": {"Canvas-Plugins-Test-Header": "test header", "Content-Type": '
            '"text/plain"}, "body": "cGxhaW4gdGV4dCByZXNwb25zZQ==", "status_code": 202}',
        ),
        (
            HTMLResponse(content="<html></html>", status_code=HTTPStatus.ACCEPTED, headers=HEADERS),
            '{"headers": {"Canvas-Plugins-Test-Header": "test header", "Content-Type": '
            '"text/html"}, "body": "PGh0bWw+PC9odG1sPg==", "status_code": 202}',
        ),
        (
            Response(status_code=HTTPStatus.NO_CONTENT, headers=HEADERS),
            '{"headers": {"Canvas-Plugins-Test-Header": "test header"}, "body": "", '
            '"status_code": 204}',
        ),
    ],
    ids=["binary", "JSON", "plain text", "HTML", "no content"],
)
def test_response_type(response: Response, expected_payload: str) -> None:
    """Test the Response object with different types of content."""
    assert response.apply() == Effect(type=EffectType.SIMPLE_API_RESPONSE, payload=expected_payload)


def test_override_base_handler_attributes_error() -> None:
    """Test the enforcement of the error that occurs when base handler attributes are overridden."""
    with pytest.raises(PluginError):

        class API(APINoAuth):
            @api.get("/route")
            def compute(self) -> list[Response | Effect]:  # type: ignore[override]
                return []


def test_multiple_handlers_for_route_error() -> None:
    """
    Test the enforcement of the error that occurs when a route is assigned to multiple handlers.
    """
    with pytest.raises(PluginError):

        class API(APINoAuth):
            @api.get("/route")
            def route1(self) -> list[Response | Effect]:
                return []

            @api.get("/route")
            def route2(self) -> list[Response | Effect]:
                return []


def test_invalid_prefix_error() -> None:
    """Test the enforcement of the error that occurs when an API has an invalid prefix."""
    with pytest.raises(PluginError):

        class API(APINoAuth):
            PREFIX = "prefix"

            @api.get("/route")
            def route(self) -> list[Response | Effect]:
                return []


def test_invalid_path_error() -> None:
    """Test the enforcement of the error that occurs when a route has an invalid path."""
    with pytest.raises(PluginError):

        class Route(RouteNoAuth):
            PATH = "route"

            def get(self) -> list[Response | Effect]:
                return []

    with pytest.raises(PluginError):

        class API(APINoAuth):
            @api.get("route")
            def route(self) -> list[Response | Effect]:
                return []


def test_route_missing_path_error() -> None:
    """
    Test the enforcement of the error that occurs when a SimpleAPIRoute is missing a PATH value.
    """
    with pytest.raises(PluginError):

        class Route(RouteNoAuth):
            def get(self) -> list[Response | Effect]:
                return []


def test_route_has_prefix_error() -> None:
    """Test the enforcement of the error that occurs when a SimpleAPIRoute has a PREFIX value."""
    with pytest.raises(PluginError):

        class Route(RouteNoAuth):
            PREFIX = "/prefix"
            PATH = "/route"

            def get(self) -> list[Response | Effect]:
                return []


def test_route_that_uses_api_decorator_error() -> None:
    """
    Test the enforcement of the error that occurs when a SimpleAPIRoute uses the api decorator.
    """
    with pytest.raises(PluginError):

        class Route(RouteNoAuth):
            PREFIX = "/prefix"
            PATH = "/route"

            def get(self) -> list[Response | Effect]:
                return []

            @api.get("/route")
            def route(self) -> list[Response | Effect]:
                return []


def basic_headers(username: str, password: str) -> dict[str, str]:
    """Given a username and password, return headers that include a basic authentication header."""
    return {"Authorization": f"Basic {b64encode(f'{username}:{password}'.encode()).decode()}"}


def bearer_headers(token: str) -> dict[str, str]:
    """Given a token, return headers that include a bearer authentication header."""
    return {"Authorization": f"Bearer {token}"}


def api_key_headers(api_key: str) -> dict[str, str]:
    """Given an API key, return headers that include an API key authentication header."""
    return {"Authorization": api_key}


def custom_headers(api_key: str, app_key: str) -> dict[str, str]:
    """
    Given an API key and an app key, return headers that include custom authentication headers.
    """
    return {"API-Key": api_key, "App-Key": app_key}


USERNAME = uuid4().hex
PASSWORD = uuid4().hex
TOKEN = uuid4().hex
API_KEY = uuid4().hex
APP_KEY = uuid4().hex


@pytest.fixture(
    params=[
        (
            BasicCredentials,
            lambda _, credentials: credentials.username == USERNAME
            and credentials.password == PASSWORD,
            basic_headers(USERNAME, PASSWORD),
        ),
        (
            BearerCredentials,
            lambda _, credentials: credentials.token == TOKEN,
            bearer_headers(TOKEN),
        ),
        (
            APIKeyCredentials,
            lambda _, credentials: credentials.key == API_KEY,
            api_key_headers(API_KEY),
        ),
        (
            Credentials,
            lambda request, _: request.headers.get("API-Key") == API_KEY
            and request.headers.get("App-Key") == APP_KEY,
            custom_headers(API_KEY, APP_KEY),
        ),
    ],
    ids=["basic", "bearer", "API key", "custom"],
)
def authenticated_route(request: SubRequest) -> SimpleNamespace:
    """
    Parametrized test fixture that returns a Route class with authentication.

    It will also return a set of headers that will pass authentication for the route.
    """
    credentials_cls, authenticate_impl, headers = request.param

    class Route(SimpleAPIRoute):
        PATH = "/route"

        def authenticate(self, credentials: credentials_cls) -> bool:  # type: ignore[valid-type]
            return authenticate_impl(self.request, credentials)

        def get(self) -> list[Response | Effect]:
            return [Effect(type=EffectType.CREATE_TASK, payload="create task")]

    return SimpleNamespace(cls=Route, headers=headers)


def test_authentication(authenticated_route: SimpleNamespace) -> None:
    """Test that valid credentials result in a successful response."""
    effects = handle_request(
        authenticated_route.cls, method="GET", path="/route", headers=authenticated_route.headers
    )

    assert effects == [Effect(type=EffectType.CREATE_TASK, payload="create task")]


@pytest.mark.parametrize(
    argnames="headers",
    argvalues=[
        basic_headers(username=uuid4().hex, password=uuid4().hex),
        basic_headers(username="", password=uuid4().hex),
        basic_headers(username=uuid4().hex, password=""),
        bearer_headers(token=uuid4().hex),
        bearer_headers(token=""),
        api_key_headers(api_key=uuid4().hex),
        api_key_headers(api_key=""),
        custom_headers(api_key=uuid4().hex, app_key=uuid4().hex),
        custom_headers(api_key="", app_key=uuid4().hex),
        custom_headers(api_key=uuid4().hex, app_key=""),
        {},
    ],
    ids=[
        "basic",
        "basic missing username",
        "basic missing password",
        "bearer",
        "bearer missing token",
        "API key",
        "API key missing value",
        "custom",
        "custom missing API key",
        "custom missing app key",
        "no authentication headers",
    ],
)
def test_authentication_failure(
    authenticated_route: SimpleNamespace, headers: Mapping[str, str]
) -> None:
    """Test that invalid credentials result in a failure response."""
    effects = handle_request(authenticated_route.cls, method="GET", path="/route", headers=headers)

    assert json.loads(effects[0].payload)["status_code"] == HTTPStatus.UNAUTHORIZED


@pytest.mark.parametrize(
    argnames="credentials_cls,headers",
    argvalues=[
        (BasicCredentials, basic_headers(USERNAME, PASSWORD)),
        (BearerCredentials, bearer_headers(TOKEN)),
        (APIKeyCredentials, api_key_headers(API_KEY)),
        (Credentials, custom_headers(API_KEY, APP_KEY)),
    ],
    ids=["basic", "bearer", "API key", "custom"],
)
def test_authentication_exception(
    credentials_cls: type[Credentials], headers: Mapping[str, str]
) -> None:
    """Test that an exception occurring during authentication results in a failure response."""

    class Route(SimpleAPIRoute):
        PATH = "/route"

        def authenticate(self, credentials: credentials_cls) -> bool:  # type: ignore[valid-type]
            raise RuntimeError

        def get(self) -> list[Response | Effect]:
            return [Effect(type=EffectType.CREATE_TASK, payload="create task")]

    effects = handle_request(Route, method="GET", path="/route", headers=headers)

    assert effects == [Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR).apply()]


@pytest.mark.parametrize(
    argnames="mixin_cls,secrets,headers,expected_effects",
    argvalues=[
        (
            BasicAuthMixin,
            {"simpleapi-basic-username": USERNAME, "simpleapi-basic-password": PASSWORD},
            basic_headers(USERNAME, PASSWORD),
            [Effect(type=EffectType.CREATE_TASK, payload="create task")],
        ),
        (
            BasicAuthMixin,
            {"simpleapi-basic-username": USERNAME, "simpleapi-basic-password": PASSWORD},
            basic_headers(uuid4().hex, uuid4().hex),
            [
                JSONResponse(
                    content={"error": "Provided credentials are invalid"},
                    status_code=HTTPStatus.UNAUTHORIZED,
                ).apply()
            ],
        ),
        (
            BasicAuthMixin,
            {},
            basic_headers(USERNAME, PASSWORD),
            [
                JSONResponse(
                    content={"error": "Provided credentials are invalid"},
                    status_code=HTTPStatus.UNAUTHORIZED,
                ).apply()
            ],
        ),
        (
            APIKeyAuthMixin,
            {"simpleapi-api-key": API_KEY},
            api_key_headers(API_KEY),
            [Effect(type=EffectType.CREATE_TASK, payload="create task")],
        ),
        (
            APIKeyAuthMixin,
            {"simpleapi-api-key": API_KEY},
            api_key_headers(uuid4().hex),
            [
                JSONResponse(
                    content={"error": "Provided credentials are invalid"},
                    status_code=HTTPStatus.UNAUTHORIZED,
                ).apply()
            ],
        ),
        (
            APIKeyAuthMixin,
            {},
            api_key_headers(API_KEY),
            [
                JSONResponse(
                    content={"error": "Provided credentials are invalid"},
                    status_code=HTTPStatus.UNAUTHORIZED,
                ).apply()
            ],
        ),
    ],
    ids=[
        "basic valid",
        "basic invalid",
        "basic missing secret",
        "API key valid",
        "API key invalid",
        "API key missing secret",
    ],
)
def test_authentication_mixins(
    mixin_cls: type[AuthSchemeMixin],
    secrets: dict[str, str],
    headers: Mapping[str, str],
    expected_effects: Sequence[Effect],
) -> None:
    """
    Test that the provided authentication mixins behave correctly in success and failure scenarios.
    """

    class Route(mixin_cls, SimpleAPIRoute):  # type: ignore[misc,valid-type]
        PATH = "/route"

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)
            self.secrets = secrets

        def get(self) -> list[Response | Effect]:
            return [Effect(type=EffectType.CREATE_TASK, payload="create task")]

    effects = handle_request(Route, method="GET", path="/route", headers=headers)
    assert effects == expected_effects
