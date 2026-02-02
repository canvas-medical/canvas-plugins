from django.db import models

from canvas_sdk.v1.data.base import AuditedModel, TimestampedModel
from canvas_sdk.v1.data.utils import presigned_url


class Snapshot(AuditedModel):
    """Snapshot model used to capture images via the iOS application."""

    class Meta:
        db_table = "canvas_sdk_data_api_snapshot_001"

    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"Snapshot(dbid={self.dbid}, title={self.title})"


class SnapshotImage(TimestampedModel):
    """SnapshotImage model for individual images within a Snapshot."""

    class Meta:
        db_table = "canvas_sdk_data_api_snapshotimage_001"

    snapshot = models.ForeignKey(Snapshot, on_delete=models.DO_NOTHING, related_name="images")
    image = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255)
    instruction = models.CharField(max_length=255)
    tag = models.CharField(max_length=25)

    def __str__(self) -> str:
        return f"SnapshotImage(dbid={self.dbid}, title={self.title}, tag={self.tag})"

    @property
    def image_url(self) -> str | None:
        """
        Return a presigned URL for accessing the image.

        Returns the presigned S3 URL if an image file exists,
        otherwise returns None.
        """
        if self.image:
            return presigned_url(self.image)
        return None


__exports__ = (
    "Snapshot",
    "SnapshotImage",
)
