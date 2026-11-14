import pytest

from canvas_sdk.agents.subagent import MAX_PARALLEL
from plugin_runner.plugin_runner import MAX_ORPHANED_AGENT_RUNS
from settings import (
    PLUGIN_RUNNER_MAX_ORPHANED_AGENT_RUNS,
    SUBAGENT_MAX_PARALLEL,
    agent_run_limit,
    database_pool_max,
)


@pytest.mark.parametrize(
    "requested, expected",
    [(None, 4), ("", 4), ("8", 8), ("1", 1), ("0", 1), ("-2", 1)],
)
def test_agent_run_limit_defaults_to_four_and_never_drops_to_zero(
    requested: str | None, expected: int
) -> None:
    """0 would turn every run away."""
    assert agent_run_limit(requested) == expected


def test_the_pool_holds_every_worker_run_and_a_full_sub_agent_fan_out() -> None:
    """Each worker and run gets 2 connections, and each run 1 more per sub-agent thread.

    A run whose call ended keeps its connections while its slot goes to a new run, so with
    4 runs and up to 4 of those, 8 runs each fanning out to 8 sub-agents need 8 * 8
    connections on top of the 26 the workers and runs hold.
    """
    assert database_pool_max(None, workers=5, agent_runs=4, orphaned_runs=4) == (
        (5 + 8) * 2 + 8 * 8
    )
    assert database_pool_max("12", workers=5, agent_runs=4, orphaned_runs=4) == 12


def test_the_pool_counts_as_many_orphaned_runs_as_the_runner_frees() -> None:
    """The ceiling the pool is sized for is the one the plugin runner enforces."""
    assert MAX_ORPHANED_AGENT_RUNS == PLUGIN_RUNNER_MAX_ORPHANED_AGENT_RUNS


def test_the_settings_fan_out_matches_the_sdks() -> None:
    """The pool's per-run fan-out is the SDK's own limit, which settings cannot import."""
    assert SUBAGENT_MAX_PARALLEL == MAX_PARALLEL, (
        "settings.SUBAGENT_MAX_PARALLEL sizes the database pool for sub-agent fan-out; "
        "change it with canvas_sdk.agents.subagent.MAX_PARALLEL"
    )
