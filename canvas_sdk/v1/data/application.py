from django.db import models


class Application(models.Model):
    """Plugin Application."""

    class Meta:
        db_table = "canvas_sdk_data_plugin_io_application_001"

    identifier = models.CharField(max_length=512, primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    name = models.TextField(null=False, max_length=32)
    description = models.TextField(null=False, max_length=256)


__exports__ = ("Application",)
