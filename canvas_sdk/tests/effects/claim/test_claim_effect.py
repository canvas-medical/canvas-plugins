import json
from collections.abc import Generator
from datetime import date
from decimal import Decimal
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from django.db.models import QuerySet
from pydantic import ValidationError

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.claim import (
    BannerAlertIntent,
    ClaimEffect,
    ColorEnum,
    Label,
    LineItemTransaction,
    PaymentMethod,
)
from canvas_sdk.effects.claim.claim_provider import (
    ClaimBillingProvider,
    ClaimFacility,
    ClaimOrderingProvider,
    ClaimProvider,
    ClaimReferringProvider,
)


@pytest.fixture
def mock_db_queries() -> Generator[dict[str, MagicMock]]:
    """Mock all database queries to return True/exist by default."""
    with (
        patch("canvas_sdk.effects.claim.claim_banner_alert.Claim") as mock_claim_banner,
        patch("canvas_sdk.effects.claim.claim_comment.Claim") as mock_claim_comment,
        patch("canvas_sdk.effects.claim.claim_label.Claim") as mock_claim_label,
        patch("canvas_sdk.effects.claim.claim_metadata.Claim") as mock_claim_metadata,
        patch("canvas_sdk.effects.claim.claim_queue.Claim") as mock_claim_queue,
        patch("canvas_sdk.effects.claim.claim_queue.ClaimQueue") as mock_queue,
        patch("canvas_sdk.effects.claim.claim_provider.Claim") as mock_claim_provider,
        patch("canvas_sdk.effects.claim.payment.base.Claim.objects") as mock_payment_claim,
        patch("canvas_sdk.effects.claim.payment.base.ClaimLineItem.objects") as mock_cli,
        patch("canvas_sdk.effects.claim.payment.base.ClaimQueue.objects") as mock_payment_queue,
    ):
        # Setup default behaviors - objects exist
        mock_claim_banner.objects.filter.return_value.exists.return_value = True
        mock_claim_comment.objects.filter.return_value.exists.return_value = True
        mock_claim_label.objects.filter.return_value.exists.return_value = True
        mock_claim_metadata.objects.filter.return_value.exists.return_value = True
        mock_claim_queue.objects.filter.return_value.exists.return_value = True
        mock_queue.objects.filter.return_value.exists.return_value = True

        # Setup claim_provider mock - .first() returns a claim with a provider
        mock_provider_claim_obj = MagicMock()
        mock_provider_claim_obj.provider = MagicMock()
        mock_claim_provider.objects.filter.return_value.first.return_value = mock_provider_claim_obj

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
            "claim_banner": mock_claim_banner,
            "claim_comment": mock_claim_comment,
            "claim_label": mock_claim_label,
            "claim_metadata": mock_claim_metadata,
            "claim_queue": mock_claim_queue,
            "queue": mock_queue,
            "claim_provider": mock_claim_provider,
            "claim_provider_obj": mock_provider_claim_obj,
            "payment_claim": mock_payment_claim,
            "payment_claim_obj": mock_claim_obj,
            "payment_cli": mock_cli,
            "payment_queue": mock_payment_queue,
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


