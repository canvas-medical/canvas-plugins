"""Factories for billing-related models."""

from decimal import Decimal

import factory

from canvas_sdk.v1.data.billing import BillingLineItem, BillingLineItemStatus


class BillingLineItemFactory(factory.django.DjangoModelFactory[BillingLineItem]):
    """Factory for creating BillingLineItem test data."""

    class Meta:
        model = BillingLineItem

    patient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    note = factory.SubFactory(
        "canvas_sdk.test_utils.factories.NoteFactory", patient=factory.SelfAttribute("..patient")
    )
    cpt = "99213"  # Default office visit code
    charge = Decimal("100.00")
    description = "Office Visit"
    units = 1
    command_type = "encounter"
    command_id = 1
    status = BillingLineItemStatus.ACTIVE
