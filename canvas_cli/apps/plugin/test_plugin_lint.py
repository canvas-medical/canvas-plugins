"""Tests for the static plugin lint used by ``canvas validate``.

Two layers:

  * lint-logic tests — feed source to :func:`lint_plugin` and assert the
    findings.
  * tripwire tests — exercise the real runner sandbox / model loader and assert
    the behavior each lint rule is pinned to. If the sandbox changes (a blocked
    construct becomes allowed, or an allowed one becomes blocked), the matching
    tripwire fails and names the rule in ``plugin_lint.py`` to add or remove — so
    the lint can never silently drift from the sandbox.
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path
from tempfile import mkdtemp
from textwrap import dedent

import pytest
import requests
import typer

from canvas_cli.apps.plugin.plugin import _lint_plugin_static
from canvas_cli.apps.plugin.plugin_lint import lint_plugin
from canvas_sdk.handlers.simple_api import SimpleAPI
from canvas_sdk.handlers.simple_api.security import APIKeyAuthMixin, Credentials
from plugin_runner.sandbox import ALLOWED_MODULES, sandbox_from_module


def _plugin(files: dict[str, str], manifest: dict | None = None) -> Path:
    """Materialize a plugin dir from ``{relative_path: source}`` and return it."""
    root = Path(mkdtemp()) / "plugin_pkg"
    root.mkdir(parents=True)
    (root / "CANVAS_MANIFEST.json").write_text(
        json.dumps({"name": "plugin_pkg", **(manifest or {})})
    )
    for rel, src in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(dedent(src))
    return root


def _codes(findings: list, severity: str | None = None) -> set[str]:
    return {f.code for f in findings if severity is None or f.severity == severity}


# ── lint-logic: construct rules ───────────────────────────────────────────────


@pytest.mark.parametrize(
    "code, expected",
    [
        ("d = {}\nd['a'] += 1\n", "augmented-subscript"),
        ("obj.attr += 1\n", "augmented-attribute"),
        ("C = type('C', (object,), {})\n", "type-blocked"),
    ],
)
def test_construct_violation_flagged(code: str, expected: str) -> None:
    """Each sandbox-rejected construct is reported as an error finding."""
    root = _plugin({"handlers/h.py": code})
    assert expected in _codes(lint_plugin(root, {}), "error")


def test_frozen_and_slots_dataclass_not_flagged() -> None:
    """The sandbox allows @dataclass(frozen=True)/slots=True (see the tripwire
    below), so the lint must NOT flag them. Guards against re-introducing the
    stale rule that once did.
    """
    root = _plugin(
        {
            "handlers/h.py": """
                from dataclasses import dataclass

                @dataclass(frozen=True)
                class A:
                    x: int = 0

                @dataclass(slots=True)
                class B:
                    y: int = 0
                """
        }
    )
    assert lint_plugin(root, {}) == []


FIXTURE_PLUGIN = (
    Path(__file__).resolve().parents[3]
    / "plugin_runner"
    / "tests"
    / "fixtures"
    / "plugins"
    / "test_sandbox_lint_violations"
)

CONSTRUCT_RULES = {
    "augmented-attribute",
    "augmented-subscript",
    "type-blocked",
}


def test_fixture_plugin_reports_every_construct_rule() -> None:
    """The on-disk fixture plugin trips every construct rule, and only in
    ``violations.py``.

    This is the end-to-end counterpart to the inline cases above: a real plugin
    directory a human can point ``canvas validate`` at. Keeping the assertion
    exhaustive means adding a construct rule without adding it to the fixture
    fails here, so the fixture cannot fall behind ``plugin_lint.py``.
    """
    manifest = json.loads((FIXTURE_PLUGIN / "CANVAS_MANIFEST.json").read_text())
    findings = lint_plugin(FIXTURE_PLUGIN, manifest)
    errors = [f for f in findings if f.severity == "error"]

    assert {f.code for f in errors} == CONSTRUCT_RULES

    # The clean handler is the control: it must contribute nothing.
    assert not [f for f in findings if "clean.py" in f.location]


def test_one_arg_type_not_flagged() -> None:
    """One-argument ``type(x)`` works in the sandbox, so the lint stays silent on it."""
    root = _plugin({"handlers/h.py": "k = type(5).__name__\n"})
    assert "type-blocked" not in _codes(lint_plugin(root, {}), "error")


def test_tripwire_sandbox_allows_setattr_and_delattr() -> None:
    """The lint lets setattr() and delattr() through because the sandbox runs them."""
    assert (
        _sandbox_raises("class T:\n    pass\nt = T()\nsetattr(t, 'y', 1)\ndelattr(t, 'y')\n")
        is None
    )


def test_tripwire_sandbox_allows_one_arg_type() -> None:
    """The lint lets one-argument ``type(x)`` through because the sandbox runs it."""
    assert _sandbox_raises("k = type(5).__name__\n") is None


# ── lint-logic: request-handling rules ────────────────────────────────────────


@pytest.mark.parametrize(
    "source",
    [
        pytest.param(
            """
            class Api:
                def authenticate(self, credentials):
                    return credentials.key == self.secrets["API_KEY"]
            """,
            id="credentials_against_secret",
        ),
        pytest.param(
            """
            class Api:
                def authenticate(self, credentials):
                    expected = self.secrets.get("API_KEY")
                    return self.request.headers.get("X-Key") != expected
            """,
            id="header_against_secret_held_in_a_local",
        ),
        pytest.param(
            """
            class Api:
                def get(self):
                    if self.secrets["TOKEN"] == self.request.query_params["token"]:
                        return []
            """,
            id="secret_on_the_left",
        ),
    ],
)
def test_secret_compared_with_eq_flagged(source: str) -> None:
    """Comparing a caller-sent value with a secret using == or != is a warning."""
    root = _plugin({"handlers/api.py": source})
    assert "secret-compared-with-eq" in _codes(lint_plugin(root, {}), "warning")


@pytest.mark.parametrize(
    "source",
    [
        pytest.param(
            """
            from hmac import compare_digest

            class Api:
                def authenticate(self, credentials):
                    return compare_digest(credentials.key.encode(), self.secrets["API_KEY"].encode())
            """,
            id="compare_digest",
        ),
        pytest.param(
            """
            class Handler:
                def compute(self):
                    if self.secrets.get("FEATURE_ENABLED") == "true":
                        return []
            """,
            id="secret_used_as_a_setting",
        ),
        pytest.param(
            """
            class Api:
                def authenticate(self, credentials):
                    return credentials.key == self.expected_key()
            """,
            id="a_method_result_is_not_a_secret_read",
        ),
    ],
)
def test_secret_compared_with_eq_not_flagged(source: str) -> None:
    """A constant-time comparison, or a secret read as a setting, is not flagged."""
    root = _plugin({"handlers/api.py": source})
    assert "secret-compared-with-eq" not in _codes(lint_plugin(root, {}))


def test_requests_without_timeout_flagged() -> None:
    """A `requests` call with no `timeout` keyword is a warning naming the method."""
    root = _plugin({"handlers/h.py": "import requests\nr = requests.post(url, json={})\n"})
    findings = [f for f in lint_plugin(root, {}) if f.code == "requests-no-timeout"]

    assert [(f.severity, f.location) for f in findings] == [("warning", "handlers/h.py:2")]
    assert "`requests.post(...)`" in findings[0].message


@pytest.mark.parametrize(
    "source",
    [
        pytest.param("import requests\nr = requests.get(url, timeout=10)\n", id="timeout_given"),
        pytest.param(
            "import requests\nr = requests.get(url, **options)\n", id="kwargs_may_carry_it"
        ),
        pytest.param(
            "from canvas_sdk.utils import Http\nr = Http().get(url)\n", id="sdk_http_sets_its_own"
        ),
    ],
)
def test_requests_with_timeout_not_flagged(source: str) -> None:
    """A call that sets or may set a timeout, or goes through the SDK's Http, is not flagged."""
    root = _plugin({"handlers/h.py": source})
    assert "requests-no-timeout" not in _codes(lint_plugin(root, {}))


