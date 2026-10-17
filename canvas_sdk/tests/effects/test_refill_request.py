import json
from unittest.mock import patch
from uuid import uuid4

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.refill_request import UpdateRefillRequest

REFILL_ID = uuid4()
STAFF_KEY = "staff-abc"

# _get_error_details checks existence in the DB; mock those managers (mirrors test_redirect.py).
REFILL_FILTER = "canvas_sdk.effects.refill_request.RefillRequest.objects.filter"
STAFF_FILTER = "canvas_sdk.effects.refill_request.Staff.objects.filter"


@patch(STAFF_FILTER)
@patch(REFILL_FILTER)
def test_apply_produces_the_update_refill_request_effect_type(mock_refill, mock_staff) -> None:  # type: ignore[no-untyped-def]
    """apply() emits an effect of type UPDATE_REFILL_REQUEST."""
    mock_refill.return_value.exists.return_value = True
    mock_staff.return_value.exists.return_value = True

    effect = UpdateRefillRequest(id=REFILL_ID, assignee_id=STAFF_KEY).apply()

    assert effect.type == EffectType.UPDATE_REFILL_REQUEST


@patch(STAFF_FILTER)
@patch(REFILL_FILTER)
def test_payload_is_flat_with_a_stringified_id(mock_refill, mock_staff) -> None:  # type: ignore[no-untyped-def]
    """The payload is {id, assignee_id} and the id is stringified so json.dumps succeeds."""
    mock_refill.return_value.exists.return_value = True
    mock_staff.return_value.exists.return_value = True

    # Reaching a parsed payload at all proves apply() didn't choke serializing a raw UUID.
    data = json.loads(UpdateRefillRequest(id=REFILL_ID, assignee_id=STAFF_KEY).apply().payload)[
        "data"
    ]

    assert data == {"id": str(REFILL_ID), "assignee_id": STAFF_KEY}


@patch(STAFF_FILTER)
@patch(REFILL_FILTER)
def test_accepts_a_string_id_and_coerces_it(mock_refill, mock_staff) -> None:  # type: ignore[no-untyped-def]
    """Field(strict=False) lets a plugin pass a string id, coerced to a UUID."""
    mock_refill.return_value.exists.return_value = True
    mock_staff.return_value.exists.return_value = True

    data = json.loads(
        UpdateRefillRequest(id=str(REFILL_ID), assignee_id=STAFF_KEY).apply().payload  # type: ignore[arg-type]
    )["data"]

    assert data["id"] == str(REFILL_ID)


def test_empty_assignee_id_is_rejected() -> None:
    """A refill is always assigned — an empty assignee_id is rejected at construction."""
    with pytest.raises(ValidationError):
        UpdateRefillRequest(id=REFILL_ID, assignee_id="")


@patch(STAFF_FILTER)
@patch(REFILL_FILTER)
def test_apply_raises_when_the_refill_request_does_not_exist(mock_refill, mock_staff) -> None:  # type: ignore[no-untyped-def]
    """A non-existent refill id fails validation at apply()."""
    mock_refill.return_value.exists.return_value = False
    mock_staff.return_value.exists.return_value = True

    with pytest.raises(ValidationError) as exc_info:
        UpdateRefillRequest(id=REFILL_ID, assignee_id=STAFF_KEY).apply()

    assert "Refill request with id" in repr(exc_info.value)


@patch(STAFF_FILTER)
@patch(REFILL_FILTER)
def test_apply_raises_when_the_staff_does_not_exist(mock_refill, mock_staff) -> None:  # type: ignore[no-untyped-def]
    """A non-existent assignee id fails validation at apply()."""
    mock_refill.return_value.exists.return_value = True
    mock_staff.return_value.exists.return_value = False

    with pytest.raises(ValidationError) as exc_info:
        UpdateRefillRequest(id=REFILL_ID, assignee_id=STAFF_KEY).apply()

    assert "Staff with id" in repr(exc_info.value)


def test_id_is_required_at_construction() -> None:
    """Id is a required field — constructing without it raises."""
    with pytest.raises(ValidationError):
        UpdateRefillRequest(assignee_id=STAFF_KEY)  # type: ignore[call-arg]


def test_assignee_id_is_required_at_construction() -> None:
    """assignee_id is a required field — constructing without it raises."""
    with pytest.raises(ValidationError):
        UpdateRefillRequest(id=REFILL_ID)  # type: ignore[call-arg]


def test_a_non_uuid_id_is_rejected() -> None:
    """Id must be a UUID (strings are coerced; garbage is rejected)."""
    with pytest.raises(ValidationError):
        UpdateRefillRequest(id="not-a-uuid", assignee_id=STAFF_KEY)  # type: ignore[arg-type]
