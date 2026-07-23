from typing import cast

from django.db import models

from canvas_sdk.v1.data.base import (
    BaseQuerySet,
    ForPatientQuerySetMixin,
    IdentifiableModel,
    TimestampedModel,
)
from canvas_sdk.v1.data.coding import Coding


class RefillRequestQuerySet(ForPatientQuerySetMixin, BaseQuerySet):
    """RefillRequestQuerySet."""


class RefillRequest(TimestampedModel, IdentifiableModel):
    """RefillRequest."""

    class Meta:
        db_table = "canvas_sdk_data_api_refillrequest_001"

    # Plain Manager (not BaseModelManager): RefillRequest is not an AuditedModel and
    # has no `deleted` column, so BaseModelManager's deleted=False filter would raise
    # FieldError on every query. Mirrors ReferralReport (also TimestampedModel-only).
    objects = cast(RefillRequestQuerySet, models.Manager.from_queryset(RefillRequestQuerySet)())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="refill_requests", null=True
    )
    staff = models.ForeignKey(
        "v1.Staff", on_delete=models.DO_NOTHING, related_name="refill_requests", null=True
    )
    message_id = models.CharField(max_length=35, blank=True, default="")
    ignored = models.BooleanField(default=False)
    content = models.JSONField(default=dict)


class RefillRequestCoding(Coding):
    """RefillRequestCoding."""

    class Meta:
        db_table = "canvas_sdk_data_api_refillrequestcoding_001"

    refill_request = models.ForeignKey(
        RefillRequest, on_delete=models.DO_NOTHING, related_name="codings"
    )


__exports__ = ("RefillRequest", "RefillRequestCoding")
