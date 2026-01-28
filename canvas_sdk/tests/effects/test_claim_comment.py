from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.claim_comment import AddClaimComment


@pytest.fixture
def mock_db_queries() -> Generator[dict[str, MagicMock]]:
    """Mock all database queries to return True/exist by default."""
    with (
        patch("canvas_sdk.effects.claim_comment.Claim.objects") as mock_claim,
    ):
        # Setup default behaviors - objects exist
        mock_claim.filter.return_value.exists.return_value = True

        yield {"claim": mock_claim}


def test_add_claim_comment_requires_existing_claim_id(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that the claim_id is valid and the claim exists."""
    mock_db_queries["claim"].filter.return_value.exists.return_value = False
    add = AddClaimComment(claim_id="something-wrong", comment="Test comment")
    with pytest.raises(ValidationError) as e:
        add.apply()

    err_msg = repr(e.value)
    assert "Claim with id something-wrong does not exist" in err_msg


def test_add_claim_comment_with_valid_claim_id(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test the correct payload with valid claim_id and comment."""
    add = AddClaimComment(claim_id="claim-id", comment="This is a test comment")
    payload = add.apply()
    assert payload.type == EffectType.ADD_CLAIM_COMMENT
    assert (
        payload.payload == '{"data": {"claim_id": "claim-id", "comment": "This is a test comment"}}'
    )
