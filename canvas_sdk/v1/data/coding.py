from django.db import models

from canvas_sdk.v1.data.base import Model


class Coding(Model):
    """A representation of a coding from a terminology system."""

    class Meta:
        abstract = True

    code = models.CharField(max_length=255, blank=True, default="")
    display = models.CharField(max_length=1000)
    system = models.CharField(max_length=255)
    version = models.CharField(max_length=255, blank=True, default="")
    user_selected = models.BooleanField(default=False)


__exports__ = ()
