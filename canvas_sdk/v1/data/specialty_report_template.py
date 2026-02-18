from typing import Self

from django.db import models

from canvas_sdk.v1.data.report_template_base import (
    BaseReportTemplate,
    BaseReportTemplateField,
    BaseReportTemplateFieldOption,
    BaseReportTemplateQuerySet,
)


class SpecialtyReportTemplateQuerySet(BaseReportTemplateQuerySet):
    """QuerySet for SpecialtyReportTemplate with filtering methods."""

    def search(self, query: str) -> Self:
        """Perform full-text search using the search_keywords field."""
        return self.filter(search_keywords__icontains=query)

    def by_specialty(self, specialty_code: str) -> Self:
        """Filter templates by specialty taxonomy code."""
        return self.filter(specialty_code=specialty_code)


class SpecialtyReportTemplate(BaseReportTemplate):
    """Model for specialty report templates used for LLM-powered specialty/referral report parsing."""

    class Meta:
        db_table = "canvas_sdk_data_data_integration_specialtyreporttemplate_001"

    objects = models.Manager.from_queryset(SpecialtyReportTemplateQuerySet)()

    search_as = models.CharField(max_length=255, default="", blank=True)
    specialty_name = models.CharField(max_length=255, default="", blank=True)
    specialty_code = models.CharField(max_length=255, default="", blank=True)
    specialty_code_system = models.CharField(max_length=255, default="", blank=True)


class SpecialtyReportTemplateField(BaseReportTemplateField):
    """Model for field definitions within a specialty report template."""

    class Meta:
        db_table = "canvas_sdk_data_data_integration_specialtyrpttmplfield_001"

    report_template = models.ForeignKey(
        SpecialtyReportTemplate,
        on_delete=models.DO_NOTHING,
        related_name="fields",
    )


class SpecialtyReportTemplateFieldOption(BaseReportTemplateFieldOption):
    """Model for options for select/radio/checkbox fields in specialty report templates."""

    class Meta:
        db_table = "canvas_sdk_data_data_integration_specialtyrpttmplfieldopt_001"

    field = models.ForeignKey(
        SpecialtyReportTemplateField,
        on_delete=models.DO_NOTHING,
        related_name="options",
    )


__exports__ = (
    "SpecialtyReportTemplate",
    "SpecialtyReportTemplateField",
    "SpecialtyReportTemplateFieldOption",
)
