import json
from collections.abc import Generator
from decimal import Decimal
from typing import Any
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from django.db.models import QuerySet
from pydantic import ValidationError

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.claim import (
    BannerAlertIntent,
    ClaimEffect,
    ColorEnum,
    Label,
    LineItemTransaction,
    PaymentMethod,
)


@pytest.fixture
def mock_db_queries() -> Generator[dict[str, MagicMock]]:
    """Mock all database queries to return True/exist by default."""
    with (
        patch("canvas_sdk.effects.claim.claim_banner_alert.Claim") as mock_banner_claim,
        patch("canvas_sdk.effects.claim.claim_comment.Claim") as mock_claim_comment,
        patch("canvas_sdk.effects.claim.claim_label.Claim") as mock_claim_label,
        patch("canvas_sdk.effects.claim.claim_queue.Claim") as mock_claim_queue,
        patch("canvas_sdk.effects.claim.claim_queue.ClaimQueue") as mock_queue,
        patch("canvas_sdk.effects.claim.payment.base.Claim.objects") as mock_payment_claim,
        patch("canvas_sdk.effects.claim.payment.base.ClaimLineItem.objects") as mock_cli,
        patch("canvas_sdk.effects.claim.payment.base.ClaimQueue.objects") as mock_payment_queue,
    ):
        # Setup default behaviors - objects exist
        mock_banner_claim.objects.filter.return_value.exists.return_value = True
        mock_claim_comment.objects.filter.return_value.exists.return_value = True
        mock_claim_label.objects.filter.return_value.exists.return_value = True
        mock_claim_queue.objects.filter.return_value.exists.return_value = True
        mock_queue.objects.filter.return_value.exists.return_value = True

        # Setup payment-related mocks
        mock_claim_obj = MagicMock()
        mock_claim_obj.id = "claim-id"

        claims_qs = MagicMock()
        claims_qs.count.return_value = 1
        claims_qs.values_list.return_value = [mock_claim_obj.id]
        claims_qs.get.return_value = mock_claim_obj
        claims_qs.first.return_value = mock_claim_obj

        mock_payment_claim.filter.return_value = claims_qs
        mock_payment_claim.filter.return_value.first.return_value = mock_claim_obj

        mock_payment_queue.filter.return_value.exists.return_value = True

        # Make claim.line_items.active().filter(id=...) return a ClaimLineItem-like mock
        def filter_side_effect(**kwargs: Any) -> QuerySet:
            qs = MagicMock()
            qs.first.return_value = MagicMock(id=kwargs.get("id"), proc_code="PROC")
            return qs

        mock_claim_obj.line_items.active.return_value.filter.side_effect = filter_side_effect

        # Ensure the coverage exists for transfer targets / provided coverage id
        mock_claim_obj.coverages.active.return_value.filter.return_value.exists.return_value = True
        mock_claim_obj.coverages.active.return_value.filter.return_value = [1]

        yield {
            "banner_claim": mock_banner_claim,
            "claim_comment": mock_claim_comment,
            "claim_label": mock_claim_label,
            "claim_queue": mock_claim_queue,
            "queue": mock_queue,
            "payment_claim": mock_payment_claim,
            "payment_claim_obj": mock_claim_obj,
            "payment_cli": mock_cli,
            "payment_queue": mock_payment_queue,
        }


class TestClaimEffect:
    """Tests for ClaimEffect class."""

    def test_claim_effect_creation_with_uuid(self) -> None:
        """Test creating a ClaimEffect with a UUID."""
        claim_id = uuid4()
        effect = ClaimEffect(claim_id=claim_id)
        assert effect.claim_id == claim_id

    def test_claim_effect_creation_with_string(self) -> None:
        """Test creating a ClaimEffect with a string ID."""
        claim_id = "test-claim-id"
        effect = ClaimEffect(claim_id=claim_id)
        assert effect.claim_id == claim_id


