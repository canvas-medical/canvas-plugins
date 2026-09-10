from decimal import Decimal
from typing import cast

from django.db import models

from canvas_sdk.v1.data.base import (
    AuditedModel,
    CommittableModelManager,
    CommittableQuerySet,
    IdentifiableModel,
)
from canvas_sdk.v1.data.utils import presigned_url, quantize


class Receipt(AuditedModel, IdentifiableModel):
    """A Canvas-generated payment receipt, one-to-one with a PaymentCollection.

    Read-only. ``receipt_url`` presigns the canonical receipt PDF that Canvas already generates for
    staff — there is no create/edit/regenerate path. A portal plugin scopes access to the
    authenticated patient by reaching receipts through that patient's payments
    (``patient.payments`` -> ``payment_collection.receipt``).
    """

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_receipt_001"

    objects = cast(CommittableQuerySet, CommittableModelManager())

    payment_collection = models.OneToOneField(
        "v1.PaymentCollection", on_delete=models.DO_NOTHING, related_name="receipt", null=True
    )
    account_balance_before_collection = models.DecimalField(max_digits=8, decimal_places=2)
    account_balance_after_collection = models.DecimalField(max_digits=8, decimal_places=2)
    discount = models.DecimalField(max_digits=8, decimal_places=2)
    template = models.CharField(max_length=250, blank=True, default="")
    receipt = models.CharField(max_length=255, null=True, blank=True)

    @property
    def receipt_url(self) -> str | None:
        """Return a short-lived presigned URL for the receipt PDF, or None when unset."""
        if self.receipt:
            return presigned_url(self.receipt)
        return None

    @property
    def total_posted_amount(self) -> Decimal:
        """Total posted with this collection: the sum of payments and write-off adjustments."""
        payment_collection = self.payment_collection
        if payment_collection is None:
            return quantize(0)
        return quantize(
            sum(posting.posted_amount for posting in payment_collection.postings.active())
        )

    @property
    def copay_amount(self) -> Decimal:
        """The amount posted as copays on this collection."""
        payment_collection = self.payment_collection
        if payment_collection is None:
            return quantize(0)
        return quantize(
            sum(
                posting.paid_amount
                for posting in payment_collection.postings.active()
                if hasattr(posting, "patientposting") and posting.patientposting.copay
            )
        )


__exports__ = ("Receipt",)