_OPEN_ROUTE = """
    from canvas_sdk.handlers.simple_api import Credentials, SimpleAPI, api
    from canvas_sdk.v1.data.observation import Observation

    class VitalsApp(SimpleAPI):
        {extra}
        def authenticate(self, credentials: Credentials) -> bool:
            \"\"\"Anyone.\"\"\"
            return True

        @api.get("/")
        def index(self):
            patient = self.request.query_params.get("patient")
            return list(Observation.objects.for_patient(patient))
"""


def test_unauthenticated_data_route_flagged() -> None:
    """A route class that admits everyone and reads data keyed from the request is a warning
    on its `authenticate`, naming the route.
    """
    root = _plugin({"routes/vitals.py": _OPEN_ROUTE.format(extra="")})
    findings = [f for f in lint_plugin(root, {}) if f.code == "unauthenticated-data-route"]

    assert [(f.severity, f.location) for f in findings] == [("warning", "routes/vitals.py:7")]
    assert "`VitalsApp.authenticate` always returns True, and `index` reads" in findings[0].message


def test_unauthenticated_data_route_through_a_helper_flagged() -> None:
    """A read done in a module-level helper the route calls counts."""
    source = """
        from canvas_sdk.handlers.simple_api import SimpleAPIRoute
        from canvas_sdk.v1.data import Note

        def notes_for(patient_id):
            return Note.objects.filter(patient__id=patient_id)

        class Notes(SimpleAPIRoute):
            PATH = "/notes"

            def authenticate(self, credentials):
                return True

            def get(self):
                return notes_for(self.request.path_params["patient"])
    """
    root = _plugin({"routes/notes.py": source})
    assert "unauthenticated-data-route" in _codes(lint_plugin(root, {}), "warning")


