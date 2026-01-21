from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_event() -> MagicMock:
    """Create a mock event with note context."""
    event = MagicMock()
    event.context = {"note": {"id": "note-123"}}
    return event
