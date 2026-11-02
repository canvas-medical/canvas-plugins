import pytest

from canvas_sdk.agents.subagent import MAX_PARALLEL
from settings import SUBAGENT_MAX_PARALLEL, agent_run_limit, database_pool_max


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

    With the defaults, 4 runs each fanning out to 8 sub-agents need 4 * 8 connections on
    top of the 18 the workers and runs hold, so event handling never waits on the pool.
    """
    assert database_pool_max(None, workers=5, agent_runs=4) == (5 + 4) * 2 + 4 * 8
    assert database_pool_max("12", workers=5, agent_runs=4) == 12


def test_the_settings_fan_out_matches_the_sdks() -> None:
    """The pool's per-run fan-out is the SDK's own limit, which settings cannot import."""
    assert SUBAGENT_MAX_PARALLEL == MAX_PARALLEL, (
        "settings.SUBAGENT_MAX_PARALLEL sizes the database pool for sub-agent fan-out; "
        "change it with canvas_sdk.agents.subagent.MAX_PARALLEL"
    )