class TestAddBanner:
    """Tests for ClaimEffect.add_banner method."""

    def test_add_banner_with_all_fields(self, mock_db_queries: dict[str, MagicMock]) -> None:
        """Test add_banner with all fields including optional href."""
        claim_id = "test-claim-id"
        effect = ClaimEffect(claim_id=claim_id)

        result = effect.add_banner(
            key="test-key",
            narrative="Test banner message",
            intent=BannerAlertIntent.INFO,
            href="https://example.com",
        )

        assert isinstance(result, Effect)
        assert result.type == EffectType.ADD_CLAIM_BANNER_ALERT
        assert '"claim_id": "test-claim-id"' in result.payload
        assert '"key": "test-key"' in result.payload
        assert '"narrative": "Test banner message"' in result.payload
        assert '"intent": "info"' in result.payload
        assert '"href": "https://example.com"' in result.payload

    def test_add_banner_without_href(self, mock_db_queries: dict[str, MagicMock]) -> None:
        """Test add_banner without the optional href."""
        claim_id = "test-claim-id"
        effect = ClaimEffect(claim_id=claim_id)

        result = effect.add_banner(
            key="test-key",
            narrative="Test banner message",
            intent=BannerAlertIntent.WARNING,
        )

        assert isinstance(result, Effect)
        assert result.type == EffectType.ADD_CLAIM_BANNER_ALERT
        assert '"href": null' in result.payload

    def test_add_banner_with_info_intent(self, mock_db_queries: dict[str, MagicMock]) -> None:
        """Test add_banner with INFO intent."""
        effect = ClaimEffect(claim_id="claim-id")
        result = effect.add_banner(key="key", narrative="message", intent=BannerAlertIntent.INFO)
        assert '"intent": "info"' in result.payload

    def test_add_banner_with_warning_intent(self, mock_db_queries: dict[str, MagicMock]) -> None:
        """Test add_banner with WARNING intent."""
        effect = ClaimEffect(claim_id="claim-id")
        result = effect.add_banner(key="key", narrative="message", intent=BannerAlertIntent.WARNING)
        assert '"intent": "warning"' in result.payload

    def test_add_banner_with_alert_intent(self, mock_db_queries: dict[str, MagicMock]) -> None:
        """Test add_banner with ALERT intent."""
        effect = ClaimEffect(claim_id="claim-id")
        result = effect.add_banner(key="key", narrative="message", intent=BannerAlertIntent.ALERT)
        assert '"intent": "alert"' in result.payload

    def test_add_banner_with_uuid_claim_id(self, mock_db_queries: dict[str, MagicMock]) -> None:
        """Test add_banner converts UUID to string in payload."""
        claim_id = uuid4()
        effect = ClaimEffect(claim_id=claim_id)

        result = effect.add_banner(
            key="test-key",
            narrative="Test message",
            intent=BannerAlertIntent.INFO,
        )

        assert f'"claim_id": "{claim_id}"' in result.payload

    def test_add_banner_requires_existing_claim(
        self, mock_db_queries: dict[str, MagicMock]
    ) -> None:
        """Test that add_banner validates claim exists."""
        mock_db_queries["banner_claim"].objects.filter.return_value.exists.return_value = False
        effect = ClaimEffect(claim_id="nonexistent-claim")

        with pytest.raises(ValidationError) as exc_info:
            effect.add_banner(
                key="test-key",
                narrative="Test message",
                intent=BannerAlertIntent.INFO,
            )

        err_msg = repr(exc_info.value)
        assert "Claim with id nonexistent-claim does not exist" in err_msg

    def test_add_banner_narrative_max_length(self, mock_db_queries: dict[str, MagicMock]) -> None:
        """Test that narrative has a maximum length of 90 characters."""
        effect = ClaimEffect(claim_id="claim-id")
        long_narrative = "x" * 91

        with pytest.raises(ValidationError) as exc_info:
            effect.add_banner(
                key="test-key",
                narrative=long_narrative,
                intent=BannerAlertIntent.INFO,
            )

        err_msg = repr(exc_info.value)
        assert "String should have at most 90 characters" in err_msg

    def test_add_banner_narrative_at_max_length(
        self, mock_db_queries: dict[str, MagicMock]
    ) -> None:
        """Test that narrative at exactly 90 characters is valid."""
        effect = ClaimEffect(claim_id="claim-id")
        max_narrative = "x" * 90

        result = effect.add_banner(
            key="test-key",
            narrative=max_narrative,
            intent=BannerAlertIntent.INFO,
        )

        assert isinstance(result, Effect)
        assert max_narrative in result.payload


