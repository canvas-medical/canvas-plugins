"""Base classes for data integration effects."""

from abc import abstractmethod
from typing import Any

from pydantic import model_validator
from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import _BaseEffect


class _BaseDocumentEffect(_BaseEffect):
    """Base class for document-related effects with confidence scores.

    This class provides shared functionality for data integration effects that
    operate on documents and include confidence score validation.

    Subclasses must:
    1. Define their own confidence_scores field with appropriate TypedDict
    2. Implement _get_confidence_score_keys() to return valid keys
    3. Call _validate_document_id_not_empty() in _get_error_details() if needed
    """

    @classmethod
    @abstractmethod
    def _get_confidence_score_keys(cls) -> frozenset[str]:
        """Return valid keys for confidence_scores validation.

        Override in subclass to return frozenset of valid key names.
        Example: return frozenset(MyConfidenceScores.__annotations__.keys())
        """
        ...

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
                valid_keys = cls._get_confidence_score_keys()
                invalid_keys = set(scores.keys()) - valid_keys
                if invalid_keys:
                    raise ValueError(
                        f"confidence_scores contains invalid keys: {sorted(invalid_keys)}. "
                        f"Valid keys are: {sorted(valid_keys)}"
                    )
        return data

    def _validate_document_id_not_empty(self, errors: list[InitErrorDetails]) -> None:
        """Validate document_id is a non-empty string if provided.

        Call this from _get_error_details() in subclasses that have document_id.
        """
        if hasattr(self, "document_id"):
            if isinstance(self.document_id, str) and not self.document_id.strip():
                errors.append(
                    self._create_error_detail(
                        "value_error",
                        "document_id must be a non-empty string",
                        self.document_id,
                    )
                )


__exports__ = ("_BaseDocumentEffect",)
