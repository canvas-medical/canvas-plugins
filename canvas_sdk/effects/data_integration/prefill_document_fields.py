from typing import Any, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect

Annotation: TypeAlias = dict[str, str]
FieldData: TypeAlias = dict[str, Any]
TemplateFields: TypeAlias = dict[str, FieldData]


class PrefillTemplate(BaseModel):
    """A template with fields to prefill."""

    model_config = ConfigDict(populate_by_name=True)

    template_id: int = Field(alias="templateId")
    template_name: str = Field(alias="templateName")
    fields: TemplateFields

    @model_validator(mode="after")
    def validate_template(self) -> "PrefillTemplate":
        """Validate template fields."""
        if not self.template_name or not self.template_name.strip():
            raise ValueError("templateName must be a non-empty string")
        return self


class PrefillDocumentFields(_BaseEffect):
    """
    An Effect that creates or updates an IntegrationTaskPrefill record
    with field_type=REPORT_TYPE for a document in the Data Integration queue.

    When processed by the home-app interpreter, this effect will:
    - Validate the document exists (IntegrationTask)
    - Validate template IDs exist in the practice
    - Create/update IntegrationTaskPrefill with the provided templates and annotations

    Attributes:
        document_id: The ID of the IntegrationTask document (required, non-empty).
        templates: List of templates with fields to prefill (required, non-empty).
        annotations: Optional top-level annotations for the report_type prefill.
    """

    class Meta:
        effect_type = EffectType.UPDATE_DOCUMENT_FIELDS
        apply_required_fields = ("document_id", "templates")

    document_id: str | None = None
    templates: list[dict[str, Any]] | None = None
    annotations: list[Annotation] | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The effect's values to be sent in the payload."""
        result: dict[str, Any] = {
            "document_id": str(self.document_id).strip() if self.document_id else None,
            "templates": self._serialize_templates(),
        }
        if self.annotations is not None:
            result["annotations"] = self.annotations
        return result

    def _serialize_templates(self) -> list[dict[str, Any]]:
        """Serialize templates for payload."""
        if not self.templates:
            return []
        return self.templates

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """Validate the effect fields and return any error details."""
        errors = super()._get_error_details(method)

        # Validate document_id is non-empty if provided
        if self.document_id is not None and not str(self.document_id).strip():
            errors.append(
                self._create_error_detail(
                    "value_error",
                    "document_id must be a non-empty string",
                    self.document_id,
                )
            )

        # Validate templates is non-empty list
        if self.templates is not None and len(self.templates) == 0:
            errors.append(
                self._create_error_detail(
                    "value_error",
                    "templates must be a non-empty list",
                    self.templates,
                )
            )

        # Validate each template structure
        if self.templates:
            for i, template in enumerate(self.templates):
                errors.extend(self._validate_template(template, i))

        # Validate top-level annotations
        if self.annotations:
            for i, annotation in enumerate(self.annotations):
                errors.extend(self._validate_annotation(annotation, f"annotations[{i}]"))

        return errors

    def _validate_template(self, template: dict[str, Any], index: int) -> list[InitErrorDetails]:
        """Validate a single template structure."""
        errors: list[InitErrorDetails] = []
        prefix = f"templates[{index}]"

        # Check templateId
        if "templateId" not in template:
            errors.append(
                self._create_error_detail(
                    "value_error",
                    f"{prefix}.templateId is required",
                    template,
                )
            )

        # Check templateName
        if "templateName" not in template:
            errors.append(
                self._create_error_detail(
                    "value_error",
                    f"{prefix}.templateName is required",
                    template,
                )
            )
        elif not template.get("templateName", "").strip():
            errors.append(
                self._create_error_detail(
                    "value_error",
                    f"{prefix}.templateName must be a non-empty string",
                    template.get("templateName"),
                )
            )

        # Check fields
        fields = template.get("fields", {})
        if isinstance(fields, dict):
            for field_key, field_data in fields.items():
                field_path = f"{prefix}.fields.{field_key}"
                if not isinstance(field_data, dict):
                    errors.append(
                        self._create_error_detail(
                            "value_error",
                            f"{field_path} must be a dict",
                            field_data,
                        )
                    )
                    continue
                errors.extend(self._validate_field(field_data, field_path))

        return errors

    def _validate_field(self, field_data: dict[str, Any], path: str) -> list[InitErrorDetails]:
        """Validate a single field structure."""
        errors: list[InitErrorDetails] = []

        # Check value key exists
        if "value" not in field_data:
            errors.append(
                self._create_error_detail(
                    "value_error",
                    f"{path}.value is required",
                    field_data,
                )
            )

        # Validate field-level annotations
        if "annotations" in field_data and field_data["annotations"]:
            for i, annotation in enumerate(field_data["annotations"]):
                annotation_path = f"{path}.annotations[{i}]"
                if not isinstance(annotation, dict):
                    errors.append(
                        self._create_error_detail(
                            "value_error",
                            f"{annotation_path} must be a dict with text and color",
                            annotation,
                        )
                    )
                    continue
                errors.extend(self._validate_annotation(annotation, annotation_path))

        return errors

    def _validate_annotation(self, annotation: dict[str, Any], path: str) -> list[InitErrorDetails]:
        """Validate a single annotation structure."""
        errors: list[InitErrorDetails] = []

        if "text" not in annotation:
            errors.append(
                self._create_error_detail(
                    "value_error",
                    f"{path}.text is required",
                    annotation,
                )
            )

        if "color" not in annotation:
            errors.append(
                self._create_error_detail(
                    "value_error",
                    f"{path}.color is required",
                    annotation,
                )
            )

        return errors


__exports__ = ("PrefillDocumentFields",)
