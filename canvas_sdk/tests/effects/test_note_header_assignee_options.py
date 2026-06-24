import json

import pytest
from pydantic import ValidationError

from canvas_sdk.effects.note_header_assignee_options import (
    AssigneeOption,
    AssigneeType,
    NoteHeaderAssigneeOptions,
)


def test_assignee_type_values() -> None:
    """Test that the AssigneeType enum has the expected values."""
    assert AssigneeType.STAFF.value == "staff"
    assert AssigneeType.TEAM.value == "team"


def test_apply_orders_and_filters_options() -> None:
    """Test that options serialize in the given order, preserving staff/team type."""
    effect = NoteHeaderAssigneeOptions(
        options=[
            AssigneeOption(id="team-1", type=AssigneeType.TEAM),
            AssigneeOption(id="staff-9", type=AssigneeType.STAFF),
        ]
    ).apply()

    payload = json.loads(effect.payload)
    assert payload == {
        "data": {
            "options": [
                {"id": "team-1", "type": "team"},
                {"id": "staff-9", "type": "staff"},
            ]
        }
    }


def test_apply_with_empty_options_hides_all() -> None:
    """Test that an empty list is valid and hides every staff member and team."""
    effect = NoteHeaderAssigneeOptions(options=[]).apply()
    assert json.loads(effect.payload) == {"data": {"options": []}}


def test_values_property() -> None:
    """Test that the values property returns the correct dict."""
    config = NoteHeaderAssigneeOptions(options=[AssigneeOption(id="s1", type=AssigneeType.STAFF)])
    assert config.values == {"options": [{"id": "s1", "type": "staff"}]}


def test_invalid_type_raises_validation_error() -> None:
    """Test that an option with an unrecognized type raises a validation error."""
    with pytest.raises(ValidationError):
        AssigneeOption(id="s1", type="nurse")  # type: ignore[arg-type]
