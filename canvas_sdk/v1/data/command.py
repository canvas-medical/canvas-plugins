from django.apps import apps
from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, MetadataModel, Model, TimestampedModel


class Command(TimestampedModel, IdentifiableModel):
    """Command."""

    class Meta:
        db_table = "canvas_sdk_data_commands_command_001"

    originator = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="commands_originated"
    )
    committer = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="commands_committed"
    )
    entered_in_error = models.ForeignKey(
        "v1.CanvasUser",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="commands_entered_in_error",
    )
    state = models.CharField(max_length=20)
    patient = models.ForeignKey("v1.Patient", on_delete=models.DO_NOTHING, null=True)
    note = models.ForeignKey("v1.Note", on_delete=models.DO_NOTHING, related_name="commands")
    schema_key = models.TextField()
    data = models.JSONField()
    custom_html = models.TextField(null=True)
    origination_source = models.CharField(max_length=20)
    anchor_object_type = models.CharField(max_length=100)
    anchor_object_dbid = models.BigIntegerField()
    edited_by = models.ManyToManyField(
        "v1.CanvasUser", related_name="commands_edited", through="v1.CommandEditedBy"
    )

    @property
    def anchor_object(self) -> models.Model | None:
        """
        Use the anchor_object_type and anchor_object_dbid to get the anchor object for the command.
        """
        # TODO: Is the anchor object type enough here, or do we need a mapping? The home-app model
        #  names might not exactly match the plugins model names.
        if not self.anchor_object_type or not self.anchor_object_dbid:
            return None

        anchor_model = apps.get_model(
            app_label=self._meta.app_label, model_name=self.anchor_object_type
        )
        return anchor_model.objects.get(dbid=self.anchor_object_dbid)


class CommandEditedBy(Model):
    """M2M for Command -> CanvasUsers who edited it."""

    class Meta:
        db_table = "canvas_sdk_data_commands_command_edited_by_001"

    command = models.ForeignKey(Command, on_delete=models.DO_NOTHING, related_name="+")
    user = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, related_name="+")


class CommandMetadata(MetadataModel):
    """A class representing Command Metadata."""

    class Meta:
        db_table = "canvas_sdk_data_api_commandmetadata_001"

    command = models.ForeignKey("v1.Command", on_delete=models.CASCADE, related_name="metadata")


__exports__ = ("Command", "CommandEditedBy", "CommandMetadata")
