from typing import Self, cast

from django.db import models
from django.db.models import Exists, OuterRef

from canvas_sdk.v1.data.base import (
    BaseQuerySet,
    ForPatientQuerySetMixin,
    IdentifiableModel,
    TimestampedModel,
)
from canvas_sdk.v1.data.coding import Coding
from canvas_sdk.v1.data.prescription import Prescription, PrescriptionStatus


class RefillRequestQuerySet(ForPatientQuerySetMixin, BaseQuerySet):
    """RefillRequestQuerySet."""

    def pending(self) -> Self:
        """Requests in the refill queue: not ignored, and not answered by a sent response.

        A sent response answers its request unless it failed to reach the pharmacy or was entered
        in error, so a request whose only responses are unsent, failed or entered in error stays
        in the queue.
        """
        answering = (
            Prescription.objects.committed()
            .filter(refill_request=OuterRef("pk"))
            .exclude(status=PrescriptionStatus.ERROR)
        )
        return self.exclude(ignored=True).exclude(Exists(answering))


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
