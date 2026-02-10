import sys
from typing import Any, NotRequired, TypeAlias

if sys.version_info >= (3, 12):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from pydantic import BaseModel, model_validator
from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType
from canvas_sdk.effects.data_integration.base import _BaseDocumentEffect
from canvas_sdk.effects.data_integration.types import AnnotationItem
from logger import log


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


class PrefillTemplate(BaseModel):
    """A template with fields to prefill."""

    template_id: int
    template_name: str
    fields: TemplateFields

    @model_validator(mode="after")
    def validate_template(self) -> "PrefillTemplate":
        """Validate template fields."""
        if not self.template_name or not self.template_name.strip():
            raise ValueError("template_name must be a non-empty string")
        return self


class PrefillDocumentFields(_BaseDocumentEffect):
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

    templates: list[dict[str, Any]] | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The effect's values to be sent in the payload."""
        log.info("[report_type] ========== PrefillDocumentFields.values START ==========")
        log.info(f"[report_type] document_id: {self.document_id!r}")
        log.info(f"[report_type] Number of templates: {len(self.templates) if self.templates else 0}")
        log.info(f"[report_type] CRITICAL: self.source_protocol = {self.source_protocol!r}")
        log.info(f"[report_type] CRITICAL: source_protocol is None? {self.source_protocol is None}")
        log.info(f"[report_type] CRITICAL: source_protocol is empty string? {self.source_protocol == ''}")

        result: dict[str, Any] = {
            "document_id": self._serialize_document_id(),
            "templates": self._serialize_templates(),
        }

        log.info(f"[report_type] Base result created with keys: {list(result.keys())}")

        if self.annotations is not None:
            log.info(f"[report_type] Adding annotations (count: {len(self.annotations)})")
            result["annotations"] = self.annotations
        else:
            log.info("[report_type] Skipping annotations (is None)")

        log.info(f"[report_type] Checking source_protocol condition: source_protocol is not None = {self.source_protocol is not None}")
        if self.source_protocol is not None:
            log.info("[report_type] CALLING _serialize_source_protocol()")
            serialized_protocol = self._serialize_source_protocol()
            log.info(f"[report_type] _serialize_source_protocol() returned: {serialized_protocol!r}")
            result["source_protocol"] = serialized_protocol
            log.info("[report_type] Added source_protocol to result")
        else:
            log.warning("[report_type] SKIPPING source_protocol (self.source_protocol is None)")

        log.info(f"[report_type] Final result keys: {list(result.keys())}")
        log.info(f"[report_type] Final result['source_protocol'] if exists: {result.get('source_protocol', 'KEY_NOT_PRESENT')!r}")
        log.info(f"[report_type] Complete result dict: {result}")
        log.info("[report_type] ========== PrefillDocumentFields.values END ==========")
        return result

    def _serialize_templates(self) -> list[dict[str, Any]]:
        """Serialize templates for payload (field_type=REPORT_TYPE)."""
        log.info("[report_type] _serialize_templates called")
        if not self.templates:
            log.info("[report_type] No templates to serialize")
            return []

        log.info(f"[report_type] Serializing {len(self.templates)} templates")
        for i, template in enumerate(self.templates):
            template_name = template.get("template_name", "unknown")
            template_id = template.get("template_id", "unknown")
            field_count = len(template.get("fields", {})) if isinstance(template.get("fields"), dict) else 0
            log.info(f"[report_type] Template[{i}]: name={template_name!r}, id={template_id}, fields={field_count}")

        return self.templates

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """Validate the effect fields and return any error details."""
        log.info("[report_type] ========== PrefillDocumentFields._get_error_details START ==========")
        log.info(f"[report_type] method: {method}")
        log.info(f"[report_type] document_id: {self.document_id!r}")
        log.info(f"[report_type] source_protocol: {self.source_protocol!r}")
        log.info(f"[report_type] templates: {self.templates!r}")

        errors = super()._get_error_details(method)

        # Validate templates is non-empty list
        if self.templates is not None and len(self.templates) == 0:
            log.warning("[report_type] templates is empty list")
            errors.append(
                self._create_error_detail(
                    "value_error",
                    "templates must be a non-empty list",
                    self.templates,
                )
            )

        # Validate each template structure
        if self.templates:
            log.info(f"[report_type] Validating {len(self.templates)} templates")
            for i, template in enumerate(self.templates):
                errors.extend(self._validate_template(template, i))

        # Validate top-level annotations
        if self.annotations:
            log.info(f"[report_type] Validating {len(self.annotations)} top-level annotations")
            for i, annotation in enumerate(self.annotations):
                errors.extend(self._validate_annotation(annotation, f"annotations[{i}]"))

        log.info(f"[report_type] PrefillDocumentFields validation completed with {len(errors)} errors")
        log.info("[report_type] ========== PrefillDocumentFields._get_error_details END ==========")
        return errors

    def _validate_template(self, template: dict[str, Any], index: int) -> list[InitErrorDetails]:
        """Validate a single template structure (field_type=REPORT_TYPE)."""
        errors: list[InitErrorDetails] = []
        prefix = f"templates[{index}]"

        log.info(f"[report_type] Validating template {index}")
        log.info(f"[report_type] Template keys: {list(template.keys())}")

        # Check template_id
        if "template_id" not in template:
            log.warning(f"[report_type] {prefix}.template_id missing")
            errors.append(
                self._create_error_detail(
                    "value_error",
                    f"{prefix}.template_id is required",
                    template,
                )
            )
        else:
            log.info(f"[report_type] {prefix}.template_id: {template['template_id']}")

        # Check template_name
        if "template_name" not in template:
            log.warning(f"[report_type] {prefix}.template_name missing")
            errors.append(
                self._create_error_detail(
                    "value_error",
                    f"{prefix}.template_name is required",
                    template,
                )
            )
        elif not template.get("template_name", "").strip():
            log.warning(f"[report_type] {prefix}.template_name is empty")
            errors.append(
                self._create_error_detail(
                    "value_error",
                    f"{prefix}.template_name must be a non-empty string",
                    template.get("template_name"),
                )
            )
        else:
            log.info(f"[report_type] {prefix}.template_name: {template['template_name']!r}")

        # Check fields
        fields = template.get("fields", {})
        if isinstance(fields, dict):
            log.info(f"[report_type] {prefix} has {len(fields)} fields")
            for field_key, field_data in fields.items():
                field_path = f"{prefix}.fields.{field_key}"
                if not isinstance(field_data, dict):
                    log.error(f"[report_type] {field_path} is not a dict: {type(field_data).__name__}")
                    errors.append(
                        self._create_error_detail(
                            "value_error",
                            f"{field_path} must be a dict",
                            field_data,
                        )
                    )
                    continue
                errors.extend(self._validate_field(field_data, field_path))
        else:
            log.warning(f"[report_type] {prefix}.fields is not a dict: {type(fields).__name__}")

        return errors

    def _validate_field(self, field_data: dict[str, Any], path: str) -> list[InitErrorDetails]:
        """Validate a single field structure (field_type=REPORT_TYPE)."""
        errors: list[InitErrorDetails] = []

        log.info(f"[report_type] Validating field at {path}")
        log.info(f"[report_type] Field data keys: {list(field_data.keys())}")

        # Check value key exists
        if "value" not in field_data:
            log.warning(f"[report_type] {path}.value missing")
            errors.append(
                self._create_error_detail(
                    "value_error",
                    f"{path}.value is required",
                    field_data,
                )
            )
        else:
            log.info(f"[report_type] {path}.value: {field_data['value']!r}")

        # Log other field attributes
        if "unit" in field_data:
            log.info(f"[report_type] {path}.unit: {field_data['unit']!r}")
        if "reference_range" in field_data:
            log.info(f"[report_type] {path}.reference_range: {field_data['reference_range']!r}")
        if "abnormal" in field_data:
            log.info(f"[report_type] {path}.abnormal: {field_data['abnormal']!r}")

        # Validate field-level annotations
        if "annotations" in field_data and field_data["annotations"]:
            log.info(f"[report_type] {path} has {len(field_data['annotations'])} annotations")
            for i, annotation in enumerate(field_data["annotations"]):
                annotation_path = f"{path}.annotations[{i}]"
                if not isinstance(annotation, dict):
                    log.error(f"[report_type] {annotation_path} is not a dict")
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

    def _validate_annotation(
        self, annotation: AnnotationItem | dict[str, Any], path: str
    ) -> list[InitErrorDetails]:
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


__exports__ = ("PrefillDocumentFieldData", "PrefillDocumentFields")
