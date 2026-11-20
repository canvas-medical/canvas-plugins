from decimal import Decimal

import factory

from canvas_sdk.v1.data import Invoice, InvoiceClaim
from canvas_sdk.v1.data.invoice import InvoiceRecipients, InvoiceStatus, InvoiceWorkflow


class InvoiceFactory(factory.django.DjangoModelFactory[Invoice]):
    """Factory for creating an Invoice."""

    class Meta:
        model = Invoice

    originator = factory.SubFactory("canvas_sdk.test_utils.factories.CanvasUserFactory")
    recipient = factory.SubFactory("canvas_sdk.test_utils.factories.PatientFactory")
    recipient_type = InvoiceRecipients.PATIENT
    total_amount = Decimal("50.00")
    status = InvoiceStatus.ACTIVE
    workflow = InvoiceWorkflow.ADHOC


class InvoiceClaimFactory(factory.django.DjangoModelFactory[InvoiceClaim]):
    """Factory for linking an Invoice to a Claim."""

    class Meta:
        model = InvoiceClaim

    invoice = factory.SubFactory(InvoiceFactory)
    claim = factory.SubFactory("canvas_sdk.test_utils.factories.ClaimFactory")
