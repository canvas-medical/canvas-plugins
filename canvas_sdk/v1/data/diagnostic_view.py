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


__exports__ = ("DiagnosticView",)
