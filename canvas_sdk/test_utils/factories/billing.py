from decimal import Decimal

import factory

from canvas_sdk.v1.data.billing import BillingLineItem


class BillingLineItemFactory(factory.django.DjangoModelFactory[BillingLineItem]):
    """Factory for creating BillingLineItem test data."""

    class Meta:
        model = BillingLineItem

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory(
        "canvas_sdk.test_utils.factories.NoteFactory", patient=factory.SelfAttribute("..patient")
    )
    charge = Decimal("100.00")
    description = "Office Visit"
