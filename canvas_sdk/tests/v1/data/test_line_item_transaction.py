from decimal import Decimal
from typing import Any

import pytest

from canvas_sdk.test_utils.factories import CanvasUserFactory, ClaimFactory
from canvas_sdk.v1.data import (
    BasePosting,
    BillingLineItem,
    LineItemTransfer,
    NewLineItemAdjustment,
    NewLineItemPayment,
)

LineItemTransaction = NewLineItemPayment | NewLineItemAdjustment | LineItemTransfer

_MODEL_FIELDS: dict[type[LineItemTransaction], dict[str, Any]] = {
    NewLineItemPayment: {"charged": Decimal("100.00")},
    NewLineItemAdjustment: {"deviated_from_posting_ruleset": False, "write_off": False},
    LineItemTransfer: {"deviated_from_posting_ruleset": False},
}


@pytest.mark.django_db
@pytest.mark.parametrize("model", list(_MODEL_FIELDS), ids=lambda model: model.__name__)
def test_active_excludes_transactions_entered_in_error(
    model: type[LineItemTransaction],
) -> None:
    """active() returns the transactions that were not entered in error."""
    fields = {
        "posting": BasePosting.objects.create(claim=ClaimFactory.create()),
        "billing_line_item": BillingLineItem.objects.create(
            charge=Decimal("100.00"), units=1, command_id=1
        ),
        "amount": Decimal("10.00"),
        **_MODEL_FIELDS[model],
    }
    active = model.objects.create(**fields)
    model.objects.create(entered_in_error=CanvasUserFactory.create(), **fields)

    assert list(model.objects.active()) == [active]
