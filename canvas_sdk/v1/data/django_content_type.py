from django.db import models

from canvas_sdk.v1.data.base import Model


class DjangoContentType(Model):
    """A Django ContentType, exposing the content type id used for generic relations and permalinks."""

    class Meta:
        db_table = "canvas_sdk_data_django_content_type_001"

    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)


__exports__ = ("DjangoContentType",)
