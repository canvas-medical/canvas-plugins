import datetime
from decimal import Decimal

import factory

from canvas_sdk.v1.data import CreditCardCharge, CreditCardChargeState, PaymentCollection


class PaymentCollectionFactory(factory.django.DjangoModelFactory[PaymentCollection]):
    """Factory for creating a PaymentCollection."""

    class Meta:
        model = PaymentCollection

    total_collected = Decimal("50.00")
    method = "card"
    check_date = datetime.date(2026, 1, 1)
    deposit_date = datetime.date(2026, 1, 1)
    description = ""


class CreditCardChargeFactory(factory.django.DjangoModelFactory[CreditCardCharge]):
    """Factory for creating a CreditCardCharge."""

    class Meta:
        model = CreditCardCharge

    originator = factory.SubFactory("canvas_sdk.test_utils.factories.CanvasUserFactory")
    payment_collection = factory.SubFactory(PaymentCollectionFactory)
    payment_method = factory.SubFactory("canvas_sdk.test_utils.factories.PaymentCardFactory")
    state = CreditCardChargeState.CHARGED
    provider = "stripe"