@pytest.mark.parametrize(
    "source",
    [
        pytest.param(_OPEN_ROUTE.format(extra="PUBLIC_ACCESS = True"), id="declared_public"),
        pytest.param(
            _OPEN_ROUTE.replace("return True", "return credentials is not None").format(extra=""),
            id="authenticate_checks_something",
        ),
        pytest.param(
            _OPEN_ROUTE.replace("Observation.objects.for_patient(patient)", "[patient]").format(
                extra=""
            ),
            id="no_data_read",
        ),
        pytest.param(
            _OPEN_ROUTE.replace('self.request.query_params.get("patient")', '"fixed"').format(
                extra=""
            ),
            id="no_request_input",
        ),
        pytest.param(
            """
            from canvas_sdk.handlers.simple_api import SimpleAPI, StaffSessionAuthMixin, api
            from canvas_sdk.v1.data import Patient

            class Staff(StaffSessionAuthMixin, SimpleAPI):
                @api.get("/")
                def index(self):
                    return list(Patient.objects.filter(id=self.request.query_params["id"]))
            """,
            id="auth_mixin_not_overridden",
        ),
        pytest.param(
            _OPEN_ROUTE.replace("(SimpleAPI)", "(WebSocketAPI)").format(extra=""),
            id="not_a_simple_api_class",
        ),
    ],
)
def test_unauthenticated_data_route_not_flagged(source: str) -> None:
    """Declared public, real authentication, or no request-keyed data read is not flagged."""
    root = _plugin({"routes/r.py": source})
    assert "unauthenticated-data-route" not in _codes(lint_plugin(root, {}))


def test_tripwire_simple_api_denies_unless_authenticate_is_overridden() -> None:
    """`unauthenticated-data-route` targets an override returning True because the SDK default
    denies. If the default starts admitting requests, widen the rule in plugin_lint.py.
    """
    assert (
        SimpleAPI.authenticate(SimpleAPI.__new__(SimpleAPI), Credentials.__new__(Credentials))
        is False
    )


