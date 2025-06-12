from django.db import models


class Instruction(models.Model):
    """Instruction."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_instruction_001"

    id = models.UUIDField()
    dbid = models.BigIntegerField(primary_key=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    originator = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, null=True)
    deleted = models.BooleanField()
    committer = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, null=True)
    entered_in_error = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING)
    patient = models.ForeignKey(
        "v1.Patient",
        on_delete=models.DO_NOTHING,
        related_name="instructions",
        null=True,
    )
    note = models.ForeignKey(
        "v1.Note", on_delete=models.DO_NOTHING, related_name="instructions", null=True
    )
    narrative = models.CharField()


class InstructionCoding(models.Model):
    """InstructionCoding."""

    class Meta:
        managed = False
        db_table = "canvas_sdk_data_api_instructioncoding_001"

    dbid = models.BigIntegerField(primary_key=True)
    system = models.CharField()
    version = models.CharField()
    code = models.CharField()
    display = models.CharField()
    user_selected = models.BooleanField()
    instruction = models.ForeignKey(
        Instruction, on_delete=models.DO_NOTHING, related_name="coding", null=True
    )


__exports__ = (
    "Instruction",
    "InstructionCoding",
)
