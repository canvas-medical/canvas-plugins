from django.apps import apps
from django.db import models

from canvas_sdk.v1.data.patient import Patient
from canvas_sdk.v1.data.user import CanvasUser


class Command(models.Model):
    """Command."""

    class Meta:
        managed = False
        app_label = "canvas_sdk"
        db_table = "canvas_sdk_data_commands_command_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    originator = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING, null=True)
    committer = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING, null=True)
    entered_in_error = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING, null=True)
    state = models.CharField()
    patient = models.ForeignKey(Patient, on_delete=models.DO_NOTHING, null=True)
    note_id = models.BigIntegerField()
    schema_key = models.TextField()
    data = models.JSONField()
    origination_source = models.CharField()
    anchor_object_type = models.CharField()
    anchor_object_dbid = models.BigIntegerField()

    @property
    def anchor_object(self) -> models.Model | None:
        """
        Use the anchor_object_type and anchor_object_dbid to get the anchor object for the command.
        """
        # TODO: Is the anchor object type enough here, or do we need a mapping? The home-app model
        #  names might not exactly match the plugins model names.
        anchor_model = apps.get_model(app_label="canvas_sdk", model_name=self.anchor_object_type)
        return anchor_model.objects.get(dbid=self.anchor_object_dbid)