# ── lint-logic: credential rules ──────────────────────────────────────────────

# Fake credentials, joined at runtime so this public repository never holds one whole.
_STRIPE_LIVE = "sk_" + "live_" + "Ab3" * 9
_API_KEYS = {
    "An Anthropic API key": "sk-ant-" + "api03-" + "A1b2C3" * 15,
    "A Slack token": "xox" + "b-" + "123456789012-123456789012-" + "AbCdEf123456" * 2,
    "A Stripe live key": _STRIPE_LIVE,
    "A GitHub token": "gh" + "p_" + "A1b2C3d4E5f6" * 3,
    "An OpenAI key": "sk-" + "proj-" + "A1b2C3d4" * 6,
}
_PRIVATE_KEY_PEM = (
    "-----BEGIN " + "PRIVATE KEY-----\\nMIIEvQIBADANBg\\n-----END " + "PRIVATE KEY-----"
)


@pytest.mark.parametrize("name", list(_API_KEYS))
def test_api_key_in_a_shipped_file_is_an_error(name: str) -> None:
    """Each API-key shape in a shipped file blocks validation, showing only its vendor prefix."""
    value = _API_KEYS[name]
    root = _plugin({"config/settings.json": json.dumps({"service": {"secret": value}})})
    findings = [f for f in lint_plugin(root, {}) if f.code == "hardcoded-credential"]

    assert [(f.severity, f.location) for f in findings] == [("error", "config/settings.json:1")]
    assert findings[0].message.startswith(f"{name} (`{value[:4]}…`, {len(value)} characters)")
    assert value not in findings[0].message


@pytest.mark.parametrize("path", ["cert/client.key", "tests/cert/client.key", "cert/client.txt"])
def test_private_key_warns_wherever_it_ships(path: str) -> None:
    """A private key warns rather than blocks until the SDK can load an mTLS client key from a
    secret; no part of the key is printed.
    """
    root = _plugin({path: f"{_PRIVATE_KEY_PEM}\n"})
    findings = [f for f in lint_plugin(root, {}) if f.code == "hardcoded-credential"]

    assert [(f.severity, f.location) for f in findings] == [("warning", f"{path}:1")]
    assert "mutual-TLS client key" in findings[0].message
    assert "MIIE" not in findings[0].message


@pytest.mark.parametrize("path", ["README.md", "docs/guide.rst"])
def test_api_key_in_a_markdown_or_rest_document_only_warns(path: str) -> None:
    """Documents hold example keys, so an API-key shape there warns instead of blocks."""
    root = _plugin({path: f'KEY = "{_STRIPE_LIVE}"\n'})
    findings = [f for f in lint_plugin(root, {}) if f.code == "hardcoded-credential"]

    assert [(f.severity, f.location) for f in findings] == [("warning", f"{path}:1")]


@pytest.mark.parametrize("path", ["tests/test_billing.py", "docs/setup.txt"])
def test_api_key_moved_to_tests_or_text_still_blocks(path: str) -> None:
    """Files under tests/ and .txt files ship like any other, so moving a key there is no way out."""
    root = _plugin({path: f'KEY = "{_STRIPE_LIVE}"\n'})
    assert "hardcoded-credential" in _codes(lint_plugin(root, {}), "error")


def test_files_that_do_not_ship_are_not_scanned(monkeypatch: pytest.MonkeyPatch) -> None:
    """Hidden files and what `.canvasignore` excludes never reach the package, so they are not read."""
    root = _plugin(
        {".env": f"KEY={_STRIPE_LIVE}\n", "scratch/notes.py": f'KEY = "{_STRIPE_LIVE}"\n'}
    )
    (root.parent / ".canvasignore").write_text("scratch/\n")
    monkeypatch.chdir(root.parent)

    assert "hardcoded-credential" not in _codes(lint_plugin(root, {}))


