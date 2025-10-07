from django.db import models


class Coding(models.Model):
    """A representation of a coding from a terminology system."""

    class Meta:
        abstract = True

    code = models.CharField(max_length=255, blank=True, default="")
    display = models.CharField(max_length=1000)
    system = models.CharField(max_length=255)
    version = models.CharField(max_length=255, blank=True, default="")
    user_selected = models.BooleanField(default=False)
