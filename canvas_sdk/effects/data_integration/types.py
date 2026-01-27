from typing import TypedDict


class AnnotationItem(TypedDict):
    """
    Annotation item with text and color for UI display.

    Attributes:
        text: The annotation label (e.g., "AI 97%", "Auto-detected")
        color: Hex color code (e.g., "#FF0000" for red)
    """

    text: str
    color: str

class DocumentType(TypedDict):
    """
    Document type information for categorizing a document.

    Attributes:
        key: The unique key identifying the document type (required, non-empty string)
        name: The human-readable name of the document type (required, non-empty string)
        report_type: The type of report, must be "CLINICAL" or "ADMINISTRATIVE" (required)
        template_type: The template type, can be "LabReportTemplate", "ImagingReportTemplate",
            "SpecialtyReportTemplate", or null for administrative docs (optional)
    """

    key: str
    name: str
    report_type: str
    template_type: str | None


__exports__ = ("AnnotationItem", "DocumentType")