def test_binary_files_are_skipped() -> None:
    """A file that is not UTF-8 text is not scanned."""
    root = _plugin({})
    (root / "icon.png").write_bytes(b"\x89PNG\r\n\x1a\n\xff\xfe" + _STRIPE_LIVE.encode())

    assert "hardcoded-credential" not in _codes(lint_plugin(root, {}))


@pytest.mark.parametrize(
    ("source", "found"),
    [
        pytest.param('API_TOKEN = "aB3dE5fG7hJ9kL1mN3pQ"\n', True, id="random_value"),
        pytest.param('auth_token = "' + "0123456789abcdef" * 2 + '"\n', True, id="hex_token"),
        pytest.param('session_token = "' + "abcxyz" * 6 + '"\n', False, id="lowercase_not_hex"),
        pytest.param('API_KEY_SECRET_NAME = "CANVAS_PLUGIN_SIMPLE_API_KEY"\n', False, id="a_name"),
        pytest.param('TOKEN_URL = "https://auth.Example.com/oauth2/Token1"\n', False, id="a_url"),
    ],
)
def test_possible_credential_warns(source: str, found: bool) -> None:
    """A random-looking value on a secret-like name warns; secret names and URLs do not."""
    root = _plugin({"handlers/h.py": source})
    assert ("possible-credential" in _codes(lint_plugin(root, {}), "warning")) is found


def test_possible_credential_prints_only_the_length() -> None:
    """A shape-only match could be the secret itself, so no character of it is printed."""
    root = _plugin({"handlers/h.py": 'API_TOKEN = "aB3dE5fG7hJ9kL1mN3pQ"\n'})
    [finding] = [f for f in lint_plugin(root, {}) if f.code == "possible-credential"]

    assert "(20 characters)" in finding.message
    assert "aB3d" not in finding.message


def test_a_hardcoded_credential_stops_validation(capsys: pytest.CaptureFixture[str]) -> None:
    """The error severity makes `canvas validate`, and so install and deploy, exit non-zero."""
    root = _plugin({"handlers/h.py": f'KEY = "{_STRIPE_LIVE}"\n'})

    with pytest.raises(typer.Exit):
        _lint_plugin_static(root)

    out = capsys.readouterr().out
    assert "[hardcoded-credential]" in out
    assert _STRIPE_LIVE not in out


def test_tripwire_requests_is_allowed_and_has_no_default_timeout() -> None:
    """`requests-no-timeout` exists because plugins may call `requests`, which waits forever by
    default. If either changes, drop the rule in plugin_lint.py.
    """
    assert "get" in ALLOWED_MODULES["requests"]
    assert inspect.signature(requests.Session.request).parameters["timeout"].default is None


def test_tripwire_api_key_auth_mixin_compares_in_constant_time() -> None:
    """`secret-compared-with-eq` points authors at APIKeyAuthMixin, so it must keep using
    compare_digest. If it stops, change the rule's message in plugin_lint.py.
    """
    assert "compare_digest(" in inspect.getsource(APIKeyAuthMixin.authenticate)


# ── lint-logic: Custom Data rules ─────────────────────────────────────────────

_MODEL_SRC = """
    from canvas_sdk.v1.data.base import CustomModel
    from django.db.models import TextField

    class Widget(CustomModel):
        label: TextField = TextField()
"""

_CUSTOM_DATA = {"custom_data": {"namespace": "org__plugin", "access": "read_write"}}


def test_model_outside_models_dir_flagged() -> None:
    """A CustomModel outside `models/` is an error (its table won't be created)."""
    root = _plugin({"handlers/widget.py": _MODEL_SRC}, _CUSTOM_DATA)
    assert "custom-model-wrong-dir" in _codes(lint_plugin(root, _CUSTOM_DATA), "error")


def test_model_in_models_dir_not_flagged_for_location() -> None:
    """A CustomModel correctly under `models/` is not flagged for location."""
    root = _plugin({"models/widget.py": _MODEL_SRC}, _CUSTOM_DATA)
    assert "custom-model-wrong-dir" not in _codes(lint_plugin(root, _CUSTOM_DATA))


