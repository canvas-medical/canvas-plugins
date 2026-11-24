from decimal import Decimal
from typing import Any

import pytest

from canvas_sdk.test_utils.factories import (
    BillingLineItemFactory,
    CanvasUserFactory,
    ClaimFactory,
    ClaimLineItemFactory,
    LineItemTransferFactory,
    NewLineItemAdjustmentFactory,
    NewLineItemPaymentFactory,
)
from canvas_sdk.v1.data import BillingLineItem, ClaimLineItem, NewLineItemPayment
from canvas_sdk.v1.data.claim_line_item import ClaimLineItemStatus

_TRANSACTION_FACTORIES = [
    NewLineItemPaymentFactory,
    NewLineItemAdjustmentFactory,
    LineItemTransferFactory,
]


@pytest.mark.django_db
@pytest.mark.parametrize("transaction_factory", _TRANSACTION_FACTORIES, ids=lambda f: f.__name__)
def test_claim_line_item_is_the_line_the_amount_was_posted_to(transaction_factory: Any) -> None:
    """claim_line_item is the claim line posted to; billing_line_item is unchanged."""
    charge = BillingLineItemFactory.create(dbid=2002, cpt="99213")
    line_item = ClaimLineItemFactory.create(dbid=1001, billing_line_item=charge)
    unrelated = BillingLineItemFactory.create(dbid=1001, cpt="NOSHOW")

    created = transaction_factory.create(claim_line_item=line_item)
    transaction = transaction_factory._meta.model.objects.get(dbid=created.dbid)

    assert transaction.claim_line_item == line_item
    assert transaction.claim_line_item.claim == transaction.posting.claim
    assert transaction.claim_line_item.billing_line_item == charge
    assert transaction.billing_line_item == unrelated


@pytest.mark.django_db
def test_claim_line_item_supports_queryset_lookups() -> None:
    """claim_line_item works in filter, select_related, prefetch_related and values."""
    line_item = ClaimLineItemFactory.create(proc_code="99213")
    payment = NewLineItemPaymentFactory.create(claim_line_item=line_item)
    payments = NewLineItemPayment.objects.filter(claim_line_item__claim=line_item.claim)

    assert list(NewLineItemPayment.objects.filter(claim_line_item=line_item)) == [payment]
    assert [p.claim_line_item for p in payments.select_related("claim_line_item")] == [line_item]
    assert [p.claim_line_item for p in payments.prefetch_related("claim_line_item")] == [line_item]
    assert list(payments.values_list("claim_line_item__proc_code", flat=True)) == ["99213"]


@pytest.mark.django_db
def test_claim_line_item_exposes_its_line_item_transactions() -> None:
    """ClaimLineItem gets the reverse relations, and BillingLineItem keeps its own."""
    line_item = ClaimLineItemFactory.create()
    payment = NewLineItemPaymentFactory.create(claim_line_item=line_item)
    adjustment = NewLineItemAdjustmentFactory.create(claim_line_item=line_item)
    transfer = LineItemTransferFactory.create(claim_line_item=line_item)

    assert list(line_item.newlineitempayments.all()) == [payment]
    assert list(line_item.newlineitemadjustments.all()) == [adjustment]
    assert list(line_item.lineitemtransfers.all()) == [transfer]
    prefetched = ClaimLineItem.objects.prefetch_related("newlineitempayments").get(
        dbid=line_item.dbid
    )
    assert list(prefetched.newlineitempayments.all()) == [payment]
    for accessor in ("newlineitempayments", "newlineitemadjustments", "lineitemtransfers"):
        assert hasattr(BillingLineItem, accessor)


