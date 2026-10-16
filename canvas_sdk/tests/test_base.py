"""Tests for the SDK model base classes."""

import pytest
from pydantic import ValidationError

from canvas_sdk.base import TrackableFieldsModel


class _Tracked(TrackableFieldsModel):
    """A model with one strictly typed field."""

    class Meta:
        effect_type = "TEST"

    count: int | None = None


def test_a_rejected_assignment_leaves_the_field_clean() -> None:
    """A value that fails validation is neither marked dirty nor sent."""
    model = _Tracked()

    with pytest.raises(ValidationError):
        model.count = "many"  # type: ignore[assignment]

    assert not model.is_dirty("count")
    assert "count" not in model.values


def test_an_accepted_assignment_marks_the_field_dirty() -> None:
    """A valid value is marked dirty and sent."""
    model = _Tracked()

    model.count = 3

    assert model.is_dirty("count")
    assert model.values == {"count": 3}
