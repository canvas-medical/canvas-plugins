import json
from base64 import b64decode, b64encode
from collections.abc import Callable, Iterable, Mapping, Sequence
from http import HTTPStatus
from typing import Any
from urllib.parse import parse_qs

import pytest

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
from canvas_sdk.handlers.simple_api.api import Request, SimpleAPI, SimpleAPIRoute
from plugin_runner.exceptions import PluginError

# TODO: test error: route not found
# TODO: test error: duplicate routes in same handler (depends on 404 handling)
# TODO: test error: no handler (depends on 404 handling)
# TODO: test error: multiple responses (depends on 404 handling)


REQUEST_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH"]
HEADERS = {"Canvas-Plugins-Test-Header": "test header"}


class RoutePathMixin:
    """Mixin to override the plugin name."""

    def _plugin_name(self) -> str:
        return ""


class TestRoute(RoutePathMixin, SimpleAPIRoute):
    """Route class with overridden plugin name for testing."""

    pass


class TestAPI(RoutePathMixin, SimpleAPI):
    """API class with overridden plugin name for testing."""

    pass


def make_event(
    method: str,
    path: str,
    query_string: str | None = None,
    body: bytes | None = None,
    headers: Mapping[str, str] | None = None,
) -> Event:
    """Make a SIMPLE_API_REQUEST event suitable for testing."""
    return Event(
        event_request=EventRequest(
            type=EventType.SIMPLE_API_REQUEST,
            target=None,
            context=json.dumps(
                {
                    "method": method,
                    "path": path,
                    "query_string": query_string or "",
                    "body": b64encode(body).decode() if body else None,
                    "headers": headers or {},
                },
                indent=None,
                separators=(",", ":"),
            ),
            target_type=None,
        )
    )


@pytest.mark.parametrize(
    argnames="method,path,query_string,body,headers",
    argvalues=[
        ("GET", "/route", "value1=a&value2=b", None, {}),
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
    request = Request(make_event(method, path, query_string, body, headers))

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

    class Route(TestRoute):
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

    handler = Route(make_event(method, path="/route"))

    effects = handler.compute()
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

    class API(TestAPI):
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

    handler = API(make_event(method, path=f"{prefix or ''}{path}"))

    effects = handler.compute()
    body = json_response_body(effects)

    assert body["method"] == method


def test_request_lifecycle() -> None:
    """Test the request-response lifecycle."""

    class Route(TestRoute):
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

    handler = Route(
        make_event(
            method="POST",
            path="/route",
            query_string="value1=a&value2=b",
            body=b'{"message": "JSON request"}',
            headers=HEADERS,
        )
    )

    effects = handler.compute()
    body = json_response_body(effects)

    assert body == {
        "body": {"message": "JSON request"},
        "headers": HEADERS,
        "method": "POST",
        "path": "/route",
        "query_string": "value1=a&value2=b",
    }


# TODO: Update the not found test once not found handling is resolved
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
        pytest.param(
            lambda: [],
            [Response(content=b"", status_code=HTTPStatus.NOT_FOUND, headers=HEADERS).apply()],
            marks=pytest.mark.xfail,
        ),
    ],
    ids=[
        "list of effects",
        "list of effects with response object",
        "list of effects with response effect",
        "no response",
        "not found",
    ],
)
def test_response(response: Callable, expected_effects: Sequence[Effect]) -> None:
    """Test the construction and return of different kinds of responses."""

    class Route(TestRoute):
        PATH = "/route"

        def get(self) -> list[Response | Effect]:
            return response()

    handler = Route(make_event(method="GET", path="/route"))

    effects = handler.compute()

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
            '{"headers": {"Canvas-Plugins-Test-Header": "test header"}, "body": null, '
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

        class API(TestAPI):
            @api.get("/route")  # type: ignore[arg-type]
            def compute(self) -> list[Response | Effect]:  # type: ignore[override]
                return [JSONResponse({})]


def test_route_missing_path_error() -> None:
    """
    Test the enforcement of the error that occurs when a SimpleAPIRoute is missing a PATH value.
    """
    with pytest.raises(PluginError):

        class Route(TestRoute):
            def get(self) -> list[Response | Effect]:
                return []


def test_route_has_prefix_error() -> None:
    """Test the enforcement of the error that occurs when a SimpleAPIRoute has a PREFIX value."""
    with pytest.raises(PluginError):

        class Route(TestRoute):
            PREFIX = "/prefix"
            PATH = "/route"

            def get(self) -> list[Response | Effect]:
                return []
