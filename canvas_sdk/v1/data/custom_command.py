from typing import TYPE_CHECKING, cast

from django.db import models

from canvas_sdk.v1.data.base import (
    AuditedModel,
    CommittableModelManager,
    CommittableQuerySet,
    IdentifiableModel,
)

if TYPE_CHECKING:
    from canvas_sdk.v1.data.plugin_command import PluginCommand


class CustomCommand(AuditedModel, IdentifiableModel):
    """A Custom Command — the anchor for the custom_command SDK command."""

    class Meta:
        db_table = "canvas_sdk_data_api_customcommand_001"

    objects = cast(CommittableQuerySet, CommittableModelManager())

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="custom_commands"
    )
    note = models.ForeignKey("v1.Note", on_delete=models.DO_NOTHING, related_name="custom_commands")

    @property
    def plugin_command(self) -> "PluginCommand | None":
        """The PluginCommand this anchor was created from, resolved by the command's schema_key."""
        from canvas_sdk.v1.data.command import Command
        from canvas_sdk.v1.data.plugin_command import PluginCommand

        schema_key = (
            Command.objects.filter(
                anchor_object_type=self._meta.model_name,
                anchor_object_dbid=self.dbid,
            )
            .values_list("schema_key", flat=True)
            .first()
        )
        if not schema_key:
            return None

        return PluginCommand.objects.filter(schema_key=schema_key).first()


__exports__ = ("CustomCommand",)
