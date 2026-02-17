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
        mock_claim_line_item.filter.return_value.first.return_value = True

        yield {"claim_line_item": mock_claim_line_item}


def test_requires_existing_claim_line_item_id(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that the claim_line_item_id is valid and the claim exists."""
    mock_db_queries["claim_line_item"].filter.return_value.first.return_value = False
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


def test_payload_with_linked_diagnosis_codes(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that linked_diagnosis_codes is included in the data payload."""
    # Mock the claim line item with diagnosis codes
    mock_item = MagicMock()
    mock_item.diagnosis_codes.filter.return_value.values_list.return_value = [
        "diag-1",
        "diag-2",
        "diag-3",
    ]
    mock_db_queries["claim_line_item"].filter.return_value.first.return_value = mock_item

    update = UpdateClaimLineItem(
        claim_line_item_id="something-right", linked_diagnosis_codes=["diag-1", "diag-2"]
    )
    payload = update.apply()
    assert payload.type == EffectType.UPDATE_CLAIM_LINE_ITEM
    assert (
        payload.payload
        == '{"data": {"linked_diagnosis_codes": ["diag-1", "diag-2"]}, "claim_line_item_id": "something-right"}'
    )


def test_payload_with_no_linked_diagnosis_codes(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that linked_diagnosis_codes is not included when not provided."""
    update = UpdateClaimLineItem(claim_line_item_id="something-right")
    payload = update.apply()
    assert payload.type == EffectType.UPDATE_CLAIM_LINE_ITEM
    assert payload.payload == '{"data": {}, "claim_line_item_id": "something-right"}'


def test_payload_with_empty_linked_diagnosis_codes(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that an empty linked_diagnosis_codes list is included in the data payload."""
    mock_item = MagicMock()
    mock_item.diagnosis_codes.filter.return_value.values_list.return_value = []
    mock_db_queries["claim_line_item"].filter.return_value.first.return_value = mock_item

    update = UpdateClaimLineItem(claim_line_item_id="something-right", linked_diagnosis_codes=[])
    payload = update.apply()
    assert payload.type == EffectType.UPDATE_CLAIM_LINE_ITEM
    assert (
        payload.payload
        == '{"data": {"linked_diagnosis_codes": []}, "claim_line_item_id": "something-right"}'
    )


def test_payload_with_charge_and_linked_diagnosis_codes(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that both charge and linked_diagnosis_codes are included in the data payload."""
    mock_item = MagicMock()
    mock_item.diagnosis_codes.filter.return_value.values_list.return_value = ["diag-1"]
    mock_db_queries["claim_line_item"].filter.return_value.first.return_value = mock_item

    update = UpdateClaimLineItem(
        claim_line_item_id="something-right", charge=150.75, linked_diagnosis_codes=["diag-1"]
    )
    payload = update.apply()
    assert payload.type == EffectType.UPDATE_CLAIM_LINE_ITEM
    assert (
        payload.payload
        == '{"data": {"charge": "150.75", "linked_diagnosis_codes": ["diag-1"]}, "claim_line_item_id": "something-right"}'
    )


def test_requires_valid_linked_diagnosis_codes(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that linked_diagnosis_codes must correspond to the claim line item."""
    mock_item = MagicMock()
    mock_item.diagnosis_codes.filter.return_value.values_list.return_value = ["diag-1", "diag-2"]
    mock_db_queries["claim_line_item"].filter.return_value.first.return_value = mock_item

    update = UpdateClaimLineItem(
        claim_line_item_id="something-right", linked_diagnosis_codes=["diag-1", "invalid-diag"]
    )
    with pytest.raises(ValidationError) as e:
        update.apply()

    err_msg = repr(e.value)
    assert "ClaimLineItemDiagnosis ids do not correspond to the claim line item" in err_msg
