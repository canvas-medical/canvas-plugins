from django.db import models

from canvas_sdk.v1.data.base import (
    IdentifiableModel,
    TimestampedModel,
)


class ExternalVisit(TimestampedModel, IdentifiableModel):
    """
    External visit record from external data sources (ADT feeds, etc.).

    Groups related ExternalEvent records for a single patient visit.
    """

    class Meta:
        db_table = "canvas_sdk_data_data_integration_externalvisit_001"

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.CASCADE, related_name="patient_visits"
    )
    visit_identifier = models.TextField(unique=True)
    information_source = models.TextField(blank=True, default="")
    facility_name = models.TextField(blank=True, default="")


class ExternalEvent(TimestampedModel, IdentifiableModel):
    """
    External event record from external data sources (ADT feeds, etc.).

    Represents individual events like admission, discharge, transfer within an ExternalVisit.
    """

    class Meta:
        db_table = "canvas_sdk_data_data_integration_externalevent_001"

    external_visit = models.ForeignKey(
        ExternalVisit, on_delete=models.CASCADE, related_name="visit_events"
    )
    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.CASCADE, related_name="patient_events"
    )
    message_control_id = models.TextField(blank=True)
    message_datetime = models.DateTimeField(default=None, null=True)
    event_type = models.TextField(blank=True, default="")
    event_datetime = models.DateTimeField(default=None, null=True)
    event_cancelation_datetime = models.DateTimeField(default=None, null=True)
    raw_message = models.TextField(default="", blank=True)

    @property
    def cancelled(self) -> bool:
        """Return True if this event has been cancelled."""
        return self.event_cancelation_datetime is not None


__exports__ = (
    "ExternalEvent",
    "ExternalVisit",
)
