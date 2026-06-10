from django.contrib.postgres.fields import ArrayField
from django.db import models

from canvas_sdk.v1.data.base import AuditedModel, IdentifiableModel


class ChartSectionReviewSection(models.TextChoices):
    """The chart section a ChartSectionReview summarizes."""

    CONDITIONS = "conditions", "Conditions"
    SURGICAL_HISTORY = "surgical_history", "Surgical History"
    MEDICATIONS = "medications", "Medications"
    FAMILY_HISTORIES = "family_histories", "Family Histories"
    ALLERGIES = "allergies", "Allergies"
    IMMUNIZATIONS = "immunizations", "Immunizations"


class ChartSectionReview(AuditedModel, IdentifiableModel):
    """A reviewed chart section captured on a note, with its pre-rendered content."""

    class Meta:
        db_table = "canvas_sdk_data_api_chartsectionreview_001"

    patient = models.ForeignKey(
        "v1.Patient", on_delete=models.DO_NOTHING, related_name="chart_section_reviews"
    )
    note = models.ForeignKey(
        "v1.Note", on_delete=models.DO_NOTHING, related_name="chart_section_reviews"
    )
    section = models.CharField(
        choices=ChartSectionReviewSection.choices, max_length=20, blank=True, default=""
    )
    entries = ArrayField(base_field=models.IntegerField(), default=list, blank=True)
    content = models.TextField(blank=True, default="")


__exports__ = ("ChartSectionReviewSection", "ChartSectionReview")
