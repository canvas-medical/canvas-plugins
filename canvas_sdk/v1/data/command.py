from django.db import models


class Command(models.Model):
    """Command."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_commands_command_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    originator = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, null=True)
    committer = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, null=True)
    entered_in_error = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, null=True)
    state = models.CharField()
    patient = models.ForeignKey("v1.Patient", on_delete=models.DO_NOTHING, null=True)
    note_id = models.BigIntegerField()
    schema_key = models.TextField()
    data = models.JSONField()
    origination_source = models.CharField()
