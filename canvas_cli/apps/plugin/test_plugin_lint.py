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

import json
from pathlib import Path
from tempfile import mkdtemp
from textwrap import dedent

import pytest

from canvas_cli.apps.plugin.plugin_lint import lint_plugin
from plugin_runner.sandbox import sandbox_from_module


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
        ("setattr(obj, 'x', 1)\n", "setattr-blocked"),
        ("delattr(obj, 'x')\n", "delattr-blocked"),
        ("b = bytearray(b'x')\n", "bytearray-blocked"),
        ("C = type('C', (object,), {})\n", "type-3arg-blocked"),
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


def test_one_arg_type_not_flagged() -> None:
    """Only 3-arg dynamic class creation is flagged; ordinary ``type(x)`` is not
    the class-creation anti-pattern the rule targets.
    """
    root = _plugin({"handlers/h.py": "k = type(5)\n"})
    assert "type-3arg-blocked" not in _codes(lint_plugin(root, {}))


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
        ("class T:\n    pass\nsetattr(T(), 'x', 1)\n", "setattr-blocked"),
        ("class T:\n    x = 1\ndelattr(T(), 'x')\n", "delattr-blocked"),
        ("b = bytearray(b'x')\n", "bytearray-blocked"),
        ("C = type('C', (object,), {})\n", "type-3arg-blocked"),
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
