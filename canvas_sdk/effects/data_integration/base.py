from uuid import UUID

from pydantic import ConfigDict

from canvas_sdk.effects.base import _BaseEffect
from canvas_sdk.effects.data_integration.types import AnnotationItem


class _BaseDocumentEffect(_BaseEffect):
    """Base class for data integration effects that operate on documents.

    Provides `document_id` (required UUID; UUID strings are accepted), optional
    `source_protocol` and `annotations`, and strips whitespace from all string fields.
    Subclasses set `Meta.effect_type` and override `values` to add their own fields.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    document_id: UUID | str
    source_protocol: str | None = None
    annotations: list[AnnotationItem] | None = None


__exports__ = ()
