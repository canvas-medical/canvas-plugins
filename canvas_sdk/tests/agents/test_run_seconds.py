"""How long an agent's run may take, from its manifest entry."""

import pytest

from canvas_sdk.agents.run_record import DEFAULT_RUN_SECONDS, MAX_RUN_SECONDS, agent_run_seconds


@pytest.mark.parametrize(
    ("entry", "seconds"),
    [
        ({}, DEFAULT_RUN_SECONDS),
        ({"run_seconds": "900"}, DEFAULT_RUN_SECONDS),
        ({"run_seconds": True}, DEFAULT_RUN_SECONDS),
        ({"run_seconds": 20}, DEFAULT_RUN_SECONDS),
        ({"run_seconds": DEFAULT_RUN_SECONDS - 1}, DEFAULT_RUN_SECONDS),
        ({"run_seconds": 900}, 900),
        ({"run_seconds": MAX_RUN_SECONDS + 1}, MAX_RUN_SECONDS),
    ],
)
def test_a_run_gets_at_least_the_default_and_at_most_the_ceiling(entry: dict, seconds: int) -> None:
    """Less than the default would leave no model time past the deadline margin."""
    assert agent_run_seconds(entry) == seconds
