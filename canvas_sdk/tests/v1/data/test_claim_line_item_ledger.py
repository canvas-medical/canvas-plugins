from decimal import Decimal
from typing import Any

import pytest

from canvas_sdk.test_utils.factories import (
    CanvasUserFactory,
    ClaimFactory,
    ClaimLineItemFactory,
)
from canvas_sdk.v1.data import (
    BasePosting,
    BillingLineItem,
    ClaimLineItem,
    LineItemTransfer,
    NewLineItemAdjustment,
    NewLineItemPayment,
)
from canvas_sdk.v1.data.claim_line_item import ClaimLineItemStatus

LineItemTransaction = NewLineItemPayment | NewLineItemAdjustment | LineItemTransfer

_MODEL_FIELDS: dict[type[LineItemTransaction], dict[str, Any]] = {
    NewLineItemPayment: {"charged": Decimal("100.00")},
    NewLineItemAdjustment: {"deviated_from_posting_ruleset": False, "write_off": False},
    LineItemTransfer: {"deviated_from_posting_ruleset": False},
}


def _charge(**kwargs: Any) -> BillingLineItem:
    return BillingLineItem.objects.create(charge=Decimal("100.00"), units=1, command_id=1, **kwargs)


def _post(
    model: type[LineItemTransaction], line_item: ClaimLineItem, amount: str
) -> LineItemTransaction:
    # Like the view, both columns get the claim line id, so the test DB needs a charge with that id.
    if not BillingLineItem.objects.filter(dbid=line_item.dbid).exists():
        _charge(dbid=line_item.dbid)
    return model.objects.create(
        posting=BasePosting.objects.create(claim=line_item.claim),
        billing_line_item_id=line_item.dbid,
        claim_line_item=line_item,
        amount=Decimal(amount),
        **_MODEL_FIELDS[model],
    )


@pytest.mark.django_db
@pytest.mark.parametrize("model", list(_MODEL_FIELDS), ids=lambda model: model.__name__)
def test_claim_line_item_is_the_line_the_amount_was_posted_to(
    model: type[LineItemTransaction],
) -> None:
    """claim_line_item is the claim line posted to; billing_line_item is unchanged."""
    charge = _charge(dbid=2002, cpt="99213")
    line_item = ClaimLineItemFactory.create(dbid=1001, billing_line_item=charge)
    unrelated = _charge(dbid=1001, cpt="NOSHOW")

    transaction = model.objects.get(dbid=_post(model, line_item, "10.00").dbid)

    assert transaction.claim_line_item == line_item
    assert transaction.claim_line_item.claim == transaction.posting.claim
    assert transaction.claim_line_item.billing_line_item == charge
    assert transaction.billing_line_item == unrelated


@pytest.mark.django_db
def test_claim_line_item_supports_queryset_lookups() -> None:
    """claim_line_item works in filter, select_related, prefetch_related and values."""
    line_item = ClaimLineItemFactory.create(proc_code="99213")
    payment = _post(NewLineItemPayment, line_item, "10.00")
    payments = NewLineItemPayment.objects.filter(claim_line_item__claim=line_item.claim)

    assert list(NewLineItemPayment.objects.filter(claim_line_item=line_item)) == [payment]
    assert [p.claim_line_item for p in payments.select_related("claim_line_item")] == [line_item]
    assert [p.claim_line_item for p in payments.prefetch_related("claim_line_item")] == [line_item]
    assert list(payments.values_list("claim_line_item__proc_code", flat=True)) == ["99213"]


@pytest.mark.django_db
def test_claim_line_item_exposes_its_line_item_transactions() -> None:
    """ClaimLineItem gets the reverse relations, and BillingLineItem keeps its own."""
    line_item = ClaimLineItemFactory.create()
    payment = _post(NewLineItemPayment, line_item, "10.00")
    adjustment = _post(NewLineItemAdjustment, line_item, "20.00")
    transfer = _post(LineItemTransfer, line_item, "30.00")

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
    paid, adjusted, transferred, untouched, netted_to_zero = (
        ClaimLineItemFactory.create(claim=claim, status=ClaimLineItemStatus.REMOVED)
        for _ in range(5)
    )
    _post(NewLineItemPayment, paid, "10.00")
    _post(NewLineItemAdjustment, adjusted, "20.00")
    _post(LineItemTransfer, transferred, "30.00")
    _post(NewLineItemPayment, netted_to_zero, "15.00")
    _post(NewLineItemPayment, netted_to_zero, "-15.00")

    kept = ClaimLineItem.objects.filter(claim=claim).exclude_removed_line_items_without_balances()

    assert set(kept) == {active, paid, adjusted, transferred}


@pytest.mark.django_db
def test_exclude_removed_line_items_without_balances_sums_each_transaction_type() -> None:
    """Each balance annotation totals its own type, even with several types on one line."""
    line_item = ClaimLineItemFactory.create(status=ClaimLineItemStatus.REMOVED)
    _post(NewLineItemPayment, line_item, "41.00")
    _post(NewLineItemPayment, line_item, "21.00")
    _post(NewLineItemAdjustment, line_item, "38.00")
    other_line_item = ClaimLineItemFactory.create(claim=line_item.claim)
    _post(NewLineItemPayment, other_line_item, "10.00")
    _post(NewLineItemAdjustment, other_line_item, "5.00")
    _post(NewLineItemAdjustment, other_line_item, "5.00")
    _post(LineItemTransfer, other_line_item, "3.00")
    _post(LineItemTransfer, other_line_item, "4.00")

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
        line_item.dbid: (Decimal("62.00"), Decimal("38.00"), Decimal("0")),
        other_line_item.dbid: (Decimal("10.00"), Decimal("10.00"), Decimal("7.00")),
    }


@pytest.mark.django_db
def test_exclude_removed_line_item_without_active_posting() -> None:
    """Removed line items are kept only while an active transaction is posted to them."""
    claim = ClaimFactory.create()
    active = ClaimLineItemFactory.create(claim=claim)
    paid, voided, untouched = (
        ClaimLineItemFactory.create(claim=claim, status=ClaimLineItemStatus.REMOVED)
        for _ in range(3)
    )
    _post(NewLineItemPayment, paid, "10.00")
    voided_payment = _post(NewLineItemPayment, voided, "10.00")
    voided_payment.entered_in_error = CanvasUserFactory.create()
    voided_payment.save()

    kept = ClaimLineItem.objects.filter(
        claim=claim
    ).exclude_removed_line_item_without_active_posting()

    assert set(kept) == {active, paid}
