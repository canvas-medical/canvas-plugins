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
    - Validate the document exists
    - Look up the DocumentType by key
    - Validate the document type exists
    - Set the IntegrationTask.type field to the document type name

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

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """Validate the effect fields and return any error details.

        Note: confidence_scores validation (invalid keys, range constraints) is
        handled by Pydantic at construction time via model_validator and TypedDict
        with Annotated field constraints.
        """
        errors = super()._get_error_details(method)

        if self.document_type is None:
            pass
        elif not isinstance(self.document_type, dict):
            errors.append(
                self._create_error_detail(
                    "value",
                    "document_type must be a dict with keys: key, name, report_type, template_type",
                    self.document_type,
                )
            )
        else:
            if "key" not in self.document_type:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "document_type.key is required",
                        None,
                    )
                )
            elif (
                not isinstance(self.document_type["key"], str)
                or not self.document_type["key"].strip()
            ):
                errors.append(
                    self._create_error_detail(
                        "value",
                        "document_type.key must be a non-empty string",
                        self.document_type.get("key"),
                    )
                )

            if "name" not in self.document_type:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "document_type.name is required",
                        None,
                    )
                )
            elif (
                not isinstance(self.document_type["name"], str)
                or not self.document_type["name"].strip()
            ):
                errors.append(
                    self._create_error_detail(
                        "value",
                        "document_type.name must be a non-empty string",
                        self.document_type.get("name"),
                    )
                )

            if "report_type" not in self.document_type:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "document_type.report_type is required",
                        None,
                    )
                )
            elif self.document_type["report_type"] not in VALID_REPORT_TYPES:
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"document_type.report_type must be one of {sorted(VALID_REPORT_TYPES)}, got: {self.document_type['report_type']}",
                        self.document_type.get("report_type"),
                    )
                )

            if "template_type" in self.document_type:
                template_type = self.document_type["template_type"]
                if template_type is not None:
                    if not isinstance(template_type, str):
                        errors.append(
                            self._create_error_detail(
                                "value",
                                "document_type.template_type must be a string or null",
                                template_type,
                            )
                        )
                    elif template_type not in VALID_TEMPLATE_TYPES:
                        errors.append(
                            self._create_error_detail(
                                "value",
                                f"document_type.template_type must be one of {sorted(VALID_TEMPLATE_TYPES)} or null, got: {template_type}",
                                template_type,
                            )
                        )

        if self.confidence_scores is not None and not isinstance(self.confidence_scores, dict):
            errors.append(
                self._create_error_detail(
                    "value",
                    "confidence_scores must be a dict if provided",
                    self.confidence_scores,
                )
            )

        return errors


__exports__ = (
    "ConfidenceScores",
    "DocumentType",
    "DocumentTypeConfidenceScores",
    "CategorizeDocument",
)
