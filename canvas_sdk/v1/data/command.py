from django.apps import apps
from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel


class Command(IdentifiableModel):
    """Command."""

    class Meta:
        db_table = "canvas_sdk_data_commands_command_001"

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
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
    origination_source = models.CharField(max_length=20)
    anchor_object_type = models.CharField(max_length=100)
    anchor_object_dbid = models.BigIntegerField()

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


__exports__ = ("Command",)
