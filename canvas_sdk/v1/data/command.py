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
    originator = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    committer = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    entered_in_error = models.ForeignKey(CanvasUser, on_delete=models.DO_NOTHING)
    state = models.CharField()
    patient = models.ForeignKey(Patient, on_delete=models.DO_NOTHING)
    note_id = models.BigIntegerField()
    schema_key = models.TextField()
    data = models.JSONField()
    origination_source = models.CharField()
