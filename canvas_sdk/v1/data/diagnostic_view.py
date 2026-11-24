from django.db import models

from canvas_sdk.v1.data.base import IdentifiableModel, TimestampedModel


class DiagnosticView(TimestampedModel, IdentifiableModel):
    """A configured combination of lab tests / questionnaire codes whose
    timeseries can be embedded in a Reference command.
    """

    class Meta:
        db_table = "canvas_sdk_data_api_diagnosticview_001"

    originator = models.ForeignKey("v1.CanvasUser", on_delete=models.CASCADE, related_name="+")
    name = models.CharField(max_length=100)
    tags = models.CharField("Search tags", max_length=500, default="", blank=True)


class DiagnosticViewElementDataType(models.TextChoices):
    """The kind of value a diagnostic view element reads."""

    LAB_VALUE = "LabValue", "lab value"
    QUESTIONNAIRE_SCORE = "QuestionnaireScore", "questionnaire score"


class DiagnosticViewElementCodingSystem(models.TextChoices):
    """The coding system of a diagnostic view element's code."""

    LOINC = "loinc", "loinc"
    SNOMED = "snomed", "snomed"
    ICD10 = "icd-10", "icd-10"
    CPT = "cpt", "cpt"
    CANVAS = "canvas", "canvas"
    INTERNAL = "internal", "internal"


class DiagnosticViewElement(TimestampedModel):
    """A lab test or questionnaire score shown as one row of a DiagnosticView."""

    class Meta:
        db_table = "canvas_sdk_data_api_diagnosticviewelement_001"

    view = models.ForeignKey(DiagnosticView, on_delete=models.CASCADE, related_name="elements")
    data_type = models.CharField(max_length=100, choices=DiagnosticViewElementDataType.choices)
    system = models.CharField(max_length=20, choices=DiagnosticViewElementCodingSystem.choices)
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    units = models.CharField(max_length=30, default="", blank=True)
    ordering = models.IntegerField(default=0)


__exports__ = (
    "DiagnosticView",
    "DiagnosticViewElement",
    "DiagnosticViewElementCodingSystem",
    "DiagnosticViewElementDataType",
)
