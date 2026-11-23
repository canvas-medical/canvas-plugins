import json
from collections.abc import Iterator
from typing import Any
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.refill_request import UpdateRefillRequest

REFILL_ID = uuid4()
STAFF_KEY = "staff-abc"

# _get_error_details checks the DB; mock the managers (mirrors test_redirect.py).
REFILL_OBJECTS = "canvas_sdk.effects.refill_request.RefillRequest.objects"
STAFF_FILTER = "canvas_sdk.effects.refill_request.Staff.objects.filter"


@pytest.fixture
def refills() -> Iterator[MagicMock]:
    """RefillRequest.objects, defaulting to a request that exists and is pending."""
    with patch(REFILL_OBJECTS) as objects:
        objects.pending.return_value.filter.return_value.exists.return_value = True
        objects.filter.return_value.exists.return_value = True
        yield objects


@pytest.fixture
def staff() -> Iterator[MagicMock]:
    """Staff.objects.filter, defaulting to a staff that exists."""
    with patch(STAFF_FILTER) as staff_filter:
        staff_filter.return_value.exists.return_value = True
        yield staff_filter


def _payload(effect: UpdateRefillRequest) -> dict[str, Any]:
    """The `data` dict of the effect's JSON payload."""
    return json.loads(effect.apply().payload)["data"]


def test_apply_produces_the_update_refill_request_effect_type(
    refills: MagicMock, staff: MagicMock
) -> None:
    """apply() emits an effect of type UPDATE_REFILL_REQUEST."""
    effect = UpdateRefillRequest(id=REFILL_ID, assignee_id=STAFF_KEY).apply()

    assert effect.type == EffectType.UPDATE_REFILL_REQUEST


def test_assignee_payload_has_a_stringified_id(refills: MagicMock, staff: MagicMock) -> None:
    """The id is stringified so json.dumps succeeds; unset fields are sent as null."""
    data = _payload(UpdateRefillRequest(id=REFILL_ID, assignee_id=STAFF_KEY))

    assert data == {"id": str(REFILL_ID), "assignee_id": STAFF_KEY, "ignored": None}


def test_ignore_payload(refills: MagicMock, staff: MagicMock) -> None:
    """Ignoring alone needs no assignee and skips the staff lookup."""
    data = _payload(UpdateRefillRequest(id=REFILL_ID, ignored=True))

    assert data == {"id": str(REFILL_ID), "assignee_id": None, "ignored": True}
    staff.assert_not_called()


def test_assign_and_ignore_together(refills: MagicMock, staff: MagicMock) -> None:
    """Both fields can be sent in one effect."""
    data = _payload(UpdateRefillRequest(id=REFILL_ID, assignee_id=STAFF_KEY, ignored=True))

    assert data == {"id": str(REFILL_ID), "assignee_id": STAFF_KEY, "ignored": True}


def test_accepts_a_string_id_and_coerces_it(refills: MagicMock, staff: MagicMock) -> None:
    """Field(strict=False) lets a plugin pass a string id, coerced to a UUID."""
    data = _payload(UpdateRefillRequest(id=str(REFILL_ID), assignee_id=STAFF_KEY))  # type: ignore[arg-type]

    assert data["id"] == str(REFILL_ID)


def test_neither_assignee_nor_ignored_is_rejected(refills: MagicMock, staff: MagicMock) -> None:
    """An update with nothing to change fails validation at apply()."""
    with pytest.raises(ValidationError, match="At least one of 'assignee_id' or 'ignored'"):
        UpdateRefillRequest(id=REFILL_ID).apply()


def test_un_ignore_is_rejected(refills: MagicMock, staff: MagicMock) -> None:
    """ignored=False fails validation at apply()."""
    with pytest.raises(ValidationError, match="Un-ignoring a refill request is not supported"):
        UpdateRefillRequest(id=REFILL_ID, ignored=False).apply()


def test_empty_assignee_id_is_rejected() -> None:
    """An empty assignee_id is rejected at construction."""
    with pytest.raises(ValidationError):
        UpdateRefillRequest(id=REFILL_ID, assignee_id="")


def test_apply_raises_when_the_refill_request_does_not_exist(
    refills: MagicMock, staff: MagicMock
) -> None:
    """A non-existent refill id fails validation at apply()."""
    refills.pending.return_value.filter.return_value.exists.return_value = False
    refills.filter.return_value.exists.return_value = False

    with pytest.raises(ValidationError, match="does not exist"):
        UpdateRefillRequest(id=REFILL_ID, ignored=True).apply()


@pytest.mark.parametrize(
    "fields",
    [{"ignored": True}, {"assignee_id": STAFF_KEY}],
    ids=["ignore", "assign"],
)
def test_apply_raises_when_the_refill_request_is_not_pending(
    refills: MagicMock, staff: MagicMock, fields: dict[str, Any]
) -> None:
    """An ignored or answered request can't be updated."""
    refills.pending.return_value.filter.return_value.exists.return_value = False

    with pytest.raises(ValidationError, match="is not pending"):
        UpdateRefillRequest(id=REFILL_ID, **fields).apply()

    refills.pending.return_value.filter.assert_called_with(id=REFILL_ID)


def test_apply_raises_when_the_staff_does_not_exist(refills: MagicMock, staff: MagicMock) -> None:
    """A non-existent assignee id fails validation at apply()."""
    staff.return_value.exists.return_value = False

    with pytest.raises(ValidationError, match="Staff with id"):
        UpdateRefillRequest(id=REFILL_ID, assignee_id=STAFF_KEY).apply()


def test_id_is_required_at_construction() -> None:
    """Id is a required field — constructing without it raises."""
    with pytest.raises(ValidationError):
        UpdateRefillRequest(assignee_id=STAFF_KEY)  # type: ignore[call-arg]


def test_a_non_uuid_id_is_rejected() -> None:
    """Id must be a UUID (strings are coerced; garbage is rejected)."""
    with pytest.raises(ValidationError):
        UpdateRefillRequest(id="not-a-uuid", assignee_id=STAFF_KEY)  # type: ignore[arg-type]
