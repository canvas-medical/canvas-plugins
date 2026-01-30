from typing import Any

from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import _BaseEffect
from canvas_sdk.effects.data_integration.types import AnnotationItem


class _BaseDocumentEffect(_BaseEffect):
    """
    Base class for data integration effects that operate on documents.

    Provides common functionality for:
    - document_id field (required, str|int, serialized as stripped string)
    - Optional source_protocol field
    - Optional annotations field
    - Validation for document_id non-empty
    - Serialization helpers

    Subclasses should:
    - Define their own Meta.effect_type
    - Define Meta.apply_required_fields (typically includes "document_id")
    - Override values() to add additional fields
    - Override _get_error_details() to add field-specific validations
    """

    document_id: str | int | None = None
    source_protocol: str | None = None
    annotations: list[AnnotationItem] | None = None

    def _serialize_document_id(self) -> str | None:
        """Serialize document_id to string with whitespace stripped."""
        return str(self.document_id).strip() if self.document_id is not None else None

    def _serialize_source_protocol(self) -> str | None:
        """Serialize source_protocol with whitespace stripped."""
        return self.source_protocol.strip() if self.source_protocol is not None else None

    def _validate_document_id(self) -> list[InitErrorDetails]:
        """Validate document_id is non-empty if provided as string."""
        errors: list[InitErrorDetails] = []
        if isinstance(self.document_id, str) and not self.document_id.strip():
            errors.append(
                self._create_error_detail(
                    "value_error",
                    "document_id must be a non-empty string",
                    self.document_id,
                )
            )
        return errors

    def _validate_non_empty_string(
        self, field_name: str, field_value: str | None
    ) -> list[InitErrorDetails]:
        """Validate a string field is non-empty if provided."""
        errors: list[InitErrorDetails] = []
        if field_value is not None and not field_value.strip():
            errors.append(
                self._create_error_detail(
                    "value_error",
                    f"{field_name} must be a non-empty string",
                    field_value,
                )
            )
        return errors

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """Validate common fields. Subclasses should extend this."""
        errors = super()._get_error_details(method)
        errors.extend(self._validate_document_id())
        return errors


__exports__ = ("_BaseDocumentEffect",)