def test_missing_custom_data_block_flagged() -> None:
    """Models present but no manifest `custom_data` block is an error."""
    root = _plugin({"models/widget.py": _MODEL_SRC})
    assert "missing-custom-data-block" in _codes(lint_plugin(root, {}), "error")


def test_custom_data_block_present_no_error() -> None:
    """A model under `models/` with a `custom_data` block yields no errors."""
    root = _plugin({"models/widget.py": _MODEL_SRC}, _CUSTOM_DATA)
    assert _codes(lint_plugin(root, _CUSTOM_DATA), "error") == set()


def test_id_filter_on_custom_model_warns() -> None:
    """`.filter(id=…)` on a CustomModel warns (they key on `dbid`)."""
    root = _plugin(
        {
            "models/widget.py": _MODEL_SRC,
            "handlers/h.py": "found = Widget.objects.filter(id=1)\n",
        },
        _CUSTOM_DATA,
    )
    assert "custom-model-id-vs-dbid" in _codes(lint_plugin(root, _CUSTOM_DATA), "warning")


def test_lazy_fk_string_ref_warns() -> None:
    """A lazy string-ref FK to a local CustomModel warns (it can silently drop)."""
    root = _plugin(
        {
            "models/widget.py": _MODEL_SRC,
            "models/thing.py": """
                from canvas_sdk.v1.data.base import CustomModel
                from django.db.models import CASCADE, ForeignKey

                class Thing(CustomModel):
                    widget = ForeignKey("Widget", on_delete=CASCADE)
                """,
        },
        _CUSTOM_DATA,
    )
    assert "lazy-fk-string-ref" in _codes(lint_plugin(root, _CUSTOM_DATA), "warning")


def test_clean_plugin_no_findings() -> None:
    """A correctly-structured Custom Data plugin produces no findings."""
    root = _plugin(
        {
            "models/widget.py": _MODEL_SRC,
            "handlers/h.py": "found = Widget.objects.filter(dbid=1)\n",
        },
        _CUSTOM_DATA,
    )
    assert lint_plugin(root, _CUSTOM_DATA) == []


# ── lint-logic: file traversal & edge cases ───────────────────────────────────


def test_non_directory_root_yields_no_findings() -> None:
    """A plugin path that isn't a directory traverses to nothing (not an error)."""
    assert lint_plugin(Path("/no/such/plugin/dir"), {}) == []


def test_files_under_skipped_dirs_are_ignored() -> None:
    """Source under a SKIP_DIRS directory (e.g. `tests/`) is never linted."""
    root = _plugin({"tests/h.py": "setattr(obj, 'x', 1)\n"})
    assert lint_plugin(root, {}) == []


def test_skip_dirs_only_apply_inside_the_plugin() -> None:
    """A plugin that merely *lives* under a SKIP_DIRS-named directory is linted.

    SKIP_DIRS was matched against the absolute path, so a plugin checked out
    under any directory called ``tests``, ``build``, ``dist`` and so on had every
    file skipped and passed the lint having examined nothing.
    """
    enclosing = Path(mkdtemp()) / "tests"
    enclosing.mkdir(parents=True)
    root = enclosing / "plugin_pkg"
    root.mkdir()
    (root / "CANVAS_MANIFEST.json").write_text(json.dumps({"name": "plugin_pkg"}))
    (root / "handlers").mkdir()
    (root / "handlers" / "h.py").write_text("C = type('C', (object,), {})\n")

    assert "type-blocked" in _codes(lint_plugin(root, {}), "error")


def test_files_under_dot_dirs_are_ignored() -> None:
    """Source under any dot-directory (e.g. a stray `.tox/`) is never linted."""
    root = _plugin({".tox/h.py": "setattr(obj, 'x', 1)\n"})
    assert lint_plugin(root, {}) == []


