import ast
from pathlib import Path
from textwrap import dedent
from unittest.mock import patch

import pytest

from canvas_sdk.events import Event, EventRequest, EventType
from plugin_runner import plugin_runner as plugin_runner_module
from plugin_runner.open_routes import find_open_routes, open_routes_in_module


def _open(source: str) -> list[tuple[str, str]]:
    return [
        (route.class_name, route.kind) for route in open_routes_in_module(ast.parse(dedent(source)))
    ]


_ROUTE = """
    from canvas_sdk.handlers.simple_api import SimpleAPI, api
    from canvas_sdk.v1.data import Patient

    class Chart(SimpleAPI):
        def authenticate(self, credentials):
            {body}

        @api.get("/")
        def index(self):
            return list(Patient.objects.filter(id=self.request.query_params["id"]))
"""


@pytest.mark.parametrize(
    ("body", "kind"),
    [
        pytest.param("return True", "always-true", id="return_true"),
        pytest.param('"""Anyone."""\n            return True', "always-true", id="docstring"),
        pytest.param(
            'log.warning("called")\n            return True', "always-true", id="logging_first"
        ),
        pytest.param(
            "return True  # dev only\n            return credentials.key == self.secrets['K']",
            "always-true",
            id="dead_code_after_return",
        ),
        pytest.param("return self.event.actor is not None", "actor-exists", id="actor_not_none"),
        pytest.param("return bool(self.event.actor)", "actor-exists", id="bool_actor"),
        pytest.param("return bool(credentials.token)", "credential-exists", id="bool_token"),
        pytest.param(
            "return credentials.token is not None", "credential-exists", id="token_not_none"
        ),
        pytest.param('return credentials.token != ""', "credential-exists", id="token_not_empty"),
        pytest.param("return credentials is not None", "credential-exists", id="credentials"),
        pytest.param(
            "return bool(credentials.token) and self.event.actor is not None",
            "credential-exists",
            id="both_presence_checks",
        ),
    ],
)
def test_authenticate_that_admits_everyone_is_found(body: str, kind: str) -> None:
    """Each of these lets an anonymous caller through, so the route is reported with its kind."""
    assert _open(_ROUTE.format(body=body)) == [("Chart", kind)]


@pytest.mark.parametrize(
    "body",
    [
        pytest.param("return self.event.actor.id is not None", id="actor_id"),
        pytest.param(
            "return bool(credentials.token and self.event.actor and self.event.actor.id)",
            id="token_and_actor_id",
        ),
        pytest.param('return credentials.key == self.secrets["KEY"]', id="key_compared"),
        pytest.param('return credentials.logged_in_user["type"] == "Staff"', id="staff"),
        pytest.param("return False", id="false"),
        pytest.param(
            "if not credentials.token:\n                return False\n            return True",
            id="branch",
        ),
    ],
)
def test_authenticate_that_checks_identity_is_not_found(body: str) -> None:
    """A check a caller can fail is left alone."""
    assert _open(_ROUTE.format(body=body)) == []


def test_public_access_opt_out() -> None:
    """A class that declares itself public on purpose is not reported."""
    source = _ROUTE.format(body="return True").replace(
        "class Chart(SimpleAPI):", "class Chart(SimpleAPI):\n        PUBLIC_ACCESS = True"
    )
    assert _open(source) == []


def test_route_that_reads_request_without_canvas_data_is_found() -> None:
    """A route keyed off request input counts even when it calls something other than the ORM,
    such as storage or another service.
    """
    source = """
        from canvas_sdk.handlers.simple_api import SimpleAPI, api

        class Files(SimpleAPI):
            def authenticate(self, credentials):
                return True

            @api.get("/list_items")
            def list_items(self):
                return storage.list(self.request.query_params["patient"])
    """
    assert _open(source) == [("Files", "always-true")]


def test_fixed_asset_route_is_not_found() -> None:
    """A route that serves only a fixed asset is left alone."""
    source = """
        from canvas_sdk.handlers.simple_api import SimpleAPI, api

        class Assets(SimpleAPI):
            def authenticate(self, credentials):
                return True

            @api.get("/style.css")
            def css(self):
                return render_to_string("templates/style.css")
    """
    assert _open(source) == []


def test_websocket_that_admits_everyone_is_found() -> None:
    """A WebSocketAPI's channel is its data, so an open one counts with no route method."""
    source = """
        from canvas_sdk.handlers.simple_api import WebSocketAPI

        class Updates(WebSocketAPI):
            def authenticate(self) -> bool:
                return True
    """
    assert _open(source) == [("Updates", "always-true")]


def test_find_open_routes_skips_tests(tmp_path: Path) -> None:
    """Plugin tests are not loaded by the runner, so an open handler there is not reported."""
    (tmp_path / "routes").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "routes" / "chart.py").write_text(dedent(_ROUTE.format(body="return True")))
    (tmp_path / "tests" / "test_chart.py").write_text(dedent(_ROUTE.format(body="return True")))

    assert [(str(rel), route.line) for rel, route in find_open_routes(tmp_path)] == [
        ("routes/chart.py", 6)
    ]


def test_report_open_routes_alerts_and_does_not_block(tmp_path: Path) -> None:
    """The runner reports an open plugin to Sentry once per load, at error level."""
    (tmp_path / "chart.py").write_text(dedent(_ROUTE.format(body="return True")))

    with patch.object(plugin_runner_module.sentry_sdk, "capture_message") as capture_message:
        plugin_runner_module._report_open_routes("open_plugin", tmp_path)

    capture_message.assert_called_once()
    assert capture_message.call_args.kwargs["level"] == "error"
    assert '"open_plugin"' in capture_message.call_args.args[0]


def test_report_open_routes_is_quiet_for_a_closed_plugin(tmp_path: Path) -> None:
    """A plugin with no open handlers produces no report."""
    (tmp_path / "chart.py").write_text(
        dedent(_ROUTE.format(body="return self.event.actor.id is not None"))
    )

    with patch.object(plugin_runner_module.sentry_sdk, "capture_message") as capture_message:
        plugin_runner_module._report_open_routes("closed_plugin", tmp_path)

    capture_message.assert_not_called()


def test_report_open_routes_survives_a_failed_check(tmp_path: Path) -> None:
    """An error inside the check is logged and never stops the plugin loading."""
    with (
        patch.object(plugin_runner_module, "find_open_routes", side_effect=RuntimeError("boom")),
        patch.object(plugin_runner_module.sentry_sdk, "capture_message") as capture_message,
    ):
        plugin_runner_module._report_open_routes("any_plugin", tmp_path)

    capture_message.assert_not_called()


def test_tripwire_event_always_has_an_actor() -> None:
    """`actor-exists` reports `self.event.actor is not None` because the SDK attaches an Actor
    even when no one is signed in. If an anonymous request ever gets `actor = None`, that check
    becomes real: drop the `actor-exists` kind from plugin_runner/open_routes.py.
    """
    event = Event(EventRequest(type=EventType.SIMPLE_API_REQUEST))

    assert event.actor is not None
    assert event.actor.id in (None, "")
