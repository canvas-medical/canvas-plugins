from datetime import date
from typing import Annotated, Any

from pydantic import Field
from pydantic_core import InitErrorDetails
from typing_extensions import TypedDict

from canvas_sdk.effects.base import EffectType
from canvas_sdk.effects.data_integration.base import _BaseDocumentEffect


class LinkDocumentConfidenceScores(TypedDict, total=False):
    """
    Confidence scores for patient demographic fields extracted from a document.

    All fields are optional. Values must be floats between 0.0 and 1.0,
    representing the confidence level of each extracted field (e.g., from OCR).

    Attributes:
        first_name: Confidence score for the extracted first name (0.0-1.0)
        last_name: Confidence score for the extracted last name (0.0-1.0)
        date_of_birth: Confidence score for the extracted date of birth (0.0-1.0)
    """

    first_name: Annotated[float, Field(ge=0.0, le=1.0)]
    last_name: Annotated[float, Field(ge=0.0, le=1.0)]
    date_of_birth: Annotated[float, Field(ge=0.0, le=1.0)]


# Public constant for backward compatibility with tests
CONFIDENCE_SCORE_KEYS = frozenset(LinkDocumentConfidenceScores.__annotations__.keys())


class LinkDocumentToPatient(_BaseDocumentEffect):
    """
    An Effect that links a document in the Data Integration queue to a patient
    based on patient demographics (first name, last name, date of birth).

    When processed by the home-app interpreter, this effect will:
    - Filter patients by the provided demographics (case-insensitive names, exact date match)
    - If exactly one patient matches, link the document to that patient
    - If zero or multiple patients match, throw an exception

    Attributes:
        first_name: The patient's first name (required, non-empty string).
            Leading/trailing whitespace is stripped during serialization.
        last_name: The patient's last name (required, non-empty string).
            Leading/trailing whitespace is stripped during serialization.
        date_of_birth: The patient's date of birth (required, date object).
        document_id: The ID of the IntegrationTask document to link (required, non-empty).
            Accepts str or int; always serialized as string in the payload.
        confidence_scores: Optional confidence scores for each demographic field.
            See LinkDocumentConfidenceScores TypedDict for valid keys and value constraints.
    """

    class Meta:
        effect_type = EffectType.LINK_DOCUMENT_TO_PATIENT
        apply_required_fields = (
            "first_name",
            "last_name",
            "date_of_birth",
            "document_id",
        )

    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None
    document_id: str | int | None = None
    confidence_scores: LinkDocumentConfidenceScores | None = None

    @classmethod
    def _get_confidence_score_keys(cls) -> frozenset[str]:
        """Return valid keys for confidence_scores validation."""
        return frozenset(LinkDocumentConfidenceScores.__annotations__.keys())

    @property
    def values(self) -> dict[str, Any]:
        """The effect's values to be sent in the payload.

        Names are stripped of leading/trailing whitespace during serialization.
        """
        result: dict[str, Any] = {
            "first_name": self.first_name.strip() if self.first_name else None,
            "last_name": self.last_name.strip() if self.last_name else None,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "document_id": str(self.document_id).strip() if self.document_id is not None else None,
        }
        if self.confidence_scores is not None:
            result["confidence_scores"] = self.confidence_scores
        return result

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """Validate the effect fields and return any error details.

        Note: confidence_scores validation (invalid keys, range constraints) is
        handled by Pydantic at construction time via model_validator and TypedDict
        with Annotated field constraints.
        """
        errors = super()._get_error_details(method)
        self._validate_document_id_not_empty(errors)

        # Validate first_name is non-empty if provided
        if self.first_name is not None and not self.first_name.strip():
            errors.append(
                self._create_error_detail(
                    "value_error",
                    "first_name must be a non-empty string",
                    self.first_name,
                )
            )

        # Validate last_name is non-empty if provided
        if self.last_name is not None and not self.last_name.strip():
            errors.append(
                self._create_error_detail(
                    "value_error",
                    "last_name must be a non-empty string",
                    self.last_name,
                )
            )

        return errors


__exports__ = ("LinkDocumentConfidenceScores", "LinkDocumentToPatient")
