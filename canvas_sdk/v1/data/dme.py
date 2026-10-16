from typing import cast

from django.db import models

from canvas_sdk.v1.data.base import (
    AuditedModel,
    CommittableModelManager,
    CommittableQuerySet,
    IdentifiableModel,
)


class DmeProductCodeSystem(models.TextChoices):
    """The code system of a DME product's code."""

    HCPCS = "HCPCS", "HCPCS"
    INTERNAL = "INTERNAL", "Internal"


class DmeProduct(IdentifiableModel):
    """A durable medical equipment item on the customer's formulary."""

    class Meta:
        db_table = "canvas_sdk_data_api_dmeproduct_001"

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=32)
    code_system = models.CharField(max_length=16, choices=DmeProductCodeSystem.choices)
    active = models.BooleanField()


class DmeOrder(AuditedModel, IdentifiableModel):
    """A signed Order DME command; the item and patient vitals are snapshotted at commit."""

    class Meta:
        db_table = "canvas_sdk_data_api_dmeorder_001"

    objects = cast(CommittableQuerySet, CommittableModelManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="dme_orders"
    )
    note = models.ForeignKey("v1.Note", on_delete=models.DO_NOTHING, related_name="dme_orders")
    product = models.ForeignKey(
        "v1.DmeProduct", on_delete=models.DO_NOTHING, related_name="orders", null=True
    )
    item_name = models.CharField(max_length=255)
    item_code = models.CharField(max_length=32)
    item_code_system = models.CharField(max_length=16)
    indications = models.JSONField(default=list)
    quantity = models.PositiveIntegerField()
    length_of_need = models.CharField(max_length=255)
    supplier = models.ForeignKey(
        "v1.ServiceProvider", on_delete=models.DO_NOTHING, related_name="dme_orders", null=True
    )
    ordering_provider = models.ForeignKey(
        "v1.Staff", on_delete=models.DO_NOTHING, related_name="dme_orders", null=True
    )
    patient_height = models.CharField(max_length=64)
    patient_weight = models.CharField(max_length=64)


__exports__ = ("DmeOrder", "DmeProduct", "DmeProductCodeSystem")
