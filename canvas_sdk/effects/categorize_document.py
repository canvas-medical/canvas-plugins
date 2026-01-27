from collections.abc import Mapping
from typing import Any

from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect
from canvas_sdk.effects.data_integration.constants import VALID_REPORT_TYPES, VALID_TEMPLATE_TYPES
from canvas_sdk.effects.data_integration.types import AnnotationItem, DocumentType


class CategorizeDocument(_BaseEffect):
    """
    An Effect that categorizes a document in the Data Integration queue into a specific document type.

    When processed by the home-app interpreter, this effect will:
    - Validate the IntegrationTask exists
    - Look up the DocumentType by key (falls back to name if key not found)
    - Validate the DocumentType exists
    - Create or update an IntegrationTaskReview with template_name and document_key

    Attributes:
        document_id: The ID of the IntegrationTask document to categorize (required, non-empty).
            Accepts str or int; always serialized as string in the payload.
        document_type: Document type information dict with required fields: key, name, report_type, template_type.
        annotations: Optional list of annotations for UI display.
        source_protocol: Optional protocol/plugin identifier for tracking.
    """

    class Meta:
        effect_type = EffectType.CATEGORIZE_DOCUMENT
        apply_required_fields = ("document_id", "document_type")

    document_id: str | int | None = None
    document_type: DocumentType | dict[str, Any] | None = None
    annotations: list[AnnotationItem] | None = None
    source_protocol: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The effect's values to be sent in the payload."""
        result: dict[str, Any] = {
            "document_id": str(self.document_id) if self.document_id is not None else None,
            "document_type": self.document_type,
        }

        if self.annotations is not None:
            result["annotations"] = self.annotations
        if self.source_protocol is not None:
            result["source_protocol"] = self.source_protocol

        return result

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return self.values

    def _validate_required_string(
        self,
        data: Mapping[str, Any],
        field: str,
        errors: list[InitErrorDetails],
    ) -> None:
        """Validate that a required string field exists and is non-empty."""
        prefix = "document_type"
        if field not in data:
            errors.append(
                self._create_error_detail("missing", f"{prefix}.{field} is required", None)
            )
        elif not isinstance(data[field], str) or not data[field].strip():
            errors.append(
                self._create_error_detail(
                    "value", f"{prefix}.{field} must be a non-empty string", data.get(field)
                )
            )

    def _validate_enum_field(
        self,
        data: Mapping[str, Any],
        field: str,
        valid_values: frozenset[str],
        errors: list[InitErrorDetails],
        *,
        required: bool = True,
        nullable: bool = False,
    ) -> None:
        """Validate that a field has a value from a set of valid options."""
        prefix = "document_type"
        if field not in data:
            if required:
                errors.append(
                    self._create_error_detail("missing", f"{prefix}.{field} is required", None)
                )
            return

        value = data[field]
        if nullable and value is None:
            return

        null_suffix = " or null" if nullable else ""
        if not isinstance(value, str):
            errors.append(
                self._create_error_detail(
                    "value", f"{prefix}.{field} must be a string{null_suffix}", value
                )
            )
        elif value not in valid_values:
            errors.append(
                self._create_error_detail(
                    "value",
                    f"{prefix}.{field} must be one of {sorted(valid_values)}{null_suffix}, got: {value}",
                    value,
                )
            )

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """Validate the effect fields and return any error details."""
        errors = super()._get_error_details(method)

        if self.document_type is not None:
            self._validate_required_string(self.document_type, "key", errors)
            self._validate_required_string(self.document_type, "name", errors)
            self._validate_enum_field(self.document_type, "report_type", VALID_REPORT_TYPES, errors)
            self._validate_enum_field(
                self.document_type,
                "template_type",
                VALID_TEMPLATE_TYPES,
                errors,
                required=False,
                nullable=True,
            )

        return errors


__exports__ = (
    "AnnotationItem",
    "DocumentType",
    "CategorizeDocument",
)
