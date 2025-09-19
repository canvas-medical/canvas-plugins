from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel


class MedicationStatement(IdentifiableModel):
    """MedicationStatement."""

    class Meta:
        db_table = "canvas_sdk_data_api_medicationstatement_001"

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="medication_statements"
    )
    note = models.ForeignKey(
        "v1.Note", on_delete=models.DO_NOTHING, related_name="medication_statements"
    )
    medication = models.ForeignKey(
        "v1.Medication",
        on_delete=models.DO_NOTHING,
        related_name="medication_statements",
        null=True,
    )
    indications = models.ManyToManyField(
        "v1.Assessment",
        related_name="treatments_stated",
        db_table="canvas_sdk_data_api_medicationstatement_indications_001",
    )
    entered_in_error = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, related_name="+", null=True
    )
    committer = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, related_name="+", null=True
    )
    originator = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, related_name="+")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    start_date_original_input = models.CharField(max_length=255, default="")
    start_date = models.DateField(default=None, null=True)
    end_date_original_input = models.CharField(max_length=255, default="")
    end_date = models.DateField(default=None, null=True)
    dose_quantity = models.FloatField(null=True)
    dose_form = models.CharField(max_length=255, default="")
    dose_route = models.CharField(max_length=255, default="")
    dose_frequency = models.FloatField(null=True)
    dose_frequency_interval = models.CharField(max_length=255, default="")
    sig_original_input = models.CharField(max_length=255, default="")


__exports__ = ("MedicationStatement",)
