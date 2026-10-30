import pytest

from settings import agent_run_limit


@pytest.mark.parametrize(
    "requested, expected",
    [(None, 4), ("", 4), ("8", 8), ("1", 1), ("0", 1), ("-2", 1)],
)
def test_agent_run_limit_defaults_to_four_and_never_drops_to_zero(
    requested: str | None, expected: int
) -> None:
    """0 would turn every run away."""
    assert agent_run_limit(requested) == expected
