"""The resolver cutoff is recorded in uv.lock, and stays recorded.

`[tool.uv] exclude-newer` in pyproject.toml holds dependency resolution to the
index as it stood 7 days ago. uv writes that setting into uv.lock's `[options]`
table on every lock, and any tool that relocks without reading the project
config drops the table, which silently widens the cutoff for everyone who locks
afterwards. These tests fail on a lock written that way.
"""

import tomllib
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).parent.parent

# Lint and type-check tooling is exempt from the cutoff so it tracks latest.
TOOLING_EXEMPT_FROM_CUTOFF = {"ruff", "ty", "uv"}


def _pyproject() -> dict[str, Any]:
    return tomllib.loads((REPO_ROOT / "pyproject.toml").read_text())


def _lock_options() -> dict[str, Any]:
    return tomllib.loads((REPO_ROOT / "uv.lock").read_text()).get("options", {})


def test_pyproject_declares_the_resolver_cutoff() -> None:
    """pyproject.toml is the source of truth for the cutoff."""
    assert _pyproject()["tool"]["uv"]["exclude-newer"] == "7 days", (
        "[tool.uv] exclude-newer in pyproject.toml is what makes every machine, CI, and the "
        "semantic release job resolve against the same index snapshot. Restore it rather than "
        "relying on a per-contributor uv config."
    )


def test_uv_lock_records_the_resolver_cutoff() -> None:
    """uv.lock carries the cutoff it was resolved under."""
    assert _lock_options().get("exclude-newer-span") == "P7D", (
        "uv.lock lost its [options] exclude-newer-span. Something relocked without reading "
        "[tool.uv] in pyproject.toml. Re-run `uv lock` and commit the result; if a CI job wrote "
        "this lock, that job needs the project config on disk."
    )


def test_uv_lock_exempts_the_lint_and_type_tooling() -> None:
    """The tooling exemptions survive a relock alongside the cutoff."""
    exempt = _lock_options().get("exclude-newer-package", {})

    assert exempt.keys() >= TOOLING_EXEMPT_FROM_CUTOFF, (
        f"uv.lock is missing exclude-newer-package entries for "
        f"{sorted(TOOLING_EXEMPT_FROM_CUTOFF - exempt.keys())}. Re-run `uv lock` and commit the "
        f"result."
    )
