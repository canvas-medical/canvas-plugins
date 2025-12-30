from collections.abc import Mapping
from typing import Annotated, Any

from pydantic import Field, model_validator
from pydantic_core import InitErrorDetails
from typing_extensions import TypedDict

from canvas_sdk.effects.base import EffectType, _BaseEffect


class DocumentTypeConfidenceScores(TypedDict, total=False):
    """
    Confidence scores for individual document_type fields.

    All fields are optional. Values must be floats between 0.0 and 1.0.

    Attributes:
        key: Confidence in key match (0.0-1.0)
        name: Confidence in name match (0.0-1.0)
        report_type: Confidence in report_type (0.0-1.0)
        template_type: Confidence in template_type (0.0-1.0)
    """

    key: Annotated[float, Field(ge=0.0, le=1.0)]
    name: Annotated[float, Field(ge=0.0, le=1.0)]
    report_type: Annotated[float, Field(ge=0.0, le=1.0)]
    template_type: Annotated[float, Field(ge=0.0, le=1.0)]


class ConfidenceScores(TypedDict, total=False):
    """
    Confidence scores for document fields extracted from a document.

    All fields are optional. Values must be floats between 0.0 and 1.0,
    representing the confidence level of each extracted field (e.g., from OCR).

    Attributes:
        document_id: Confidence score for the document_id field (0.0-1.0)
        document_type: Confidence scores for document_type fields, as a nested dict
            with keys: key, name, report_type, template_type (each 0.0-1.0)
    """

    document_id: Annotated[float, Field(ge=0.0, le=1.0)]
    document_type: DocumentTypeConfidenceScores


CONFIDENCE_SCORE_KEYS = frozenset(ConfidenceScores.__annotations__.keys())
DOCUMENT_TYPE_CONFIDENCE_KEYS = frozenset(DocumentTypeConfidenceScores.__annotations__.keys())


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


VALID_REPORT_TYPES = frozenset(["CLINICAL", "ADMINISTRATIVE"])
VALID_TEMPLATE_TYPES = frozenset(
    ["LabReportTemplate", "ImagingReportTemplate", "SpecialtyReportTemplate"]
)


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
        confidence_scores: Optional confidence scores for document fields.
            See ConfidenceScores TypedDict for valid keys and value constraints.
    """

    class Meta:
        effect_type = EffectType.CATEGORIZE_DOCUMENT
        apply_required_fields = ("document_id", "document_type")

    document_id: str | int | None = None
    document_type: DocumentType | dict[str, Any] | None = None
    confidence_scores: ConfidenceScores | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_confidence_scores_keys(cls, data: Any) -> Any:
        """Validate confidence_scores keys before Pydantic processes the TypedDict.

        TypedDict in Pydantic silently drops unknown keys, so we validate
        them here to provide a clear error message to users.
        """
        if isinstance(data, dict) and "confidence_scores" in data:
            scores = data.get("confidence_scores")
            if isinstance(scores, dict):
                invalid_keys = set(scores.keys()) - CONFIDENCE_SCORE_KEYS
                if invalid_keys:
                    raise ValueError(
                        f"confidence_scores contains invalid keys: {sorted(invalid_keys)}. "
                        f"Valid keys are: {sorted(CONFIDENCE_SCORE_KEYS)}"
                    )

                if "document_type" in scores and isinstance(scores["document_type"], dict):
                    doc_type_scores = scores["document_type"]
                    invalid_doc_type_keys = (
                        set(doc_type_scores.keys()) - DOCUMENT_TYPE_CONFIDENCE_KEYS
                    )
                    if invalid_doc_type_keys:
                        raise ValueError(
                            f"confidence_scores.document_type contains invalid keys: {sorted(invalid_doc_type_keys)}. "
                            f"Valid keys are: {sorted(DOCUMENT_TYPE_CONFIDENCE_KEYS)}"
                        )
        return data

    @property
    def values(self) -> dict[str, Any]:
        """The effect's values to be sent in the payload."""
        result: dict[str, Any] = {
            "document_id": str(self.document_id) if self.document_id is not None else None,
            "document_type": self.document_type,
        }

        if self.confidence_scores is not None:
            result["confidence_scores"] = self.confidence_scores

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
        """Validate the effect fields and return any error details.

        Note: confidence_scores validation (invalid keys, range constraints) is
        handled by Pydantic at construction time via model_validator and TypedDict
        with Annotated field constraints.
        """
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
    "ConfidenceScores",
    "DocumentType",
    "DocumentTypeConfidenceScores",
    "CategorizeDocument",
)
