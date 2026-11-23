from decimal import Decimal

import factory

from canvas_sdk.v1.data import BillingLineItem


class BillingLineItemFactory(factory.django.DjangoModelFactory[BillingLineItem]):
    """Factory for creating a BillingLineItem."""

    class Meta:
        model = BillingLineItem

    charge = Decimal("100.00")
    units = 1
    command_id = 1
