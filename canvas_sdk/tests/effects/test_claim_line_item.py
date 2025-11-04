from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.claim_line_item import UpdateClaimLineItem


@pytest.fixture
def mock_db_queries() -> Generator[dict[str, MagicMock]]:
    """Mock all database queries to return True/exist by default."""
    with (
        patch("canvas_sdk.effects.claim_line_item.ClaimLineItem.objects") as mock_claim_line_item,
    ):
        # Setup default behaviors - objects exist
        mock_claim_line_item.filter.return_value.exists.return_value = True

        yield {"claim_line_item": mock_claim_line_item}


def test_requires_existing_claim_line_item_id(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that the claim_line_item_id is valid and the claim exists."""
    mock_db_queries["claim_line_item"].filter.return_value.exists.return_value = False
    update = UpdateClaimLineItem(claim_line_item_id="something-wrong")
    with pytest.raises(ValidationError) as e:
        update.apply()

    err_msg = repr(e.value)
    assert "Claim Line Item does not exist" in err_msg


def test_payload_with_charge(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that the charge is included in the data payload."""
    update = UpdateClaimLineItem(claim_line_item_id="something-right", charge=150.75)
    payload = update.apply()
    assert payload.type == EffectType.UPDATE_CLAIM_LINE_ITEM
    assert (
        payload.payload == '{"data": {"charge": "150.75"}, "claim_line_item_id": "something-right"}'
    )


def test_payload_with_no_charge(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that the charge is not included in the data payload."""
    update = UpdateClaimLineItem(claim_line_item_id="something-right")
    payload = update.apply()
    assert payload.type == EffectType.UPDATE_CLAIM_LINE_ITEM
    assert payload.payload == '{"data": {}, "claim_line_item_id": "something-right"}'


def test_payload_with_zero_charge(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that a charge of 0 is included in the data payload."""
    update = UpdateClaimLineItem(claim_line_item_id="something-right", charge=0)
    payload = update.apply()
    assert payload.type == EffectType.UPDATE_CLAIM_LINE_ITEM
    assert payload.payload == '{"data": {"charge": "0.0"}, "claim_line_item_id": "something-right"}'
