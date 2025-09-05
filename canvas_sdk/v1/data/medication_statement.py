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
    )
    indications = models.ManyToManyField(
        "v1.Assessment",
        related_name="treatments_stated",
        db_table="canvas_sdk_data_api_medicationstatement_indications_001",
    )
    entered_in_error = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, related_name="+"
    )
    committer = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, related_name="+")
    originator = models.ForeignKey("v1.CanvasUser", on_delete=models.DO_NOTHING, related_name="+")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    start_date_original_input = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date_original_input = models.CharField(max_length=255)
    end_date = models.DateField()
    dose_quantity = models.FloatField()
    dose_form = models.CharField(max_length=255)
    dose_route = models.CharField(max_length=255)
    dose_frequency = models.FloatField()
    dose_frequency_interval = models.CharField(max_length=255)
    sig_original_input = models.CharField(max_length=255)


__exports__ = ("MedicationStatement",)
