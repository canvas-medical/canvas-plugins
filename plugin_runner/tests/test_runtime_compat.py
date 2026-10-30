"""Patterns installed plugins rely on when their handlers run.

Each fixture handler calls into a helper module of its plugin, the way the plugins these
patterns come from do, and the test runs the handler after loading it through the
runner's own load path.
"""

import json
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import pytest

from plugin_runner import plugin_runner as plugin_runner_module
from plugin_runner.plugin_runner import HandlerLoadResult, sandbox_plugin_handlers
from plugin_runner.sandbox import SandboxMode


def _load(path: Path) -> dict[str, HandlerLoadResult]:
    """Load a fixture plugin as the runner does, keyed by handler class name."""
    components = json.loads((path / "CANVAS_MANIFEST.json").read_text())["components"]
    results = sandbox_plugin_handlers(path.name, path, components["handlers"])

    return {result.handler_class or "": result for result in results}


def _run(result: HandlerLoadResult) -> Any:
    """Run a loaded handler's compute() and return its first effect's payload."""
    assert result.error is None, result.error
    assert result.scope is not None

    assert result.handler_class is not None

    handler = result.scope[result.handler_class](event=Mock())

    return handler.compute()[0].payload


@pytest.mark.parametrize("install_test_plugin", ["test_runtime_compat_plugin"], indirect=True)
@pytest.mark.parametrize(
    ("handler", "expected"),
    [
        ("SuperCall", "QUESTION: DISPOSITION"),
        ("BuiltinsInUse", "False|ok|3.14"),
        ("NumbersAndFrames", "1760000000|True"),
        ("FuzzyMatch", "100.0"),
        ("ListItemAssignment", "a,B,c"),
        ("MissingRelation", "no supervising provider"),
        ("ModelMeta", "laborder|True|False"),
        ("ExceptionAncestry", "True"),
        ("ErrorReporting", "KeyError: \"'missing'\""),
        ("Introspection", "True|2|Does a thing."),
    ],
)
def test_helper_patterns_work_under_the_current_rules(
    install_test_plugin: Path, monkeypatch: pytest.MonkeyPatch, handler: str, expected: str
) -> None:
    """Each pattern runs under the current rules with the plugin on no list."""
    monkeypatch.setattr(plugin_runner_module, "is_always_legacy", lambda *_: False)
    monkeypatch.setattr(plugin_runner_module, "is_allowlisted", lambda *_: False)

    result = _load(install_test_plugin)[handler]

    assert result.sandbox_mode is SandboxMode.STRICT
    assert _run(result) == expected


ALWAYS_LEGACY_CASES = [
    ("PrivateSdkAttribute", "True"),
    ("LazilyImportedNonlocal", "3"),
    ("OwnModuleName", "test_always_legacy_plugin"),
]


@pytest.mark.parametrize("install_test_plugin", ["test_always_legacy_plugin"], indirect=True)
@pytest.mark.parametrize(("handler", "expected"), ALWAYS_LEGACY_CASES)
def test_listed_patterns_work_under_the_deprecated_rules(
    install_test_plugin: Path, monkeypatch: pytest.MonkeyPatch, handler: str, expected: str
) -> None:
    """A plugin on the always list runs these patterns when its handlers run."""
    monkeypatch.setattr(plugin_runner_module, "is_always_legacy", lambda *_: True)

    with patch.object(plugin_runner_module.sentry_sdk, "capture_message"):
        result = _load(install_test_plugin)[handler]

    assert result.sandbox_mode is SandboxMode.LEGACY_PERMISSIVE
    assert _run(result) == expected


@pytest.mark.parametrize("install_test_plugin", ["test_always_legacy_plugin"], indirect=True)
@pytest.mark.parametrize(("handler", "expected"), ALWAYS_LEGACY_CASES)
def test_listed_patterns_fail_when_the_plugin_is_not_listed(
    install_test_plugin: Path, monkeypatch: pytest.MonkeyPatch, handler: str, expected: str
) -> None:
    """The same patterns fail under the current rules, which is why the plugin is listed.

    They load cleanly and fail only once the handler runs.
    """
    monkeypatch.setattr(plugin_runner_module, "is_always_legacy", lambda *_: False)
    monkeypatch.setattr(plugin_runner_module, "is_allowlisted", lambda *_: False)

    result = _load(install_test_plugin)[handler]

    assert result.error is None
    assert result.sandbox_mode is SandboxMode.STRICT

    with pytest.raises((AttributeError, RuntimeError)):
        _run(result)


@pytest.mark.parametrize("install_test_plugin", ["test_allowlisted_load_plugin"], indirect=True)
def test_an_allowlisted_load_time_dependency_loads_and_runs(
    install_test_plugin: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An allowlisted plugin that reads an ungranted module name loads and runs."""
    monkeypatch.setattr(plugin_runner_module, "is_always_legacy", lambda *_: False)
    monkeypatch.setattr(plugin_runner_module, "is_allowlisted", lambda *_: True)

    with patch.object(plugin_runner_module.sentry_sdk, "capture_message"):
        result = _load(install_test_plugin)["PrecisionCheck"]

    assert result.sandbox_mode is SandboxMode.LEGACY_PERMISSIVE
    assert _run(result) == "True"


@pytest.mark.parametrize("install_test_plugin", ["test_allowlisted_load_plugin"], indirect=True)
def test_an_unlisted_load_time_dependency_is_refused_naming_it(
    install_test_plugin: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Without an entry the same plugin is refused at load, naming what to change."""
    monkeypatch.setattr(plugin_runner_module, "is_always_legacy", lambda *_: False)
    monkeypatch.setattr(plugin_runner_module, "is_allowlisted", lambda *_: False)

    result = _load(install_test_plugin)["PrecisionCheck"]

    assert result.error is not None
    assert "decimal.getcontext" in str(result.error)