class TestRemoveBanner:
    """Tests for ClaimEffect.remove_banner method."""

    def test_remove_banner(self, mock_db_queries: dict[str, MagicMock]) -> None:
        """Test remove_banner returns correct effect."""
        claim_id = "test-claim-id"
        effect = ClaimEffect(claim_id=claim_id)

        result = effect.remove_banner(key="test-key")

        assert isinstance(result, Effect)
        assert result.type == EffectType.REMOVE_CLAIM_BANNER_ALERT
        assert '"claim_id": "test-claim-id"' in result.payload
        assert '"key": "test-key"' in result.payload

    def test_remove_banner_with_uuid_claim_id(self, mock_db_queries: dict[str, MagicMock]) -> None:
        """Test remove_banner converts UUID to string in payload."""
        claim_id = uuid4()
        effect = ClaimEffect(claim_id=claim_id)

        result = effect.remove_banner(key="test-key")

        assert f'"claim_id": "{claim_id}"' in result.payload

    def test_remove_banner_does_not_validate_claim_exists(
        self, mock_db_queries: dict[str, MagicMock]
    ) -> None:
        """Test that remove_banner does not check if claim exists."""
        mock_db_queries["banner_claim"].filter.return_value.exists.return_value = False
        effect = ClaimEffect(claim_id="nonexistent-claim")

        # Should not raise - remove_banner doesn't validate claim existence
        result = effect.remove_banner(key="test-key")

        assert isinstance(result, Effect)
        assert result.type == EffectType.REMOVE_CLAIM_BANNER_ALERT


class TestBannerAlertIntent:
    """Tests for BannerAlertIntent enum."""

    def test_banner_alert_intent_values(self) -> None:
        """Test that BannerAlertIntent has correct values."""
        assert BannerAlertIntent.INFO.value == "info"
        assert BannerAlertIntent.WARNING.value == "warning"
        assert BannerAlertIntent.ALERT.value == "alert"

    def test_banner_alert_intent_members(self) -> None:
        """Test that BannerAlertIntent has exactly three members."""
        members = list(BannerAlertIntent)
        assert len(members) == 3
        assert BannerAlertIntent.INFO in members
        assert BannerAlertIntent.WARNING in members
        assert BannerAlertIntent.ALERT in members


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


