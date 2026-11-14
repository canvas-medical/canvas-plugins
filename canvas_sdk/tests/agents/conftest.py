import pytest

from canvas_sdk.test_utils.agents import turn_on_command_types


@pytest.fixture(autouse=True)
def command_types_on(request: pytest.FixtureRequest) -> None:
    """Every command type is on, as in a new instance, for the tests that use the database."""
    if request.node.get_closest_marker("django_db") is not None:
        turn_on_command_types()
