from typing import Any

from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect


class RemoveDocumentFromPatientEffect(_BaseEffect):
    """
    An Effect that removes/unlinks a patient from a document in the Data Integration queue.

    When an LLM system determines that a document should not be linked to a patient,
    it can emit this effect to remove the patient association from the document.
    """

    class Meta:
        effect_type = EffectType.REMOVE_DOCUMENT_FROM_PATIENT

    document_id: str
    patient_id: str | None = None
    confidence_scores: dict[str, float] | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The effect's values."""
        result: dict[str, Any] = {"document_id": self.document_id}
        if self.patient_id is not None:
            result["patient_id"] = self.patient_id
        if self.confidence_scores is not None:
            result["confidence_scores"] = self.confidence_scores
        return result

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload of the effect."""
        return self.values

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if self.confidence_scores is not None:
            for key, value in self.confidence_scores.items():
                # Validate that the key matches the document_id
                if key != self.document_id:
                    errors.append(
                        self._create_error_detail(
                            "value",
                            f"confidence_scores key {key} does not match document_id {self.document_id}",
                            key,
                        )
                    )

                # Validate that values are between 0.0 and 1.0
                if not (0.0 <= value <= 1.0):
                    errors.append(
                        self._create_error_detail(
                            "value",
                            f"confidence_scores value {value} must be between 0.0 and 1.0",
                            value,
                        )
                    )

        return errors


__exports__ = ("RemoveDocumentFromPatientEffect",)
