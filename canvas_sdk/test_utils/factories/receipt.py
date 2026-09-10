from decimal import Decimal

import factory

from canvas_sdk.v1.data import Receipt


class ReceiptFactory(factory.django.DjangoModelFactory[Receipt]):
    """Factory for creating a Receipt."""

    class Meta:
        model = Receipt

    account_balance_before_collection = Decimal("100.00")
    account_balance_after_collection = Decimal("50.00")
    discount = Decimal("0.00")
    receipt = factory.Sequence(lambda n: f"receipts/receipt_{n}.pdf")
