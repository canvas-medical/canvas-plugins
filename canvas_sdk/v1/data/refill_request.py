from typing import cast

from django.db import models

from canvas_sdk.v1.data.base import (
    BaseModelManager,
    BaseQuerySet,
    ForPatientQuerySetMixin,
    IdentifiableModel,
    TimestampedModel,
)
from canvas_sdk.v1.data.coding import Coding


class RefillRequestQuerySet(ForPatientQuerySetMixin, BaseQuerySet):
    """RefillRequestQuerySet."""


RefillRequestManager = BaseModelManager.from_queryset(RefillRequestQuerySet)


class RefillRequest(TimestampedModel, IdentifiableModel):
    """RefillRequest."""

    class Meta:
        db_table = "canvas_sdk_data_api_refillrequest_001"

    objects = cast(RefillRequestQuerySet, RefillRequestManager())

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
