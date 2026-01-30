from typing import Self

from django.db import models

from canvas_sdk.v1.data.base import BaseQuerySet, IdentifiableModel, Model


class SpecialtyReportTemplateQuerySet(BaseQuerySet):
    """QuerySet for SpecialtyReportTemplate with filtering methods."""

    def active(self) -> Self:
        """Return a queryset that filters for active templates."""
        return self.filter(active=True)

    def search(self, query: str) -> Self:
        """Perform full-text search using the search_keywords field."""
        return self.filter(search_keywords__icontains=query)

    def custom(self) -> Self:
        """Return a queryset that filters for custom templates."""
        return self.filter(custom=True)

    def builtin(self) -> Self:
        """Return a queryset that filters for built-in templates."""
        return self.filter(custom=False)

    def by_specialty(self, specialty_code: str) -> Self:
        """Filter templates by specialty taxonomy code."""
        return self.filter(specialty_code=specialty_code)


class SpecialtyReportTemplate(IdentifiableModel):
    """Model for specialty report templates used for LLM-powered specialty/referral report parsing."""

    class Meta:
        db_table = "canvas_sdk_data_data_integration_specialtyreporttemplate_001"
        managed = False

    objects = models.Manager.from_queryset(SpecialtyReportTemplateQuerySet)()

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    code_system = models.CharField(max_length=255)
    search_keywords = models.CharField(max_length=500)
    active = models.BooleanField()
    custom = models.BooleanField()
    search_as = models.CharField(max_length=255)
    specialty_name = models.CharField(max_length=255)
    specialty_code = models.CharField(max_length=255)
    specialty_code_system = models.CharField(max_length=255)


class SpecialtyReportTemplateField(Model):
    """Model for field definitions within a specialty report template."""

    class Meta:
        db_table = "canvas_sdk_data_data_integration_specialtyrpttmplfield_001"
        managed = False

    report_template = models.ForeignKey(
        SpecialtyReportTemplate,
        on_delete=models.DO_NOTHING,
        related_name="fields",
        db_column="report_template_id",
        to_field="dbid",
    )
    sequence = models.IntegerField()
    code = models.CharField(max_length=255, null=True, blank=True)
    code_system = models.CharField(max_length=255)
    label = models.CharField(max_length=255)
    units = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=50)
    required = models.BooleanField()


class SpecialtyReportTemplateFieldOption(Model):
    """Model for options for select/radio/checkbox fields in specialty report templates."""

    class Meta:
        db_table = "canvas_sdk_data_data_integration_specialtyrpttmplfieldopt_001"
        managed = False

    field = models.ForeignKey(
        SpecialtyReportTemplateField,
        on_delete=models.DO_NOTHING,
        related_name="options",
        db_column="field_id",
        to_field="dbid",
    )
    label = models.CharField(max_length=255)
    key = models.CharField(max_length=255)


__exports__ = (
    "SpecialtyReportTemplate",
    "SpecialtyReportTemplateField",
    "SpecialtyReportTemplateFieldOption",
)
