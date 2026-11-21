import importlib.metadata
import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import typer

from canvas_cli.utils.runner_extra import missing_runner_packages, needs_runner

REPOSITORY = Path(__file__).resolve().parents[2]

REQUIREMENTS = [
    "django>=5.1.1,<6",
    "psycopg[binary]>=3.3.3,<4",
    'psycopg[pool]>=3.3.3,<4; extra == "runner"',
    'redis>=5.0.4,<6; extra == "runner"',
    'sentry-sdk>=2.33.2; extra == "runner"',
    'factory-boy>=3.3.3; extra == "test-utils"',
    'canvas[runner]; extra == "test-utils"',
]


def _installed_except(*absent: str) -> object:
    """A stand-in for `importlib.metadata.distribution` that finds all but ``absent``."""

    def distribution(name: str) -> object:
        if name in absent:
            raise importlib.metadata.PackageNotFoundError(name)
        return object()

    return distribution


def test_missing_runner_packages_lists_the_runner_extras_absent_distributions() -> None:
    """Only requirements under the runner extra count, and only the uninstalled ones."""
    with (
        patch("importlib.metadata.requires", return_value=REQUIREMENTS),
        patch("importlib.metadata.distribution", _installed_except("redis", "factory-boy")),
    ):
        assert missing_runner_packages() == ["redis"]


def test_missing_runner_packages_is_empty_when_the_extra_is_installed() -> None:
    """With every runner distribution present, nothing is missing."""
    with (
        patch("importlib.metadata.requires", return_value=REQUIREMENTS),
        patch("importlib.metadata.distribution", _installed_except()),
    ):
        assert missing_runner_packages() == []


def test_needs_runner_names_the_command_and_how_to_install_the_extra(
    capsys: pytest.CaptureFixture,
) -> None:
    """The stand-in command exits 1 and says to install `canvas[runner]`."""
    command = needs_runner("emit", ["grpcio", "redis"])

    with pytest.raises(typer.Exit) as exit_info:
        command()

    assert exit_info.value.exit_code == 1
    error = capsys.readouterr().err
    assert "`canvas emit`" in error
    assert "grpcio, redis" in error
    assert "pip install 'canvas[runner]'" in error


# Runs the CLI as a base install sees it: every distribution only the `runner` extra declares
# is reported missing, and every module those distributions provide fails to import.
BASE_INSTALL_SCRIPT = """
import importlib.abc
import importlib.metadata
import json
import sys

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

base, runner = set(), set()
for line in importlib.metadata.requires("canvas"):
    requirement = Requirement(line)
    name = canonicalize_name(requirement.name)
    if requirement.marker is None:
        base.add(name)
    elif requirement.marker.evaluate({"extra": "runner"}):
        runner.add(name)
runner_only = runner - base

blocked = {
    module
    for module, distributions in importlib.metadata.packages_distributions().items()
    if {canonicalize_name(d) for d in distributions} & runner_only
}

real_distribution = importlib.metadata.distribution


def distribution(name):
    if canonicalize_name(name) in runner_only:
        raise importlib.metadata.PackageNotFoundError(name)
    return real_distribution(name)


importlib.metadata.distribution = distribution


class BlockRunnerModules(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in blocked:
            raise ModuleNotFoundError(f"No module named {fullname!r}", name=fullname)
        return None


sys.meta_path.insert(0, BlockRunnerModules())

from typer.testing import CliRunner

from canvas_cli.main import app

runner = CliRunner()
results = {"blocked": sorted(blocked)}
for argv in json.loads(sys.argv[1]):
    result = runner.invoke(app, argv)
    results[" ".join(argv)] = {"exit_code": result.exit_code, "output": result.output}
print(json.dumps(results))
"""

EXAMPLE_PLUGINS = [
    "example-plugins/my_first_plugin/my_first_plugin",
    "example-plugins/api_samples/api_samples",
    "example-plugins/llm/llm_manip",
    "example-plugins/custom_data_room_booking/custom_data_room_booking",
]


def test_a_base_install_validates_plugins_and_explains_the_runner_commands(
    tmp_path: Path,
) -> None:
    """Without the runner extra, `canvas validate` (which `canvas deploy` runs) loads plugins in
    the sandbox, and the commands that need a plugin runner say how to install it.
    """
    commands = [["validate", str(REPOSITORY / plugin)] for plugin in EXAMPLE_PLUGINS]
    commands.append(["emit", "event.json"])

    completed = subprocess.run(
        [sys.executable, "-c", BASE_INSTALL_SCRIPT, json.dumps(commands)],
        cwd=REPOSITORY,
        env={**os.environ, "HOME": str(tmp_path), "CANVAS_NO_UPDATE_CHECK": "1"},
        capture_output=True,
        text=True,
        timeout=300,
    )

    assert completed.returncode == 0, completed.stderr
    results = json.loads(completed.stdout.splitlines()[-1])

    # The block has to cover the runner's packages for the rest to mean anything.
    assert {"grpc", "redis", "sentry_sdk", "statsd", "psutil", "snowflake"} <= set(
        results["blocked"]
    )

    for plugin in EXAMPLE_PLUGINS:
        result = results[f"validate {REPOSITORY / plugin}"]
        assert result["exit_code"] == 0, result["output"]
        assert "load cleanly in the sandbox" in result["output"]

    emit = results["emit event.json"]
    assert emit["exit_code"] == 1
    assert "pip install 'canvas[runner]'" in emit["output"]