@pytest.mark.django_db
def test_exclude_removed_line_items_without_balances() -> None:
    """Removed line items are kept only while a posted amount is left on them."""
    claim = ClaimFactory.create()
    active = ClaimLineItemFactory.create(claim=claim)
    paid, adjusted, transferred, _untouched, netted_to_zero = (
        ClaimLineItemFactory.create(claim=claim, status=ClaimLineItemStatus.REMOVED)
        for _ in range(5)
    )
    NewLineItemPaymentFactory.create(claim_line_item=paid, amount=Decimal("10.00"))
    NewLineItemAdjustmentFactory.create(claim_line_item=adjusted, amount=Decimal("20.00"))
    LineItemTransferFactory.create(claim_line_item=transferred, amount=Decimal("30.00"))
    NewLineItemPaymentFactory.create(claim_line_item=netted_to_zero, amount=Decimal("15.00"))
    NewLineItemPaymentFactory.create(claim_line_item=netted_to_zero, amount=Decimal("-15.00"))

    kept = ClaimLineItem.objects.filter(claim=claim).exclude_removed_line_items_without_balances()

    assert set(kept) == {active, paid, adjusted, transferred}


@pytest.mark.django_db
@pytest.mark.parametrize("transaction_factory", _TRANSACTION_FACTORIES, ids=lambda f: f.__name__)
def test_exclude_removed_line_items_without_balances_counts_soft_deleted_transactions(
    transaction_factory: Any,
) -> None:
    """A removed line item whose only transaction is soft-deleted still has a balance, as in home-app."""
    removed = ClaimLineItemFactory.create(status=ClaimLineItemStatus.REMOVED)
    transaction_factory.create(claim_line_item=removed, amount=Decimal("25.00"), deleted=True)

    kept = ClaimLineItem.objects.filter(
        claim=removed.claim
    ).exclude_removed_line_items_without_balances()

    assert list(kept) == [removed]


@pytest.mark.django_db
def test_exclude_removed_line_items_without_balances_sums_each_transaction_type() -> None:
    """Each balance annotation totals its own type, even with several types on one line."""
    line_item = ClaimLineItemFactory.create(status=ClaimLineItemStatus.REMOVED)
    NewLineItemPaymentFactory.create(claim_line_item=line_item, amount=Decimal("41.00"))
    NewLineItemPaymentFactory.create(claim_line_item=line_item, amount=Decimal("21.00"))
    NewLineItemAdjustmentFactory.create(claim_line_item=line_item, amount=Decimal("38.00"))
    other_line_item = ClaimLineItemFactory.create(claim=line_item.claim)
    NewLineItemPaymentFactory.create(claim_line_item=other_line_item, amount=Decimal("10.00"))
    NewLineItemAdjustmentFactory.create(claim_line_item=other_line_item, amount=Decimal("5.00"))
    NewLineItemAdjustmentFactory.create(claim_line_item=other_line_item, amount=Decimal("5.00"))
    LineItemTransferFactory.create(claim_line_item=other_line_item, amount=Decimal("3.00"))
    LineItemTransferFactory.create(claim_line_item=other_line_item, amount=Decimal("4.00"))

    kept = {
        item.dbid: (
            item.sum_of_all_payments,
            item.sum_of_all_adjustments,
            item.sum_of_all_transfers,
        )
        for item in ClaimLineItem.objects.filter(
            claim=line_item.claim
        ).exclude_removed_line_items_without_balances()
    }

    assert kept == {
        line_item.dbid: (Decimal("62.00"), Decimal("38.00"), Decimal(0)),
        other_line_item.dbid: (Decimal("10.00"), Decimal("10.00"), Decimal("7.00")),
    }


@pytest.mark.django_db
def test_exclude_removed_line_item_without_active_posting() -> None:
    """Removed line items are kept only while an active transaction is posted to them."""
    claim = ClaimFactory.create()
    active = ClaimLineItemFactory.create(claim=claim)
    paid, voided, _untouched = (
        ClaimLineItemFactory.create(claim=claim, status=ClaimLineItemStatus.REMOVED)
        for _ in range(3)
    )
    NewLineItemPaymentFactory.create(claim_line_item=paid)
    NewLineItemPaymentFactory.create(
        claim_line_item=voided, entered_in_error=CanvasUserFactory.create()
    )

    kept = ClaimLineItem.objects.filter(
        claim=claim
    ).exclude_removed_line_item_without_active_posting()

    assert set(kept) == {active, paid}
