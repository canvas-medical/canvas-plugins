from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel


class PluginCommand(IdentifiableModel):
    """A custom command registered by a plugin via customize_custom_command."""

    class Meta:
        db_table = "canvas_sdk_data_plugin_io_plugincommand_001"

    objects: models.Manager["PluginCommand"]

    name = models.CharField(max_length=256, null=False)
    schema_key = models.CharField(max_length=320)
    label = models.CharField(max_length=256, null=True)
    section = models.CharField(max_length=256, null=True)


__exports__ = ("PluginCommand",)
