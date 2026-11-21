"""Whether the `canvas[runner]` packages are installed.

A base `canvas` install carries what the CLI and the sandbox check need. The packages a running
plugin runner uses (gRPC, Redis, Sentry, StatsD, and libraries the sandbox lets plugins import,
such as the Snowflake connector) come with `pip install 'canvas[runner]'`.
"""

import importlib.metadata
import sys
from collections.abc import Callable

import typer
from packaging.requirements import Requirement

RUNNER_EXTRA = "runner"
INSTALL_RUNNER_EXTRA = "pip install 'canvas[runner]'"


def missing_runner_packages() -> list[str]:
    """The distributions the `runner` extra declares that are not installed."""
    missing = []

    for line in importlib.metadata.requires("canvas") or []:
        requirement = Requirement(line)

        if requirement.marker is None or not requirement.marker.evaluate({"extra": RUNNER_EXTRA}):
            continue

        # The marker names the extra; one that holds without it applies to every install.
        if requirement.marker.evaluate({"extra": ""}):
            continue

        try:
            importlib.metadata.distribution(requirement.name)
        except importlib.metadata.PackageNotFoundError:
            missing.append(requirement.name)

    return missing


def needs_runner(command: str, missing: list[str]) -> Callable[[], None]:
    """A stand-in for a command that needs the `runner` extra, which says how to install it."""

    def command_needing_runner() -> None:
        print(
            f"`canvas {command}` needs the plugin runner's packages, which this install does "
            f"not have ({', '.join(missing)}). Install them with `{INSTALL_RUNNER_EXTRA}`.",
            file=sys.stderr,
        )
        raise typer.Exit(1)

    command_needing_runner.__doc__ = f"Needs `{INSTALL_RUNNER_EXTRA}`."

    return command_needing_runner
