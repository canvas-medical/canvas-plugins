from typing import Self

from django.db import models

from canvas_sdk.v1.data.base import BaseQuerySet, IdentifiableModel, Model


class BaseReportTemplateQuerySet(BaseQuerySet):
    """Base QuerySet with shared filtering methods for report templates."""

    def active(self) -> Self:
        """Filter to active templates."""
        return self.filter(active=True)

    def custom(self) -> Self:
        """Filter to custom (user-created) templates."""
        return self.filter(custom=True)

    def builtin(self) -> Self:
        """Filter to built-in (system) templates."""
        return self.filter(custom=False)


class BaseReportTemplate(IdentifiableModel):
    """Abstract base model for report templates."""

    class Meta:
        abstract = True

    name = models.CharField(max_length=250)
    code = models.CharField(max_length=50, blank=True, default="")
    code_system = models.CharField(max_length=50, blank=True, default="")
    search_keywords = models.CharField(max_length=500, blank=True, default="")
    active = models.BooleanField(default=True)
    custom = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class BaseReportTemplateField(Model):
    """Abstract base model for report template fields."""

    class Meta:
        abstract = True

    sequence = models.IntegerField(default=1)
    code = models.CharField(max_length=50, blank=True, null=True)
    code_system = models.CharField(max_length=50, blank=True, default="")
    label = models.CharField(max_length=250)
    units = models.CharField(max_length=50, blank=True, null=True)
    type = models.CharField(max_length=250)
    required = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.label


class BaseReportTemplateFieldOption(Model):
    """Abstract base model for report template field options."""

    class Meta:
        abstract = True

    label = models.CharField(max_length=250)
    key = models.CharField(max_length=250)

    def __str__(self) -> str:
        return f"{self.label} ({self.key})"


__exports__ = (
    "BaseReportTemplateQuerySet",
    "BaseReportTemplate",
    "BaseReportTemplateField",
    "BaseReportTemplateFieldOption",
)
