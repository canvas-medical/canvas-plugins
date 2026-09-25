import datetime
from decimal import Decimal

import factory

from canvas_sdk.v1.data import PaymentCollection


class PaymentCollectionFactory(factory.django.DjangoModelFactory[PaymentCollection]):
    """Factory for creating a PaymentCollection."""

    class Meta:
        model = PaymentCollection

    total_collected = Decimal("50.00")
    method = "card"
    check_number = ""
    check_date = datetime.date(2026, 1, 1)
    deposit_date = datetime.date(2026, 1, 1)
    description = ""
