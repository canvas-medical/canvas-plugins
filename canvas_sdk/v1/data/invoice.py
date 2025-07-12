from django.db import models

from canvas_sdk.v1.data.base import Model


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


class Invoice(Model):
    """Represents a full invoice for a patient."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_invoicefull_001"

    originator = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.PROTECT, related_name="generated_invoices"
    )
    recipient = models.ForeignKey("v1.Patient", on_delete=models.CASCADE, related_name="invoices")
    recipient_type = models.CharField(max_length=10, choices=InvoiceRecipients.choices)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    # invoice_pdf = models.FileField(blank=True, null=True, upload_to=invoice_upload)
    status = models.CharField(max_length=10, choices=InvoiceStatus.choices)
    workflow = models.CharField(max_length=10, choices=InvoiceWorkflow.choices)
    # claims = models.ManyToManyField("v1.Claim", related_name="full_invoices")
    error_message = models.TextField()
    sent_mean = models.CharField(max_length=6, choices=InvoiceSentMeans.choices)


__exports__ = (
    "Invoice",
    "InvoiceRecipients",
    "InvoiceStatus",
    "InvoiceWorkflow",
    "InvoiceSentMeans",
)
