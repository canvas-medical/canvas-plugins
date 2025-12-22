from typing import Self

from django.db import models
from django.db.models import Q

from canvas_sdk.v1.data.base import Model


class FieldType(models.TextChoices):
    """Choices for lab report template field types."""

    FLOAT = "float", "Float"
    SELECT = "select", "Select"
    TEXT = "text", "Text"
    CHECKBOX = "checkbox", "Checkbox"
    RADIO = "radio", "Radio"
    ARRAY = "array", "Array"
    LAB_REPORT = "labReport", "Lab Report"
    REMOTE_FIELDS = "remoteFields", "Remote Fields"
    AUTOCOMPLETE = "autocomplete", "Autocomplete"
    DATE = "date", "Date"


class LabReportTemplateQuerySet(models.QuerySet):
    """QuerySet for LabReportTemplate with custom filtering methods."""

    def active(self) -> Self:
        """Return templates that are active."""
        return self.filter(active=True)

    def inactive(self) -> Self:
        """Return templates that are inactive."""
        return self.filter(active=False)

    def search(self, query: str) -> Self:
        """Search templates by name or search_keywords."""
        if not query:
            return self
        return self.filter(
            Q(name__icontains=query) | Q(search_keywords__icontains=query)
        )

    def point_of_care(self) -> Self:
        """Return Point of Care (POC) test templates."""
        return self.filter(poc=True)

    def custom(self) -> Self:
        """Return custom (user-created) templates."""
        return self.filter(custom=True)

    def builtin(self) -> Self:
        """Return built-in (system) templates."""
        return self.filter(custom=False)


class LabReportTemplate(Model):
    """A lab report template for POC labs and custom lab reports."""

    class Meta:
        db_table = "canvas_sdk_data_data_integration_labreporttemplate_001"

    objects = models.Manager.from_queryset(LabReportTemplateQuerySet)()

    name = models.CharField(max_length=250)
    code = models.CharField(max_length=50, blank=True, default="")
    code_system = models.CharField(max_length=50, blank=True, default="")
    search_keywords = models.CharField(max_length=500, blank=True, default="")
    active = models.BooleanField(default=True)
    custom = models.BooleanField(default=True)
    poc = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name


class LabReportTemplateField(Model):
    """A field definition within a lab report template."""

    class Meta:
        db_table = "canvas_sdk_data_data_integration_labreporttemplatefield_001"

    report_template = models.ForeignKey(
        LabReportTemplate,
        on_delete=models.DO_NOTHING,
        related_name="fields",
    )
    sequence = models.IntegerField(default=1)
    code = models.CharField(max_length=50, null=True, blank=True)
    code_system = models.CharField(max_length=50, blank=True, default="")
    label = models.CharField(max_length=250)
    units = models.CharField(max_length=50, null=True, blank=True)
    field_type = models.CharField(
        max_length=250,
        choices=FieldType.choices,
        default=FieldType.FLOAT,
        db_column="type",
    )
    required = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.label


class LabReportTemplateFieldOption(Model):
    """An option for a select/radio field in a lab report template."""

    class Meta:
        db_table = "canvas_sdk_data_data_integration_labreporttemplatefieldoption_001"

    field = models.ForeignKey(
        LabReportTemplateField,
        on_delete=models.DO_NOTHING,
        related_name="options",
    )
    label = models.CharField(max_length=250)
    key = models.CharField(max_length=250)

    def __str__(self) -> str:
        return f"{self.label} ({self.key})"


__exports__ = (
    "FieldType",
    "LabReportTemplate",
    "LabReportTemplateField",
    "LabReportTemplateFieldOption",
    "LabReportTemplateQuerySet",
)
