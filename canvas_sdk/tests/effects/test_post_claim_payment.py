import json
from collections.abc import Generator
from decimal import Decimal
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from django.db.models import QuerySet
from pydantic import ValidationError

from canvas_sdk.effects.payment.base import ClaimAllocation, LineItemTransaction, PaymentMethod
from canvas_sdk.effects.payment.post_claim_payment import PostClaimPayment


@pytest.fixture
def mock_db_queries() -> Generator[dict[str, MagicMock]]:
    """Mock common DB queries used by post_claim_payment._get_error_details."""
    with (
        patch("canvas_sdk.effects.payment.base.Claim.objects") as mock_claim_q,
        patch("canvas_sdk.effects.payment.base.ClaimLineItem.objects") as mock_cli_q,
        patch("canvas_sdk.effects.payment.base.ClaimQueue.objects") as mock_queue,
    ):
        # A representative Claim object used by tests
        mock_claim = MagicMock()
        mock_claim.id = "claim-1"

        # QuerySet-like mock returned by Claim.objects.filter(...)
        claims_qs = MagicMock()
        claims_qs.count.return_value = 1
        claims_qs.values_list.return_value = [mock_claim.id]
        claims_qs.get.return_value = mock_claim
        claims_qs.first.return_value = mock_claim

        mock_claim_q.filter.return_value = claims_qs
        mock_claim_q.filter.return_value.first.return_value = mock_claim

        mock_queue.filter.return_value.exists.return_value = True

        # Make claim.line_items.active().filter(id=...) return a ClaimLineItem-like mock for any id.
        def filter_side_effect(**kwargs: Any) -> QuerySet:
            qs = MagicMock()
            qs.first.return_value = MagicMock(id=kwargs.get("id"), proc_code="PROC")
            return qs

        mock_claim.line_items.active.return_value.filter.side_effect = filter_side_effect

        # Ensure the coverage exists for transfer targets / provided coverage id
        mock_claim.coverages.active.return_value.filter.return_value.exists.return_value = True

        yield {
            "claim": mock_claim_q,
            "claims_qs": claims_qs,
            "claim_line_item": mock_cli_q,
            "mock_claim": mock_claim,
            "mock_queue": mock_queue,
        }


def test_post_claim_payment_requires_existing_claim(mock_db_queries: dict[str, MagicMock]) -> None:
    """Tests that the claim_id is valid and the Claim exists."""
    # Simulate Claim.objects.filter(...).first() returning None (claim does not exist)
    mock_db_queries["claim"].filter.return_value.first.return_value = None

    claim_alloc = ClaimAllocation(
        claim_id="non-existent-claim",
        claim_coverage_id="patient",
        line_item_transactions=[],
    )

    post = PostClaimPayment(
        claim=claim_alloc, method=PaymentMethod.CASH, total_collected=Decimal("0.00")
    )
    with pytest.raises(ValidationError) as e:
        post.apply()
    err_msg = repr(e.value)
    assert (
        "1 validation error for PostClaimPayment\n  The provided claim_id does not correspond with an existing Claim [type=value, input_value='non-existent-claim', input_type=str]"
        in err_msg
    )


