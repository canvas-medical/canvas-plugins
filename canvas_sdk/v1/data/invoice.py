from django.db import models

from canvas_sdk.v1.data.base import Model, TimestampedModel
from canvas_sdk.v1.data.utils import presigned_url


class InvoiceRecipients(models.TextChoices):
    """Choices for invoice recipients."""

    PATIENT = "patient", "Patient"
    GUARANTOR = "guarantor", "Guarantor"


class InvoiceStatus(models.TextChoices):
    """Choices for invoice status."""

    ACTIVE = "active", "Active"
    ERROR = "error", "Error"
    ARCHIVED = "archived", "Archived"


class InvoiceWorkflow(models.TextChoices):
    """Choices for invoice workflow."""

    AUTOMATED = "automated", "Automated"
    ADHOC = "adhoc", "Adhoc"
    BATCH = "batch", "Batch"


class InvoiceSentMeans(models.TextChoices):
    """Choices for how the invoice was sent."""

    MAIL = "mail", "Mail"
    EMAIL = "e-mail", "E-mail"


class Invoice(TimestampedModel):
    """Represents a full invoice for a patient."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_invoicefull_001"

    originator = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.PROTECT, related_name="generated_invoices"
    )
    recipient = models.ForeignKey("v1.Patient", on_delete=models.CASCADE, related_name="invoices")
    recipient_type = models.CharField(max_length=10, choices=InvoiceRecipients.choices)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    invoice_pdf = models.FileField(null=True)
    status = models.CharField(max_length=10, choices=InvoiceStatus.choices)
    workflow = models.CharField(max_length=10, choices=InvoiceWorkflow.choices)
    claims = models.ManyToManyField(
        "v1.Claim", related_name="full_invoices", through="v1.InvoiceClaim"
    )
    error_message = models.TextField(null=True, blank=True)
    sent_mean = models.CharField(max_length=6, choices=InvoiceSentMeans.choices, null=True)

    @property
    def invoice_pdf_url(self) -> str | None:
        """Return a presigned URL for the invoice PDF, or None if unset."""
        if self.invoice_pdf:
            return presigned_url(self.invoice_pdf.name)
        return None


class InvoiceClaim(Model):
    """M2M for Invoice -> Claims."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_invoicefull_claims_001"

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, db_column="invoicefull_id")
    claim = models.ForeignKey("v1.Claim", on_delete=models.CASCADE)


__exports__ = (
    "Invoice",
    "InvoiceClaim",
    "InvoiceRecipients",
    "InvoiceStatus",
    "InvoiceWorkflow",
    "InvoiceSentMeans",
)
