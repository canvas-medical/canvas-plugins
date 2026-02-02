from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.claim import ClaimEffect, ColorEnum, Label


@pytest.fixture
def mock_db_queries() -> Generator[dict[str, MagicMock]]:
    """Mock all database queries to return True/exist by default."""
    with (
        patch("canvas_sdk.effects.claim.claim_comment.Claim") as mock_claim_comment,
        patch("canvas_sdk.effects.claim.claim_label.Claim") as mock_claim_label,
        patch("canvas_sdk.effects.claim.claim_queue.Claim") as mock_claim_queue,
        patch("canvas_sdk.effects.claim.claim_queue.ClaimQueue") as mock_queue,
    ):
        # Setup default behaviors - objects exist
        mock_claim_comment.objects.filter.return_value.exists.return_value = True
        mock_claim_label.objects.filter.return_value.exists.return_value = True
        mock_claim_queue.objects.filter.return_value.exists.return_value = True
        mock_queue.objects.filter.return_value.exists.return_value = True

        yield {
            "claim_comment": mock_claim_comment,
            "claim_label": mock_claim_label,
            "claim_queue": mock_claim_queue,
            "queue": mock_queue,
        }


def test_claim_effect_add_comment(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that add_comment returns the correct effect."""
    claim = ClaimEffect(claim_id="claim-id")
    effect = claim.add_comment("This is a test comment")

    assert effect.type == EffectType.ADD_CLAIM_COMMENT
    assert (
        effect.payload == '{"data": {"claim_id": "claim-id", "comment": "This is a test comment"}}'
    )


def test_claim_effect_add_comment_requires_existing_claim(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that add_comment validates the claim exists."""
    mock_db_queries["claim_comment"].objects.filter.return_value.exists.return_value = False
    claim = ClaimEffect(claim_id="invalid-claim-id")

    with pytest.raises(ValidationError) as e:
        claim.add_comment("This is a test comment")

    err_msg = repr(e.value)
    assert "Claim with id invalid-claim-id does not exist." in err_msg


def test_claim_effect_add_label_with_strings(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that add_label returns the correct effect with string labels."""
    claim = ClaimEffect(claim_id="claim-id")
    effect = claim.add_label(["urgent", "routine"])

    assert effect.type == EffectType.ADD_CLAIM_LABEL
    assert (
        effect.payload
        == '{"data": {"claim_id": "claim-id", "labels": [{"name": "urgent"}, {"name": "routine"}]}}'
    )


def test_claim_effect_add_label_with_label_objects(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that add_label returns the correct effect with Label objects."""
    claim = ClaimEffect(claim_id="claim-id")
    effect = claim.add_label([Label(color=ColorEnum.PINK, name="test")])

    assert effect.type == EffectType.ADD_CLAIM_LABEL
    assert (
        effect.payload
        == '{"data": {"claim_id": "claim-id", "labels": [{"color": "pink", "name": "test"}]}}'
    )


def test_claim_effect_add_label_with_mixed_labels(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that add_label returns the correct effect with mixed string and Label objects."""
    claim = ClaimEffect(claim_id="claim-id")
    effect = claim.add_label(["urgent", Label(color=ColorEnum.PINK, name="test")])

    assert effect.type == EffectType.ADD_CLAIM_LABEL
    assert (
        effect.payload
        == '{"data": {"claim_id": "claim-id", "labels": [{"name": "urgent"}, {"color": "pink", "name": "test"}]}}'
    )


def test_claim_effect_remove_label(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that remove_label returns the correct effect."""
    claim = ClaimEffect(claim_id="claim-id")
    effect = claim.remove_label(["urgent", "routine"])

    assert effect.type == EffectType.REMOVE_CLAIM_LABEL
    assert effect.payload == '{"data": {"claim_id": "claim-id", "labels": ["urgent", "routine"]}}'


def test_claim_effect_add_label_requires_existing_claim(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that add_label validates the claim exists."""
    mock_db_queries["claim_label"].objects.filter.return_value.exists.return_value = False
    claim = ClaimEffect(claim_id="invalid-claim-id")

    with pytest.raises(ValidationError) as e:
        claim.add_label(["urgent"])

    err_msg = repr(e.value)
    assert "Claim with id invalid-claim-id does not exist." in err_msg


def test_claim_effect_remove_label_requires_existing_claim(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that remove_label validates the claim exists."""
    mock_db_queries["claim_label"].objects.filter.return_value.exists.return_value = False
    claim = ClaimEffect(claim_id="invalid-claim-id")

    with pytest.raises(ValidationError) as e:
        claim.remove_label(["urgent"])

    err_msg = repr(e.value)
    assert "Claim with id invalid-claim-id does not exist." in err_msg


def test_claim_effect_move_to_queue(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that move_to_queue returns the correct effect."""
    claim = ClaimEffect(claim_id="claim-id")
    effect = claim.move_to_queue("NeedsClinicianReview")

    assert effect.type == EffectType.MOVE_CLAIM_TO_QUEUE
    assert effect.payload == '{"data": {"claim_id": "claim-id", "queue": "NeedsClinicianReview"}}'


def test_claim_effect_move_to_queue_requires_existing_claim(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that move_to_queue validates the claim exists."""
    mock_db_queries["claim_queue"].objects.filter.return_value.exists.return_value = False
    claim = ClaimEffect(claim_id="invalid-claim-id")

    with pytest.raises(ValidationError) as e:
        claim.move_to_queue("NeedsClinicianReview")

    err_msg = repr(e.value)
    assert "Claim does not exist" in err_msg


def test_claim_effect_move_to_queue_requires_existing_queue(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that move_to_queue validates the queue exists."""
    mock_db_queries["queue"].objects.filter.return_value.exists.return_value = False
    claim = ClaimEffect(claim_id="claim-id")

    with pytest.raises(ValidationError) as e:
        claim.move_to_queue("InvalidQueue")

    err_msg = repr(e.value)
    assert "Queue does not exist" in err_msg
