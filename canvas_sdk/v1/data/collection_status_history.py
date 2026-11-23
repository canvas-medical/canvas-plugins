from django.db import models

from canvas_sdk.v1.data.base import TimestampedModel


class CollectionStatus(models.TextChoices):
    """Where a patient's balance is in collections."""

    NONE = "none", "none"
    INTERNAL = "internal", "internal"
    EXTERNAL = "external", "external"


class CollectionStatusHistory(TimestampedModel):
    """A patient's collection status as of a date."""

    class Meta:
        db_table = "canvas_sdk_data_quality_and_revenue_collectionstatushistory_001"

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.CASCADE, related_name="collection_status_histories"
    )
    status = models.CharField(
        max_length=10, choices=CollectionStatus.choices, default=CollectionStatus.NONE
    )
    status_date = models.DateField()


__exports__ = (
    "CollectionStatus",
    "CollectionStatusHistory",
)
