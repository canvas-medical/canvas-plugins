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
    ):
        # Setup default behaviors - objects exist
        mock_claim.filter.return_value.exists.return_value = True

        yield {"claim": mock_claim}


def test_add_claim_label_requires_existing_claim_id(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that the claim_id is valid and the claim exists."""
    mock_db_queries["claim"].filter.return_value.exists.return_value = False
    add = AddClaimLabel(claim_id="something-wrong", labels=["urgent", "routine"])
    with pytest.raises(ValidationError) as e:
        add.apply()

    err_msg = repr(e.value)
    assert "Claim with id something-wrong does not exist" in err_msg


def test_add_claim_label_with_labels(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test the correct payload with valid claim_id and labels."""
    add = AddClaimLabel(claim_id="claim-id", labels=["urgent", "routine"])
    payload = add.apply()
    assert payload.type == EffectType.ADD_CLAIM_LABEL
    assert (
        payload.payload
        == '{"data": {"claim_id": "claim-id", "labels": [{"name": "urgent"}, {"name": "routine"}]}}'
    )


def test_add_claim_label_with_label_values(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test the correct payload with valid claim_id and label_values."""
    add = AddClaimLabel(
        claim_id="claim-id", labels=[Label(color=ColorEnum.PINK, name="test", position=100)]
    )
    payload = add.apply()
    assert payload.type == EffectType.ADD_CLAIM_LABEL
    assert (
        payload.payload
        == '{"data": {"claim_id": "claim-id", "labels": [{"color": "pink", "name": "test", "position": 100}]}}'
    )


def test_add_claim_label_with_label_name_and_label_values(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test the correct payload with valid claim_id and label names and label_values."""
    add = AddClaimLabel(
        claim_id="claim-id",
        labels=["urgent", Label(color=ColorEnum.PINK, name="test", position=100)],
    )
    payload = add.apply()
    assert payload.type == EffectType.ADD_CLAIM_LABEL
    assert (
        payload.payload
        == '{"data": {"claim_id": "claim-id", "labels": [{"name": "urgent"}, {"color": "pink", "name": "test", "position": 100}]}}'
    )


def test_remove_claim_label_requires_existing_claim_id(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that the claim_id is valid and the claim exists."""
    mock_db_queries["claim"].filter.return_value.exists.return_value = False
    remove = RemoveClaimLabel(claim_id="something-wrong", labels=["urgent", "routine"])
    with pytest.raises(ValidationError) as e:
        remove.apply()

    err_msg = repr(e.value)
    assert "Claim with id something-wrong does not exist" in err_msg


def test_remove_claim_label(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test the correct payload with valid claim_id and label_id."""
    remove = RemoveClaimLabel(claim_id="claim-id", labels=["urgent", "routine"])
    payload = remove.apply()
    assert payload.type == EffectType.REMOVE_CLAIM_LABEL
    assert (
        payload.payload
        == '{"data": {"claim_id": "claim-id", "label_names": ["urgent", "routine"]}}'
    )
