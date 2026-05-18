from typing import Annotated, Any, NotRequired, TypeAlias

from pydantic import Field
from typing_extensions import TypedDict

from canvas_sdk.effects.base import EffectType
from canvas_sdk.effects.data_integration.base import _PrefillingDocumentEffect
from canvas_sdk.effects.data_integration.types import AnnotationItem, NonEmptyStr


class PrefillDocumentFieldData(TypedDict):
    """
    Field data for a prefill template field.

    Attributes:
        value: The field value (required)
        unit: The unit of measurement
        reference_range: The reference range for the value
        abnormal: Whether the value is abnormal
        annotations: List of annotations for the field
    """

    value: str
    unit: NotRequired[str]
    reference_range: NotRequired[str]
    abnormal: NotRequired[bool]
    annotations: NotRequired[list[AnnotationItem]]


TemplateFields: TypeAlias = dict[str, PrefillDocumentFieldData]


class PrefillTemplate(TypedDict):
    """A template with fields to prefill."""

    template_id: int
    template_name: NonEmptyStr
    fields: TemplateFields


class PrefillDocumentFields(_PrefillingDocumentEffect):
    """Creates or updates an IntegrationTaskPrefill record with field_type=REPORT_TYPE.

    When processed, this effect will:
    - Validate the IntegrationTask exists
    - Validate template IDs exist in the practice
    - Create/update IntegrationTaskPrefill with the provided templates and annotations
    """

    class Meta:
        effect_type = EffectType.UPDATE_DOCUMENT_FIELDS

    templates: Annotated[list[PrefillTemplate], Field(min_length=1)]

    @property
    def values(self) -> dict[str, Any]:
        """The effect's values to be sent in the payload."""
        return {
            "document_id": str(self.document_id),
            "templates": self.templates,
            "annotations": self.annotations,
            "source_protocol": self.source_protocol,
        }


__exports__ = ("PrefillDocumentFieldData", "PrefillDocumentFields", "PrefillTemplate")
