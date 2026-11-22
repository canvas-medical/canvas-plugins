"""Tests for pytest-canvas, run as a separate pytest session against a throwaway plugin."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PYTEST_CANVAS_DIR = REPO_ROOT / "pytest-canvas"

MODEL = """\
from django.db.models import TextField

from canvas_sdk.v1.data.base import CustomModel


class Widget(CustomModel):
    name = TextField()
"""

PLUGIN_TEST = """\
from {plugin}.models.widget import Widget


def test_widget_table_exists():
    Widget.objects.create(name="first")

    assert Widget.objects.count() == 1
"""


def write_plugin(root: Path, plugin: str, *, nested: bool) -> Path:
    """Write a plugin with one CustomModel and one test that uses it; return its tests dir.

    Nested is the layout `canvas init` scaffolds (plugin/plugin/models); flat keeps the
    manifest and models directly in the rootdir (plugin/models).
    """
    rootdir = root / plugin
    package = rootdir / plugin if nested else rootdir
    (package / "models").mkdir(parents=True)
    (package / "__init__.py").write_text("")
    (package / "models" / "__init__.py").write_text("")
    (package / "models" / "widget.py").write_text(MODEL)
    (package / "CANVAS_MANIFEST.json").write_text(json.dumps({"name": plugin}))
    (rootdir / "pyproject.toml").write_text(
        f'[project]\nname = "{plugin}"\n\n[tool.pytest.ini_options]\npython_files = ["test_*.py"]\n'
    )
    tests = rootdir / "tests"
    tests.mkdir()
    (tests / "__init__.py").write_text("")
    (tests / "test_widget.py").write_text(PLUGIN_TEST.format(plugin=plugin))
    return tests


def run_pytest(tests: Path) -> subprocess.CompletedProcess[str]:
    """Run pytest with pytest-canvas on a plugin's tests, from the repo root as CI does."""
    env = {
        **os.environ,
        "CUSTOMER_IDENTIFIER": "ci-unit-tests",
        "PYTHONPATH": os.pathsep.join([str(PYTEST_CANVAS_DIR), str(REPO_ROOT)]),
    }
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "pytest_canvas.plugin", "-p", "no:cacheprovider"]
        + ["--no-cov", "-q", str(tests)],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        check=False,
        text=True,
        timeout=120,
    )


@pytest.mark.parametrize("nested", [True, False], ids=["nested", "flat"])
def test_creates_custom_model_tables(tmp_path: Path, nested: bool) -> None:
    """The plugin's CustomModel tables exist in the test database in either layout."""
    plugin = "nested_plugin" if nested else "flat_plugin"
    result = run_pytest(write_plugin(tmp_path, plugin, nested=nested))

    assert result.returncode == 0, result.stdout + result.stderr
    assert "1 passed" in result.stdout
