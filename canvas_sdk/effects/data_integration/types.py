from enum import StrEnum
from typing import Annotated, TypedDict

from pydantic import StringConstraints

NonEmptyStr = Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]


class ReportType(StrEnum):
    """The category of report for a document type."""

    CLINICAL = "CLINICAL"
    ADMINISTRATIVE = "ADMINISTRATIVE"


class TemplateType(StrEnum):
    """The template applied to a clinical report document."""

    LAB_REPORT = "LabReportTemplate"
    IMAGING_REPORT = "ImagingReportTemplate"
    SPECIALTY_REPORT = "SpecialtyReportTemplate"


class AnnotationItem(TypedDict):
    """UI annotation: `text` is the label (e.g., "AI 97%"); `color` is a hex code (e.g., "#FF0000")."""

    text: str
    color: str


class DocumentType(TypedDict):
    """Document type information for categorizing a document.

    `template_type` is None for administrative documents.
    """

    key: NonEmptyStr
    name: NonEmptyStr
    report_type: ReportType
    template_type: TemplateType | None


__exports__ = ("AnnotationItem", "DocumentType", "ReportType", "TemplateType")
