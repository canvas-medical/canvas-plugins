from decimal import Decimal
from typing import Any

import pytest

from canvas_sdk.test_utils.factories import ClaimFactory, ClaimLineItemFactory
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
    return model.objects.create(
        posting=BasePosting.objects.create(claim=line_item.claim),
        billing_line_item_id=line_item.dbid,
        amount=Decimal(amount),
        **_MODEL_FIELDS[model],
    )


@pytest.mark.django_db
@pytest.mark.parametrize("model", list(_MODEL_FIELDS), ids=lambda model: model.__name__)
def test_billing_line_item_is_the_claim_line_item_posted_to(
    model: type[LineItemTransaction],
) -> None:
    """billing_line_item resolves to the claim line item, not a charge that shares its id."""
    charge = _charge(dbid=2002, cpt="99213")
    line_item = ClaimLineItemFactory.create(dbid=1001, billing_line_item=charge)
    _charge(dbid=1001, cpt="NOSHOW")

    transaction = model.objects.get(dbid=_post(model, line_item, "10.00").dbid)

    assert transaction.billing_line_item == line_item
    assert transaction.billing_line_item.claim == transaction.posting.claim
    assert transaction.billing_line_item.billing_line_item == charge


@pytest.mark.django_db
def test_claim_line_item_exposes_its_line_item_transactions() -> None:
    """The reverse relations are on ClaimLineItem and no longer on BillingLineItem."""
    line_item = ClaimLineItemFactory.create()
    payment = _post(NewLineItemPayment, line_item, "10.00")
    adjustment = _post(NewLineItemAdjustment, line_item, "20.00")
    transfer = _post(LineItemTransfer, line_item, "30.00")

    assert list(line_item.newlineitempayments.all()) == [payment]
    assert list(line_item.newlineitemadjustments.all()) == [adjustment]
    assert list(line_item.lineitemtransfers.all()) == [transfer]
    for accessor in ("newlineitempayments", "newlineitemadjustments", "lineitemtransfers"):
        assert not hasattr(BillingLineItem, accessor)


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
    """Each balance annotation totals its own transaction type on the line item."""
    line_item = ClaimLineItemFactory.create(status=ClaimLineItemStatus.REMOVED)
    _post(NewLineItemPayment, line_item, "10.00")
    _post(NewLineItemPayment, line_item, "5.00")
    other_line_item = ClaimLineItemFactory.create(claim=line_item.claim)
    _post(NewLineItemAdjustment, other_line_item, "20.00")
    _post(LineItemTransfer, other_line_item, "30.00")

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
        line_item.dbid: (Decimal("15.00"), Decimal("0"), Decimal("0")),
        other_line_item.dbid: (Decimal("0"), Decimal("20.00"), Decimal("30.00")),
    }
