from typing import TypeAlias

from django.db import models

from canvas_sdk.v1.data.base import (
    BaseQuerySet,
    ForPatientQuerySetMixin,
    IdentifiableModel,
    Model,
    TimestampedModel,
)
from canvas_sdk.v1.data.coding import Coding
from canvas_sdk.v1.data.django_content_type import resolve_content_object
from canvas_sdk.v1.data.imaging import ImagingOrder
from canvas_sdk.v1.data.lab import LabOrder
from canvas_sdk.v1.data.procedure import Procedure
from canvas_sdk.v1.data.referral import Referral

RequestedService: TypeAlias = ImagingOrder | LabOrder | Referral | Procedure

# The SDK model for each content type a service request wraps, keyed by (app_label, model).
_REQUESTED_SERVICE_MODELS: dict[tuple[str, str], type[RequestedService]] = {
    ("api", "imagingorder"): ImagingOrder,
    ("api", "laborder"): LabOrder,
    ("api", "referral"): Referral,
    ("api", "procedure"): Procedure,
}


class ServiceRequestStatus(models.TextChoices):
    """Status choices for ServiceRequest."""

    DRAFT = "draft", "Draft"
    ACTIVE = "active", "Active"
    COMPLETED = "completed", "Completed"
    ENTERED_IN_ERROR = "entered-in-error", "Entered in Error"


class ServiceRequestQuerySet(ForPatientQuerySetMixin, BaseQuerySet):
    """QuerySet for ServiceRequest."""


class ServiceRequest(TimestampedModel, IdentifiableModel):
    """The FHIR ServiceRequest wrapping an imaging order, lab order, referral, or procedure."""

    class Meta:
        db_table = "canvas_sdk_data_api_servicerequest_001"

    objects = ServiceRequestQuerySet.as_manager()

    status = models.CharField(
        choices=ServiceRequestStatus.choices,
        max_length=20,
        default=ServiceRequestStatus.ACTIVE,
    )
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="service_requests"
    )
    requester = models.ForeignKey(
        "v1.Staff", on_delete=models.DO_NOTHING, related_name="service_requests", null=True
    )
    authored_on = models.DateTimeField(null=True)
    occurrence_period_start = models.DateTimeField(null=True)
    occurrence_period_end = models.DateTimeField(null=True)

    # requested_service_type + requested_service_object_id form a generic link to the order
    requested_service_type = models.ForeignKey(
        "v1.ContentType", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )
    requested_service_object_id = models.IntegerField(null=True)

    conditions = models.ManyToManyField(
        "v1.Condition",
        through="v1.ServiceRequestReasonCondition",
        related_name="service_requests",
    )

    def __str__(self) -> str:
        return f"ServiceRequest(id={self.id})"

    @property
    def requested_service(self) -> RequestedService | None:
        """The imaging order, lab order, referral, or procedure this service request wraps.

        Returns None when the service request is unlinked, when the content type has no SDK
        model, and when the order is soft-deleted, so a deleted order reads the same as no
        order. Each access queries the content type and then the order; when looping over
        service requests, use ``select_related("requested_service_type")`` to skip the first.
        """
        return resolve_content_object(
            _REQUESTED_SERVICE_MODELS,
            self.requested_service_type,
            self.requested_service_object_id,
        )


class ServiceRequestCategoryCoding(Coding):
    """A category coding (imaging, lab, referral, procedure) of a ServiceRequest."""

    class Meta:
        db_table = "canvas_sdk_data_api_servicerequestcategorycoding_001"

    service_request = models.ForeignKey(
        ServiceRequest, on_delete=models.DO_NOTHING, related_name="category_codings"
    )


class ServiceRequestCoding(Coding):
    """A coding of the service a ServiceRequest asks for."""

    class Meta:
        db_table = "canvas_sdk_data_api_servicerequestcoding_001"

    service_request = models.ForeignKey(
        ServiceRequest, on_delete=models.DO_NOTHING, related_name="codings"
    )


class ServiceRequestReasonCondition(Model):
    """A condition given as the reason for a ServiceRequest."""

    class Meta:
        db_table = "canvas_sdk_data_api_servicerequestreasoncondition_001"

    service_request = models.ForeignKey(
        ServiceRequest, on_delete=models.DO_NOTHING, related_name="reason_conditions"
    )
    condition = models.ForeignKey(
        "v1.Condition", on_delete=models.DO_NOTHING, related_name="service_request_reasons"
    )


__exports__ = (
    "ServiceRequest",
    "ServiceRequestCategoryCoding",
    "ServiceRequestCoding",
    "ServiceRequestReasonCondition",
    "ServiceRequestStatus",
)
