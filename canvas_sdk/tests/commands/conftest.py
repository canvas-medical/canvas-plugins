"""Fixtures shared by the command tests."""

from collections.abc import Iterator
from unittest.mock import MagicMock, patch

import pytest

from canvas_sdk.v1.data.command import Command


@pytest.fixture
def stored_command() -> Iterator[MagicMock]:
    """Stub the command-state lookup so an effect that changes a stored command can be built.

    Before building such an effect a command checks that its stored counterpart is in a state that
    allows it, which a test constructing a command in isolation has no database to answer. This
    answers affirmatively whichever state the method asks for, leaving the test free to assert on
    the effect itself. Tests that are about the state rules should stub the lookup themselves.
    """
    manager = MagicMock()
    manager.filter.return_value.exists.return_value = True
    with patch.object(Command, "objects", manager):
        yield manager