def test_claim_effect_upsert_metadata(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that upsert_metadata returns the correct effect."""
    claim = ClaimEffect(claim_id="claim-id")
    effect = claim.upsert_metadata(key="billing_code", value="99213")

    assert effect.type == EffectType.UPSERT_CLAIM_METADATA
    payload = json.loads(effect.payload)["data"]
    assert payload["claim_id"] == "claim-id"
    assert payload["key"] == "billing_code"
    assert payload["value"] == "99213"


def test_claim_effect_upsert_metadata_requires_existing_claim(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that upsert_metadata validates the claim exists."""
    mock_db_queries["claim_metadata"].objects.filter.return_value.exists.return_value = False
    claim = ClaimEffect(claim_id="invalid-claim-id")

    with pytest.raises(ValidationError) as e:
        claim.upsert_metadata(key="billing_code", value="99213")

    err_msg = repr(e.value)
    assert "Claim with id: invalid-claim-id does not exist." in err_msg


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


def test_add_banner_with_all_fields(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test add_banner with all fields including optional href."""
    claim_id = "test-claim-id"
    effect = ClaimEffect(claim_id=claim_id)

    result = effect.add_banner(
        key="test-key",
        narrative="Test banner message",
        intent=BannerAlertIntent.INFO,
        href="https://example.com",
    )

    assert result.type == EffectType.ADD_CLAIM_BANNER_ALERT
    payload = json.loads(result.payload)["data"]
    assert payload["claim_id"] == "test-claim-id"
    assert payload["key"] == "test-key"
    assert payload["narrative"] == "Test banner message"
    assert payload["intent"] == "info"
    assert payload["href"] == "https://example.com"


def test_add_banner_without_href(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test add_banner without the optional href."""
    claim_id = "test-claim-id"
    effect = ClaimEffect(claim_id=claim_id)

    result = effect.add_banner(
        key="test-key",
        narrative="Test banner message",
        intent=BannerAlertIntent.WARNING,
    )

    assert result.type == EffectType.ADD_CLAIM_BANNER_ALERT
    payload = json.loads(result.payload)["data"]
    assert payload["href"] is None


def test_add_banner_requires_existing_claim(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that add_banner validates claim exists."""
    mock_db_queries["claim_banner"].objects.filter.return_value.exists.return_value = False
    effect = ClaimEffect(claim_id="nonexistent-claim")

    with pytest.raises(ValidationError) as exc_info:
        effect.add_banner(
            key="test-key",
            narrative="Test message",
            intent=BannerAlertIntent.INFO,
        )

    err_msg = repr(exc_info.value)
    assert "Claim with id nonexistent-claim does not exist" in err_msg


def test_add_banner_narrative_max_length(mock_db_queries: dict[str, MagicMock]) -> None:
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


def test_add_banner_narrative_at_max_length(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that narrative at exactly 90 characters is valid."""
    effect = ClaimEffect(claim_id="claim-id")
    max_narrative = "x" * 90

    result = effect.add_banner(
        key="test-key",
        narrative=max_narrative,
        intent=BannerAlertIntent.INFO,
    )

    assert max_narrative in result.payload


def test_remove_banner(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test remove_banner returns correct effect."""
    claim_id = "test-claim-id"
    effect = ClaimEffect(claim_id=claim_id)

    result = effect.remove_banner(key="test-key")

    assert result.type == EffectType.REMOVE_CLAIM_BANNER_ALERT
    payload = json.loads(result.payload)["data"]
    assert payload["claim_id"] == "test-claim-id"
    assert payload["key"] == "test-key"


def test_remove_banner_requires_existing_claim(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that remove_banner validates claim exists."""
    mock_db_queries["claim_banner"].objects.filter.return_value.exists.return_value = False
    effect = ClaimEffect(claim_id="nonexistent-claim")

    with pytest.raises(ValidationError) as exc_info:
        effect.remove_banner(key="test-key")

    err_msg = repr(exc_info.value)
    assert "Claim with id nonexistent-claim does not exist" in err_msg


def test_update_provider_with_only_claim_id(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that update_provider with no optional params returns correct effect."""
    claim = ClaimEffect(claim_id="claim-id")
    effect = claim.update_provider()

    assert effect.type == EffectType.UPDATE_CLAIM_PROVIDER
    payload = json.loads(effect.payload)["data"]
    assert payload == {"claim_id": "claim-id"}


def test_update_provider_with_clia_number(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that update_provider includes clia_number when provided."""
    claim = ClaimEffect(claim_id="claim-id")
    effect = claim.update_provider(clia_number="12D4567890")

    payload = json.loads(effect.payload)["data"]
    assert payload["claim_id"] == "claim-id"
    assert payload["clia_number"] == "12D4567890"


def test_update_provider_with_billing_provider(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that update_provider includes billing_provider fields with prefix."""
    claim = ClaimEffect(claim_id="claim-id")
    billing = ClaimBillingProvider(name="Test Practice", npi="1234567890", state="CA")
    effect = claim.update_provider(billing_provider=billing)

    payload = json.loads(effect.payload)["data"]
    assert payload["billing_provider_name"] == "Test Practice"
    assert payload["billing_provider_npi"] == "1234567890"
    assert payload["billing_provider_state"] == "CA"


def test_update_provider_with_provider(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that update_provider includes provider fields with prefix."""
    claim = ClaimEffect(claim_id="claim-id")
    provider = ClaimProvider(first_name="John", last_name="Doe", npi="9876543210")
    effect = claim.update_provider(provider=provider)

    payload = json.loads(effect.payload)["data"]
    assert payload["provider_first_name"] == "John"
    assert payload["provider_last_name"] == "Doe"
    assert payload["provider_npi"] == "9876543210"


def test_update_provider_with_referring_provider(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that update_provider includes referring_provider fields with prefix."""
    claim = ClaimEffect(claim_id="claim-id")
    referring = ClaimReferringProvider(first_name="Jane", last_name="Smith", npi="1112223334")
    effect = claim.update_provider(referring_provider=referring)

    payload = json.loads(effect.payload)["data"]
    assert payload["referring_provider_first_name"] == "Jane"
    assert payload["referring_provider_last_name"] == "Smith"
    assert payload["referring_provider_npi"] == "1112223334"


def test_update_provider_with_ordering_provider(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that update_provider includes ordering_provider fields with prefix."""
    claim = ClaimEffect(claim_id="claim-id")
    ordering = ClaimOrderingProvider(first_name="Bob", last_name="Jones", npi="5556667778")
    effect = claim.update_provider(ordering_provider=ordering)

    payload = json.loads(effect.payload)["data"]
    assert payload["ordering_provider_first_name"] == "Bob"
    assert payload["ordering_provider_last_name"] == "Jones"
    assert payload["ordering_provider_npi"] == "5556667778"


def test_update_provider_with_facility(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that update_provider includes facility fields with prefix."""
    claim = ClaimEffect(claim_id="claim-id")
    facility = ClaimFacility(name="General Hospital", npi="1231231234", state="NY")
    effect = claim.update_provider(facility=facility)

    payload = json.loads(effect.payload)["data"]
    assert payload["facility_name"] == "General Hospital"
    assert payload["facility_npi"] == "1231231234"
    assert payload["facility_state"] == "NY"


def test_update_provider_facility_date_isoformat(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that facility hospitalization dates are serialized as ISO format strings."""
    claim = ClaimEffect(claim_id="claim-id")
    facility = ClaimFacility(
        name="General Hospital",
        hosp_from_date=date(2024, 1, 15),
        hosp_to_date=date(2024, 1, 20),
    )
    effect = claim.update_provider(facility=facility)

    payload = json.loads(effect.payload)["data"]
    assert payload["hosp_from_date"] == "2024-01-15"
    assert payload["hosp_to_date"] == "2024-01-20"


def test_update_provider_with_all_params(mock_db_queries: dict[str, MagicMock]) -> None:
    """Test that update_provider includes all params with prefixed keys."""
    claim = ClaimEffect(claim_id="claim-id")
    effect = claim.update_provider(
        clia_number="12D4567890",
        billing_provider=ClaimBillingProvider(name="Test Practice"),
        provider=ClaimProvider(first_name="John", last_name="Doe"),
        referring_provider=ClaimReferringProvider(first_name="Jane", last_name="Smith"),
        ordering_provider=ClaimOrderingProvider(first_name="Bob", last_name="Jones"),
        facility=ClaimFacility(name="General Hospital"),
    )

    payload = json.loads(effect.payload)["data"]
    assert payload["claim_id"] == "claim-id"
    assert payload["clia_number"] == "12D4567890"
    assert payload["billing_provider_name"] == "Test Practice"
    assert payload["provider_first_name"] == "John"
    assert payload["provider_last_name"] == "Doe"
    assert payload["referring_provider_first_name"] == "Jane"
    assert payload["referring_provider_last_name"] == "Smith"
    assert payload["ordering_provider_first_name"] == "Bob"
    assert payload["ordering_provider_last_name"] == "Jones"
    assert payload["facility_name"] == "General Hospital"


def test_update_provider_excludes_none_dataclass_fields(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that to_dict excludes fields that are None."""
    claim = ClaimEffect(claim_id="claim-id")
    billing = ClaimBillingProvider(name="Test Practice")
    effect = claim.update_provider(billing_provider=billing)

    payload = json.loads(effect.payload)["data"]
    assert payload["billing_provider_name"] == "Test Practice"
    assert "billing_provider_phone" not in payload
    assert "billing_provider_npi" not in payload


def test_update_provider_requires_existing_claim(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that update_provider validates the claim exists."""
    mock_db_queries["claim_provider"].objects.filter.return_value.first.return_value = None
    claim = ClaimEffect(claim_id="invalid-claim-id")

    with pytest.raises(ValidationError) as e:
        claim.update_provider()

    err_msg = repr(e.value)
    assert "Claim with id invalid-claim-id does not exist." in err_msg


def test_update_provider_requires_existing_provider_info(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Test that update_provider validates the claim has existing provider information."""
    mock_db_queries["claim_provider_obj"].provider = None
    claim = ClaimEffect(claim_id="claim-id")

    with pytest.raises(ValidationError) as e:
        claim.update_provider()

    err_msg = repr(e.value)
    assert "does not have any existing provider information to update." in err_msg