def test_unparseable_file_is_skipped() -> None:
    """A file that fails to parse is skipped, not crashed on."""
    root = _plugin({"handlers/broken.py": "def oops(:\n"})
    assert lint_plugin(root, {}) == []


def test_custom_model_with_dotted_base_detected() -> None:
    """A CustomModel declared via a dotted base (`base.CustomModel`) is still
    recognized — here it's outside `models/`, so it's flagged for location.
    """
    root = _plugin(
        {
            "handlers/widget.py": """
                from canvas_sdk.v1.data import base

                class Widget(base.CustomModel):
                    pass
                """
        },
        _CUSTOM_DATA,
    )
    assert "custom-model-wrong-dir" in _codes(lint_plugin(root, _CUSTOM_DATA), "error")


def test_class_with_subscripted_base_is_not_a_custom_model() -> None:
    """A top-level class whose base is neither a name nor an attribute (e.g. a
    subscripted generic) is scanned without error and isn't treated as a model.
    """
    root = _plugin(
        {
            "handlers/h.py": """
                from collections.abc import Sequence

                class NotAModel(Sequence[int]):
                    pass
                """
        }
    )
    assert lint_plugin(root, {}) == []


def test_call_on_non_name_non_attr_is_ignored() -> None:
    """A call whose callable is neither a name nor an attribute (e.g. `funcs[0]()`)
    is handled gracefully and flags nothing.
    """
    root = _plugin({"handlers/h.py": "funcs = []\nfuncs[0]()\n"})
    assert lint_plugin(root, {}) == []


def test_fk_direct_class_reference_not_flagged() -> None:
    """A ForeignKey to a directly-referenced class (not a string) is fine — only
    lazy *string* refs to local CustomModels warn.
    """
    root = _plugin(
        {
            "models/widget.py": _MODEL_SRC,
            "models/thing.py": """
                from canvas_sdk.v1.data.base import CustomModel
                from django.db.models import CASCADE, ForeignKey

                from .widget import Widget

                class Thing(CustomModel):
                    widget = ForeignKey(Widget, on_delete=CASCADE)
                """,
        },
        _CUSTOM_DATA,
    )
    assert "lazy-fk-string-ref" not in _codes(lint_plugin(root, _CUSTOM_DATA))


def test_fk_string_ref_to_external_model_not_flagged() -> None:
    """A lazy FK string ref to a model NOT defined in this plugin doesn't warn —
    the rule targets only locally-defined CustomModels.
    """
    root = _plugin(
        {
            "models/widget.py": _MODEL_SRC,
            "models/thing.py": """
                from canvas_sdk.v1.data.base import CustomModel
                from django.db.models import CASCADE, ForeignKey

                class Thing(CustomModel):
                    patient = ForeignKey("canvas_sdk.Patient", on_delete=CASCADE)
                """,
        },
        _CUSTOM_DATA,
    )
    assert "lazy-fk-string-ref" not in _codes(lint_plugin(root, _CUSTOM_DATA))


# ── tripwires: pin each construct rule to real sandbox behavior ───────────────


def _sandbox_raises(source: str) -> Exception | None:
    """Execute module-level ``source`` in the real runner sandbox; return the
    exception it raised (or None if it ran clean).
    """
    temp = Path(mkdtemp())
    pkg = temp / "plugin_name" / "handlers"
    pkg.mkdir(parents=True)
    (temp / "plugin_name" / "__init__.py").touch()
    (pkg / "__init__.py").touch()
    (pkg / "handler.py").write_text(dedent(source))
    sandbox = sandbox_from_module(temp, "plugin_name.handlers.handler")
    try:
        sandbox.execute()
    except Exception as exc:  # noqa: BLE001 — we want to inspect whatever it raised
        return exc
    return None


