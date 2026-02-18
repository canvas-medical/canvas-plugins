from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.claim_queue import MoveClaimToQueue


@pytest.fixture
def mock_db_queries() -> Generator[dict[str, MagicMock]]:
    """Mock all database queries to return True/exist by default."""
    with (
        patch("canvas_sdk.effects.claim.claim_queue.Claim.objects") as mock_claim,
        patch("canvas_sdk.effects.claim.claim_queue.ClaimQueue.objects") as mock_queue,
    ):
        # Setup default behaviors - objects exist
        mock_claim.filter.return_value.exists.return_value = True
        mock_queue.filter.return_value.exists.return_value = True

        yield {"claim": mock_claim, "queue": mock_queue}


def test_move_claim_requires_existing_claim_id(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that the claim_id is valid and the claim exists."""
    mock_db_queries["claim"].filter.return_value.exists.return_value = False
    move = MoveClaimToQueue(claim_id="something-wrong", queue="NeedsClinicianReview")
    with pytest.raises(ValidationError) as e:
        move.apply()

    err_msg = repr(e.value)
    assert "Claim does not exist" in err_msg


def test_move_claim_requires_existing_queue(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that the queue exists."""
    mock_db_queries["queue"].filter.return_value.exists.return_value = False
    move = MoveClaimToQueue(claim_id="something-right", queue="SomethingWrong")
    with pytest.raises(ValidationError) as e:
        move.apply()

    err_msg = repr(e.value)
    assert "Queue does not exist" in err_msg


def test_move_claim_payload(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test the correct payload with valid claim_id and queue."""
    move = MoveClaimToQueue(claim_id="claim-id", queue="NeedsClinicianReview")
    payload = move.apply()
    assert payload.type == EffectType.MOVE_CLAIM_TO_QUEUE
    assert payload.payload == '{"data": {"claim_id": "claim-id", "queue": "NeedsClinicianReview"}}'
