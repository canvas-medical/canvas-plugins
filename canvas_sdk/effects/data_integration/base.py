from uuid import UUID

from pydantic import ConfigDict

from canvas_sdk.effects.base import _BaseEffect
from canvas_sdk.effects.data_integration.types import AnnotationItem


class _BaseDocumentEffect(_BaseEffect):
    """Base class for data integration effects that operate on documents.

    Provides `document_id` (required UUID; UUID strings are accepted) and strips
    whitespace from all string fields. Subclasses set `Meta.effect_type` and
    override `values` to add their own fields.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    document_id: UUID | str


class _PrefillingDocumentEffect(_BaseDocumentEffect):
    """Document effect that creates an IntegrationTaskPrefill record.

    Adds optional `annotations` (UI display) and `source_protocol` (audit tag)
    that the interpreter writes onto the prefill record. Effects that only
    mutate the task itself (e.g. status, patient link) should inherit from
    `_BaseDocumentEffect` directly so they don't expose fields the interpreter
    would ignore.
    """

    annotations: list[AnnotationItem] | None = None
    source_protocol: str | None = None


__exports__ = ()
