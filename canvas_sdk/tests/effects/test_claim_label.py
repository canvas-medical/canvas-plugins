from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.claim_label import AddClaimLabel, ColorEnum, Label, RemoveClaimLabel


@pytest.fixture
def mock_db_queries() -> Generator[dict[str, MagicMock]]:
    """Mock all database queries to return True/exist by default."""
    with (
        patch("canvas_sdk.effects.claim_label.Claim.objects") as mock_claim,
        patch("canvas_sdk.effects.claim_label.TaskLabel.objects") as mock_label,
    ):
        # Setup default behaviors - objects exist
        mock_claim.filter.return_value.exists.return_value = True
        mock_label.filter.return_value.exists.return_value = True

        yield {
            "claim": mock_claim,
            "label": mock_label,
        }


def test_add_claim_label_requires_claim_id() -> None:
    """Test that claim_id is required."""
    with pytest.raises(ValidationError) as e:
        AddClaimLabel()  # type: ignore
    err_msg = repr(e.value)
    assert "1 validation error for AddClaimLabel\nclaim_id\n  Field required" in err_msg


def test_add_claim_label_requires_label_id_or_label_values(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that label_id or label_values is required."""
    add = AddClaimLabel(claim_id="claim-id")
    with pytest.raises(ValidationError) as e:
        add.apply()
    err_msg = repr(e.value)
    assert (
        "1 validation error for AddClaimLabel\n  One of the fields 'label_id' or 'label_values' are required in order to add a claim label. [type=missing,"
        in err_msg
    )


def test_add_claim_label_requires_existing_label_id(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that the label_id is valid and the label exists."""
    mock_db_queries["label"].filter.return_value.exists.return_value = False
    add = AddClaimLabel(claim_id="something-right", label_id="something-wrong")
    with pytest.raises(ValidationError) as e:
        add.apply()

    err_msg = repr(e.value)
    assert "Label with id something-wrong does not exist" in err_msg


def test_add_claim_label_requires_existing_claim_id(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that the claim_id is valid and the claim exists."""
    mock_db_queries["claim"].filter.return_value.exists.return_value = False
    add = AddClaimLabel(claim_id="something-wrong", label_id="something-right")
    with pytest.raises(ValidationError) as e:
        add.apply()

    err_msg = repr(e.value)
    assert "Claim with id something-wrong does not exist" in err_msg


def test_add_claim_label_with_label_id(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test the correct payload with valid claim_id and label_id."""
    add = AddClaimLabel(claim_id="claim-id", label_id="label-id")
    payload = add.apply()
    assert payload.type == EffectType.ADD_CLAIM_LABEL
    assert (
        payload.payload
        == '{"data": {"claim_id": "claim-id", "label_id": "label-id", "label_values": null}}'
    )


def test_add_claim_label_with_label_values(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test the correct payload with valid claim_id and label_values."""
    add = AddClaimLabel(
        claim_id="claim-id", label_values=Label(color=ColorEnum.PINK, name="test", position=100)
    )
    payload = add.apply()
    assert payload.type == EffectType.ADD_CLAIM_LABEL
    assert (
        payload.payload
        == '{"data": {"claim_id": "claim-id", "label_id": null, "label_values": {"color": "pink", "name": "test", "position": 100}}}'
    )


def test_remove_claim_label_requires_claim_id_and_label_id() -> None:
    """Test that claim_id is required."""
    with pytest.raises(ValidationError) as e:
        RemoveClaimLabel()  # type: ignore
    err_msg = repr(e.value)
    assert (
        "2 validation errors for RemoveClaimLabel\nclaim_id\n  Field required [type=missing,"
        in err_msg
    )
    assert "label_id\n  Field required [type=missing," in err_msg


def test_remove_claim_label_requires_existing_label_id(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that the label_id is valid and the label exists."""
    mock_db_queries["label"].filter.return_value.exists.return_value = False
    remove = RemoveClaimLabel(claim_id="something-right", label_id="something-wrong")
    with pytest.raises(ValidationError) as e:
        remove.apply()

    err_msg = repr(e.value)
    assert "Label with id something-wrong does not exist" in err_msg


def test_remove_claim_label_requires_existing_claim_id(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that the claim_id is valid and the claim exists."""
    mock_db_queries["claim"].filter.return_value.exists.return_value = False
    remove = RemoveClaimLabel(claim_id="something-wrong", label_id="something-right")
    with pytest.raises(ValidationError) as e:
        remove.apply()

    err_msg = repr(e.value)
    assert "Claim with id something-wrong does not exist" in err_msg


def test_remove_claim_label(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test the correct payload with valid claim_id and label_id."""
    remove = RemoveClaimLabel(claim_id="claim-id", label_id="label-id")
    payload = remove.apply()
    assert payload.type == EffectType.REMOVE_CLAIM_LABEL
    assert payload.payload == '{"data": {"claim_id": "claim-id", "label_id": "label-id"}}'