@pytest.mark.parametrize(
    "code, rule",
    [
        ("d = {'a': 1}\nd['a'] += 1\n", "augmented-subscript"),
        ("class T:\n    x = 1\nt = T()\nt.x += 1\n", "augmented-attribute"),
        ("C = type('C', (object,), {})\n", "type-blocked"),
    ],
)
def test_tripwire_sandbox_still_rejects(code: str, rule: str) -> None:
    """Each construct the lint flags as an error must still fail in the sandbox.
    If one starts passing, the matching rule in plugin_lint.py is stale — remove
    it (this is the exact drift that shipped a false-reject before).
    """
    exc = _sandbox_raises(code)
    assert exc is not None, (
        f"Sandbox now ACCEPTS a construct the lint blocks — remove the "
        f"'{rule}' rule from plugin_lint.py (and update this tripwire)."
    )


@pytest.mark.parametrize(
    "code, kwarg",
    [
        (
            "from dataclasses import dataclass\n@dataclass(frozen=True)\nclass A:\n    x: int = 0\nA(1)\n",
            "frozen",
        ),
        (
            "from dataclasses import dataclass\n@dataclass(slots=True)\nclass A:\n    x: int = 0\nA(1)\n",
            "slots",
        ),
    ],
)
def test_tripwire_sandbox_still_allows_dataclass(code: str, kwarg: str) -> None:
    """@dataclass(frozen=/slots=True) must keep loading in the sandbox. If it
    starts failing, ADD a construct rule for it in plugin_lint.py — plugins that
    use it would otherwise fail on the instance with no lint warning.
    """
    exc = _sandbox_raises(code)
    assert exc is None, (
        f"Sandbox now REJECTS @dataclass({kwarg}=True) ({exc!r}) — add a construct "
        f"rule for it in plugin_lint.py so authors get a pre-deploy warning."
    )


# ── tripwires: pin Custom Data rules to loader / model behavior ───────────────


def test_tripwire_custom_model_pk_is_dbid() -> None:
    """The id-vs-dbid rule assumes CustomModel keys on ``dbid``. If the PK name
    changes, update the rule + message in plugin_lint.py.
    """
    from canvas_sdk.v1.data.base import CustomModel

    assert CustomModel._meta.pk.name == "dbid", (
        "CustomModel primary key is no longer 'dbid' — update the "
        "'custom-model-id-vs-dbid' rule in plugin_lint.py."
    )


def test_tripwire_models_discovered_only_from_models_dir(tmp_path: Path) -> None:
    """The custom-model-wrong-dir rule assumes the loader reads only
    ``<plugin>/models/``. If discovery widens, relax the rule.
    """
    from plugin_runner.ddl import discover_model_files

    (tmp_path / "handlers").mkdir()
    (tmp_path / "handlers" / "m.py").write_text("x = 1\n")
    assert discover_model_files(tmp_path) == [], (
        "Model discovery now looks outside <plugin>/models/ — relax the "
        "'custom-model-wrong-dir' rule in plugin_lint.py."
    )

    (tmp_path / "models").mkdir()
    (tmp_path / "models" / "widget.py").write_text("x = 1\n")
    assert (tmp_path / "models" / "widget.py") in discover_model_files(tmp_path)


def test_secret_compared_with_eq_in_a_nested_function_is_reported_once() -> None:
    """The enclosing function's walk reaches the nested one too; the comparison is one finding."""
    source = """
        class Api:
            def authenticate(self, credentials):
                def check():
                    return credentials.key == self.secrets["K"]

                return check()
    """
    root = _plugin({"handlers/a.py": source})
    findings = [f.location for f in lint_plugin(root, {}) if f.code == "secret-compared-with-eq"]

    assert findings == ["handlers/a.py:5"]


def test_possible_credential_skips_docs_and_tests() -> None:
    """Placeholder values belong in docs and tests, so a value matched by its shape alone is not
    reported there.
    """
    root = _plugin({"GUIDE.md": '"access_token": "aB3dE5fG7hJ9kL1mN3pQ"\n'})
    assert "possible-credential" not in _codes(lint_plugin(root, {}))