def test_post_claim_payment_requires_claim_coverage_id_that_is_active_coverage(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Tests that the claim_coverage_id is valid and is an active coverage for the claim."""
    mock_db_queries["mock_claim"].coverages.active.return_value.filter.return_value = []

    claim_alloc = ClaimAllocation(
        claim_id=mock_db_queries["mock_claim"].id,
        claim_coverage_id="coverage-1",
        line_item_transactions=[],
    )
    post = PostClaimPayment(
        claim=claim_alloc, method=PaymentMethod.CASH, total_collected=Decimal("0.00")
    )
    with pytest.raises(ValidationError) as e:
        post.apply()
    err_msg = repr(e.value)
    assert (
        "1 validation error for PostClaimPayment\n  The provided claim_coverage_id does not correspond to an active coverage for the claim [type=value, input_value={'claim_coverage_id': 'coverage-1'}, input_type=dict]"
        in err_msg
    )


def test_post_claim_payment_requires_existing_move_to_queue_name(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Tests that the move_to_queue_name is an existing ClaimQueue."""
    mock_db_queries["mock_queue"].filter.return_value.exists.return_value = False

    claim_alloc = ClaimAllocation(
        claim_id=mock_db_queries["mock_claim"].id,
        claim_coverage_id="coverage-1",
        line_item_transactions=[],
        move_to_queue_name="beep-boop",
    )
    post = PostClaimPayment(
        claim=claim_alloc, method=PaymentMethod.CASH, total_collected=Decimal("0.00")
    )
    with pytest.raises(ValidationError) as e:
        post.apply()
    err_msg = repr(e.value)
    assert (
        "1 validation error for PostClaimPayment\n  The provided move_to_queue_name does not correspond to an existing ClaimQueue [type=value, input_value='beep-boop', input_type=str]"
        in err_msg
    )


@pytest.mark.parametrize(
    "scenario",
    [
        {
            "name": "missing_line_item",
            "line_items_map": {},
            "active_coverages_filter_result": [1],
            "alloc_kwargs": {
                "claim_coverage_id": "coverage-1",
                "line_item_transactions": [
                    LineItemTransaction(claim_line_item_id="missing-line", payment=Decimal("1.00"))
                ],
            },
            "expected_substring": "The provided claim_line_item_id does not correspond to an existing ClaimLineItem",
        },
        {
            "name": "patient_allowed",
            "line_items_map": {"line-1": MagicMock(proc_code="PROC")},
            "active_coverages_filter_result": [1],
            "alloc_kwargs": {
                "claim_coverage_id": "patient",
                "line_item_transactions": [
                    LineItemTransaction(claim_line_item_id="line-1", allowed=Decimal("1.00"))
                ],
            },
            "expected_substring": "Allowed amount should be $0 or None for patient postings",
        },
        {
            "name": "payment_required",
            "line_items_map": {"line-2": MagicMock(proc_code="PROC")},
            "active_coverages_filter_result": [1],
            "alloc_kwargs": {
                "claim_coverage_id": "coverage-1",
                "line_item_transactions": [
                    LineItemTransaction(claim_line_item_id="line-2"),
                ],
            },
            "expected_substring": "Payment or adjustment is required for a claim line item's first transaction",
        },
        {
            "name": "adjustment_required_sequential",
            "line_items_map": {"line-3": MagicMock(proc_code="PROC")},
            "active_coverages_filter_result": [1],
            "alloc_kwargs": {
                "claim_coverage_id": "coverage-1",
                "line_item_transactions": [
                    LineItemTransaction(claim_line_item_id="line-3", payment=Decimal("1.00")),
                    LineItemTransaction(claim_line_item_id="line-3"),
                ],
            },
            "expected_substring": "Specify an adjustment amount for added adjustments or remove the added adjustment line for this claim line item",
        },
        {
            "name": "adjustment_type_required",
            "line_items_map": {"line-4": MagicMock(proc_code="PROC")},
            "active_coverages_filter_result": [1],
            "alloc_kwargs": {
                "claim_coverage_id": "coverage-1",
                "line_item_transactions": [
                    LineItemTransaction(claim_line_item_id="line-4", adjustment=Decimal("1.00")),
                ],
            },
            "expected_substring": "Specify an adjustment code for the adjustment amount",
        },
        {
            "name": "transfer_to_required",
            "line_items_map": {"line-5": MagicMock(proc_code="PROC")},
            "active_coverages_filter_result": [1],
            "alloc_kwargs": {
                "claim_coverage_id": "coverage-1",
                "line_item_transactions": [
                    LineItemTransaction(
                        claim_line_item_id="line-5",
                        adjustment=Decimal("1.00"),
                        adjustment_code="Transfer",
                    )
                ],
            },
            "expected_substring": "Specify a payer to transfer the adjusted amount",
        },
        {
            "name": "adjustment_conflict",
            "line_items_map": {"line-6": MagicMock(proc_code="PROC")},
            "active_coverages_filter_result": [1],
            "alloc_kwargs": {
                "claim_coverage_id": "coverage-1",
                "line_item_transactions": [
                    LineItemTransaction(
                        claim_line_item_id="line-6",
                        adjustment=Decimal("1.00"),
                        adjustment_code="PR-2",
                        write_off=True,
                        transfer_remaining_balance_to="some-payer",
                    )
                ],
            },
            "expected_substring": "Adjustments cannot write off and transfer at the same time",
        },
        {
            "name": "copay_payer_invalid",
            "line_items_map": {"copay-line": MagicMock(proc_code="COPAY")},
            "active_coverages_filter_result": [1],
            "alloc_kwargs": {
                "claim_coverage_id": "coverage-1",
                "line_item_transactions": [
                    LineItemTransaction(claim_line_item_id="copay-line", payment=Decimal("1.00")),
                ],
            },
            "expected_substring": "COPAY payments may only be posted by patients",
        },
        {
            "name": "transfer_to_invalid_coverage",
            "line_items_map": {"line-7": MagicMock(proc_code="PROC")},
            "active_coverages_filter_result": [1],
            "active_coverages_exists_map": {"unknown-payer": False},
            "alloc_kwargs": {
                "claim_coverage_id": "coverage-1",
                "line_item_transactions": [
                    LineItemTransaction(
                        claim_line_item_id="line-7",
                        adjustment=Decimal("1.00"),
                        adjustment_code="Adj-1",
                        transfer_remaining_balance_to="unknown-payer",
                    )
                ],
            },
            "expected_substring": "Balance can only be transferred to patient or an active coverage for the claim",
        },
    ],
    ids=lambda s: s["name"],
)
def test_post_claim_payment_line_item_validation(
    mock_db_queries: dict[str, MagicMock], scenario: dict
) -> None:
    """Tests that the line_item_transaction validate works as expected, for each type of error possible."""
    mock_claim = mock_db_queries["mock_claim"]

    def set_line_items_map(mapping: dict[str, MagicMock]) -> None:
        def _filter_side_effect(**kwargs: Any) -> QuerySet:
            key = kwargs.get("id")
            qs = MagicMock()
            qs.first.return_value = mapping.get(key)  # type: ignore
            return qs

        mock_claim.line_items.active.return_value.filter.side_effect = _filter_side_effect

    # Ensure claim exists for all sub-cases
    mock_db_queries["claim"].filter.return_value.first.return_value = mock_claim

    s = scenario

    # Configure active coverages filter return for validate_claim_coverage
    active_coverages = mock_claim.coverages.active.return_value
    active_coverages.filter.return_value = s.get("active_coverages_filter_result", [1])

    # For transfer existence checks per-id (exists()), set exists return if provided
    if s.get("name") == "transfer_to_invalid_coverage":

        def cover_filter_side_effect(**kwargs: Any) -> QuerySet:
            qs = MagicMock()
            idx = kwargs.get("id")
            qs.exists.return_value = s.get("active_coverages_exists_map", {}).get(idx, False)
            return qs

        active_coverages.filter.side_effect = cover_filter_side_effect

    # Configure claim line items returned by id
    set_line_items_map(s["line_items_map"])

    claim_alloc = ClaimAllocation(
        claim_id=mock_claim.id,
        description=None,
        move_to_queue_name=None,
        **s["alloc_kwargs"],
    )

    post = PostClaimPayment(
        claim=claim_alloc, method=PaymentMethod.CASH, total_collected=Decimal("0.00")
    )

    with pytest.raises(ValidationError) as e:
        post.apply()
    err_msg = repr(e.value)
    assert s["expected_substring"] in err_msg, (
        f"{s['name']}: expected '{s['expected_substring']}' in {err_msg}"
    )


def test_post_claim_payment_check_method_has_required_fields(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Tests that when paymentmethod is check that check_number and check_date must be included."""
    claim_alloc = ClaimAllocation(
        claim_id=mock_db_queries["mock_claim"].id,
        claim_coverage_id="patient",
        line_item_transactions=[],
    )

    post = PostClaimPayment(
        claim=claim_alloc, method=PaymentMethod.CHECK, total_collected=Decimal("0.00")
    )

    with pytest.raises(ValidationError) as e:
        post.apply()

    err_msg = repr(e.value)
    assert (
        "2 validation errors for PostClaimPayment\n  Check number is required for payment method CHECK [type=value, input_value=None, input_type=NoneType]"
        in err_msg
    )
    assert (
        "Check date is required for payment method CHECK [type=value, input_value=None, input_type=NoneType]"
        in err_msg
    )


def test_valid_post_claim_payment_patient_payload_is_correct(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Tests that a valid PostClaimPayment for a patient payment has the correct payload on .apply()."""
    mock_claim = mock_db_queries["mock_claim"]

    lit1 = LineItemTransaction(claim_line_item_id="line-1", payment=Decimal("5.00"))
    lit2 = LineItemTransaction(claim_line_item_id="line-2", payment=Decimal("3.50"))

    claim_alloc = ClaimAllocation(
        claim_id=mock_claim.id,
        claim_coverage_id="patient",
        line_item_transactions=[lit1, lit2],
    )
    post = PostClaimPayment(
        claim=claim_alloc, method=PaymentMethod.CASH, total_collected=Decimal("8.50")
    )

    result = post.apply()

    assert json.loads(result.payload)["data"] == {
        "posting": {"description": None},
        "payment_collection": {
            "check_date": None,
            "check_number": None,
            "deposit_date": None,
            "method": "cash",
            "payment_description": None,
            "total_collected": "8.50",
        },
        "claims_allocation": [
            {
                "claim_id": str(mock_claim.id),
                "claim_coverage_id": "patient",
                "line_item_transactions": [
                    {
                        "charged": None,
                        "adjustment": None,
                        "adjustment_code": None,
                        "allowed": None,
                        "claim_line_item_id": "line-1",
                        "payment": "5.00",
                        "transfer_to": None,
                        "write_off": False,
                    },
                    {
                        "charged": None,
                        "adjustment": None,
                        "adjustment_code": None,
                        "allowed": None,
                        "claim_line_item_id": "line-2",
                        "payment": "3.50",
                        "transfer_to": None,
                        "write_off": False,
                    },
                ],
                "move_to_queue_name": None,
                "description": None,
            }
        ],
    }


def test_valid_post_claim_payment_coverage_payload_is_correct(
    mock_db_queries: dict[str, MagicMock],
) -> None:
    """Tests that a valid PostClaimPayment for a coverage payment has the correct payload on .apply()."""
    mock_claim = mock_db_queries["mock_claim"]

    lit1 = LineItemTransaction(
        claim_line_item_id="line-1",
        payment=Decimal("10.00"),
        adjustment=Decimal("2.00"),
        adjustment_code="Adj-1",
        transfer_remaining_balance_to="patient",
    )
    lit2 = LineItemTransaction(
        claim_line_item_id="line-2",
        payment=Decimal("5.50"),
        adjustment=Decimal("1.50"),
        adjustment_code="Adj-2",
        transfer_remaining_balance_to="secondary-coverage",
    )
    lit3 = LineItemTransaction(
        claim_line_item_id="line-3",
        payment=Decimal("2.25"),
        adjustment=Decimal("10.00"),
        adjustment_code="CO-45",
        write_off=True,
    )

    claim_alloc = ClaimAllocation(
        claim_id=mock_claim.id,
        claim_coverage_id="coverage-id",
        line_item_transactions=[lit1, lit2, lit3],
    )

    post = PostClaimPayment(
        claim=claim_alloc, method=PaymentMethod.CASH, total_collected=Decimal("17.75")
    )

    result = post.apply()

    assert json.loads(result.payload)["data"] == {
        "posting": {"description": None},
        "payment_collection": {
            "check_date": None,
            "check_number": None,
            "deposit_date": None,
            "method": "cash",
            "payment_description": None,
            "total_collected": "17.75",
        },
        "claims_allocation": [
            {
                "claim_id": str(mock_claim.id),
                "claim_coverage_id": "coverage-id",
                "line_item_transactions": [
                    {
                        "charged": None,
                        "adjustment": "2.00",
                        "adjustment_code": "Adj-1",
                        "allowed": None,
                        "claim_line_item_id": "line-1",
                        "payment": "10.00",
                        "transfer_to": "patient",
                        "write_off": False,
                    },
                    {
                        "charged": None,
                        "adjustment": "1.50",
                        "adjustment_code": "Adj-2",
                        "allowed": None,
                        "claim_line_item_id": "line-2",
                        "payment": "5.50",
                        "transfer_to": "secondary-coverage",
                        "write_off": False,
                    },
                    {
                        "charged": None,
                        "adjustment": "10.00",
                        "adjustment_code": "CO-45",
                        "allowed": None,
                        "claim_line_item_id": "line-3",
                        "payment": "2.25",
                        "transfer_to": None,
                        "write_off": True,
                    },
                ],
                "move_to_queue_name": None,
                "description": None,
            }
        ],
    }
