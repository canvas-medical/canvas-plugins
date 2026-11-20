from typing import Any

import pytest

from canvas_sdk.test_utils.factories import (
    CanvasUserFactory,
    ClaimLineItemFactory,
    LineItemTransferFactory,
    NewLineItemAdjustmentFactory,
    NewLineItemPaymentFactory,
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "transaction_factory",
    [NewLineItemPaymentFactory, NewLineItemAdjustmentFactory, LineItemTransferFactory],
    ids=lambda f: f.__name__,
)
def test_active_excludes_transactions_entered_in_error(transaction_factory: Any) -> None:
    """active() returns the transactions that were not entered in error."""
    line_item = ClaimLineItemFactory.create()
    active = transaction_factory.create(claim_line_item=line_item)
    transaction_factory.create(
        claim_line_item=line_item, entered_in_error=CanvasUserFactory.create()
    )

    assert list(transaction_factory._meta.model.objects.active()) == [active]