def test_claim_effect_add_labels_with_strings(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that add_labels returns the correct effect with string labels."""
    claim = ClaimEffect(claim_id="claim-id")
    effect = claim.add_labels(["urgent", "routine"])

    assert effect.type == EffectType.ADD_CLAIM_LABEL
    assert (
        effect.payload
        == '{"data": {"claim_id": "claim-id", "labels": [{"name": "urgent"}, {"name": "routine"}]}}'
    )


def test_claim_effect_add_labels_with_label_objects(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that add_labels returns the correct effect with Label objects."""
    claim = ClaimEffect(claim_id="claim-id")
    effect = claim.add_labels([Label(color=ColorEnum.PINK, name="test")])

    assert effect.type == EffectType.ADD_CLAIM_LABEL
    assert (
        effect.payload
        == '{"data": {"claim_id": "claim-id", "labels": [{"color": "pink", "name": "test"}]}}'
    )


def test_claim_effect_add_labels_with_mixed_labels(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that add_labels returns the correct effect with mixed string and Label objects."""
    claim = ClaimEffect(claim_id="claim-id")
    effect = claim.add_labels(["urgent", Label(color=ColorEnum.PINK, name="test")])

    assert effect.type == EffectType.ADD_CLAIM_LABEL
    assert (
        effect.payload
        == '{"data": {"claim_id": "claim-id", "labels": [{"name": "urgent"}, {"color": "pink", "name": "test"}]}}'
    )


def test_claim_effect_remove_labels(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that remove_labels returns the correct effect."""
    claim = ClaimEffect(claim_id="claim-id")
    effect = claim.remove_labels(["urgent", "routine"])

    assert effect.type == EffectType.REMOVE_CLAIM_LABEL
    assert effect.payload == '{"data": {"claim_id": "claim-id", "labels": ["urgent", "routine"]}}'


def test_claim_effect_add_labels_requires_existing_claim(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that add_labels validates the claim exists."""
    mock_db_queries["claim_label"].objects.filter.return_value.exists.return_value = False
    claim = ClaimEffect(claim_id="invalid-claim-id")

    with pytest.raises(ValidationError) as e:
        claim.add_labels(["urgent"])

    err_msg = repr(e.value)
    assert "Claim with id invalid-claim-id does not exist." in err_msg


def test_claim_effect_remove_labels_requires_existing_claim(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that remove_labels validates the claim exists."""
    mock_db_queries["claim_label"].objects.filter.return_value.exists.return_value = False
    claim = ClaimEffect(claim_id="invalid-claim-id")

    with pytest.raises(ValidationError) as e:
        claim.remove_labels(["urgent"])

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


def test_claim_effect_post_payment_patient_payment(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that post_payment returns the correct effect for a patient payment."""
    claim = ClaimEffect(claim_id="claim-id")
    line_items = [
        LineItemTransaction(claim_line_item_id="line-1", payment=Decimal("5.00")),
        LineItemTransaction(claim_line_item_id="line-2", payment=Decimal("3.50")),
    ]

    effect = claim.post_payment(
        claim_coverage_id="patient",
        line_item_transactions=line_items,
        method=PaymentMethod.CASH,
    )

    assert effect.type == EffectType.POST_CLAIM_PAYMENT
    payload = json.loads(effect.payload)["data"]
    assert payload["payment_collection"]["method"] == "cash"
    assert payload["payment_collection"]["total_collected"] == "8.50"
    assert payload["claims_allocation"][0]["claim_id"] == "claim-id"
    assert payload["claims_allocation"][0]["claim_coverage_id"] == "patient"
    assert len(payload["claims_allocation"][0]["line_item_transactions"]) == 2


def test_claim_effect_post_payment_coverage_payment(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that post_payment returns the correct effect for a coverage payment."""
    claim = ClaimEffect(claim_id="claim-id")
    line_items = [
        LineItemTransaction(
            claim_line_item_id="line-1",
            payment=Decimal("10.00"),
            adjustment=Decimal("2.00"),
            adjustment_code="CO-45",
            transfer_remaining_balance_to="patient",
        ),
    ]

    effect = claim.post_payment(
        claim_coverage_id="coverage-id",
        line_item_transactions=line_items,
        method=PaymentMethod.CASH,
    )

    assert effect.type == EffectType.POST_CLAIM_PAYMENT
    payload = json.loads(effect.payload)["data"]
    assert payload["claims_allocation"][0]["claim_coverage_id"] == "coverage-id"
    line_item = payload["claims_allocation"][0]["line_item_transactions"][0]
    assert line_item["payment"] == "10.00"
    assert line_item["adjustment"] == "2.00"
    assert line_item["adjustment_code"] == "CO-45"
    assert line_item["transfer_to"] == "patient"


def test_claim_effect_post_payment_with_check_method(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that post_payment with CHECK method includes check details."""
    from datetime import date

    claim = ClaimEffect(claim_id="claim-id")
    line_items = [
        LineItemTransaction(claim_line_item_id="line-1", payment=Decimal("25.00")),
    ]

    effect = claim.post_payment(
        claim_coverage_id="patient",
        line_item_transactions=line_items,
        method=PaymentMethod.CHECK,
        check_date=date(2024, 1, 15),
        check_number="12345",
    )

    assert effect.type == EffectType.POST_CLAIM_PAYMENT
    payload = json.loads(effect.payload)["data"]
    assert payload["payment_collection"]["method"] == "check"
    assert payload["payment_collection"]["check_number"] == "12345"
    assert payload["payment_collection"]["check_date"] == "2024-01-15"


def test_claim_effect_post_payment_with_optional_fields(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that post_payment includes optional fields when provided."""
    from datetime import date

    claim = ClaimEffect(claim_id="claim-id")
    line_items = [
        LineItemTransaction(claim_line_item_id="line-1", payment=Decimal("15.00")),
    ]

    effect = claim.post_payment(
        claim_coverage_id="patient",
        line_item_transactions=line_items,
        method=PaymentMethod.CARD,
        move_to_queue_name="ReadyToBill",
        claim_description="Payment for visit",
        deposit_date=date(2024, 1, 20),
        payment_description="Credit card payment",
    )

    assert effect.type == EffectType.POST_CLAIM_PAYMENT
    payload = json.loads(effect.payload)["data"]
    assert payload["payment_collection"]["deposit_date"] == "2024-01-20"
    assert payload["payment_collection"]["payment_description"] == "Credit card payment"
    assert payload["claims_allocation"][0]["move_to_queue_name"] == "ReadyToBill"
    assert payload["claims_allocation"][0]["description"] == "Payment for visit"


def test_claim_effect_post_payment_requires_existing_claim(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that post_payment validates the claim exists."""
    mock_db_queries["payment_claim"].filter.return_value.first.return_value = None

    claim = ClaimEffect(claim_id="non-existent-claim")
    line_items = [
        LineItemTransaction(claim_line_item_id="line-1", payment=Decimal("5.00")),
    ]

    with pytest.raises(ValidationError) as e:
        claim.post_payment(
            claim_coverage_id="patient",
            line_item_transactions=line_items,
            method=PaymentMethod.CASH,
        )

    err_msg = repr(e.value)
    assert "The provided claim_id does not correspond with an existing Claim" in err_msg


def test_claim_effect_post_payment_requires_active_coverage(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that post_payment validates the coverage is active for the claim."""
    mock_db_queries["payment_claim_obj"].coverages.active.return_value.filter.return_value = []

    claim = ClaimEffect(claim_id="claim-id")
    line_items = [
        LineItemTransaction(claim_line_item_id="line-1", payment=Decimal("5.00")),
    ]

    with pytest.raises(ValidationError) as e:
        claim.post_payment(
            claim_coverage_id="invalid-coverage",
            line_item_transactions=line_items,
            method=PaymentMethod.CASH,
        )

    err_msg = repr(e.value)
    assert "does not correspond to an active coverage" in err_msg


def test_claim_effect_post_payment_requires_existing_queue(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that post_payment validates the queue exists when move_to_queue_name is provided."""
    mock_db_queries["payment_queue"].filter.return_value.exists.return_value = False

    claim = ClaimEffect(claim_id="claim-id")
    line_items = [
        LineItemTransaction(claim_line_item_id="line-1", payment=Decimal("5.00")),
    ]

    with pytest.raises(ValidationError) as e:
        claim.post_payment(
            claim_coverage_id="patient",
            line_item_transactions=line_items,
            method=PaymentMethod.CASH,
            move_to_queue_name="NonExistentQueue",
        )

    err_msg = repr(e.value)
    assert "does not correspond to an existing ClaimQueue" in err_msg


def test_claim_effect_post_payment_check_method_requires_check_fields(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that post_payment with CHECK method requires check_number and check_date."""
    claim = ClaimEffect(claim_id="claim-id")
    line_items = [
        LineItemTransaction(claim_line_item_id="line-1", payment=Decimal("5.00")),
    ]

    with pytest.raises(ValidationError) as e:
        claim.post_payment(
            claim_coverage_id="patient",
            line_item_transactions=line_items,
            method=PaymentMethod.CHECK,
        )

    err_msg = repr(e.value)
    assert "Check number is required for payment method CHECK" in err_msg
    assert "Check date is required for payment method CHECK" in err_msg


def test_claim_effect_post_payment_requires_existing_line_item(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that post_payment validates the claim line item exists."""

    # Make line item lookup return None
    def filter_side_effect(**_kwargs: Any) -> MagicMock:
        qs = MagicMock()
        qs.first.return_value = None
        return qs

    mock_db_queries[
        "payment_claim_obj"
    ].line_items.active.return_value.filter.side_effect = filter_side_effect

    claim = ClaimEffect(claim_id="claim-id")
    line_items = [
        LineItemTransaction(claim_line_item_id="missing-line", payment=Decimal("5.00")),
    ]

    with pytest.raises(ValidationError) as e:
        claim.post_payment(
            claim_coverage_id="patient",
            line_item_transactions=line_items,
            method=PaymentMethod.CASH,
        )

    err_msg = repr(e.value)
    assert "does not correspond to an existing ClaimLineItem" in err_msg


def test_claim_effect_post_payment_patient_not_allowed_to_post_allowed(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that patient payments cannot have allowed amounts."""
    claim = ClaimEffect(claim_id="claim-id")
    line_items = [
        LineItemTransaction(
            claim_line_item_id="line-1",
            payment=Decimal("5.00"),
            allowed=Decimal("10.00"),
        ),
    ]

    with pytest.raises(ValidationError) as e:
        claim.post_payment(
            claim_coverage_id="patient",
            line_item_transactions=line_items,
            method=PaymentMethod.CASH,
        )

    err_msg = repr(e.value)
    assert "Allowed amount should be $0 or None for patient postings" in err_msg


def test_claim_effect_post_payment_requires_adjustment_code(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that adjustments require an adjustment code."""
    claim = ClaimEffect(claim_id="claim-id")
    line_items = [
        LineItemTransaction(
            claim_line_item_id="line-1",
            adjustment=Decimal("5.00"),
        ),
    ]

    with pytest.raises(ValidationError) as e:
        claim.post_payment(
            claim_coverage_id="coverage-id",
            line_item_transactions=line_items,
            method=PaymentMethod.CASH,
        )

    err_msg = repr(e.value)
    assert "Specify an adjustment code for the adjustment amount" in err_msg


def test_line_item_transaction_is_first_transaction_not_in_list() -> None:
    """Test that is_first_transaction_for_line_item returns False when transaction is not in the list."""
    # Create a transaction with a claim_line_item_id that won't be in the list
    transaction = LineItemTransaction(
        claim_line_item_id="line-not-in-list",
        payment=Decimal("5.00"),
    )

    # Create a list of transactions that doesn't contain any matching claim_line_item_id
    other_transactions = [
        LineItemTransaction(claim_line_item_id="line-1", payment=Decimal("10.00")),
        LineItemTransaction(claim_line_item_id="line-2", payment=Decimal("15.00")),
    ]

    # The transaction's claim_line_item_id is not in other_transactions, so should return False
    result = transaction.is_first_transaction_for_line_item(other_transactions, index=0)

    assert result is False
