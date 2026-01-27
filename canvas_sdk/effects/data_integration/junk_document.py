from typing import Any

from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect


class JunkDocument(_BaseEffect):
    """
    An Effect that marks a document in the Data Integration queue as junk (spam).

    When processed by the home-app interpreter, this effect will:
    - Validate the document exists
    - Mark the document as junk (spam) by setting IntegrationTask.status to "JUN" (JUNK constant)

    Attributes:
        document_id: The ID of the IntegrationTask document to mark as junk (required, non-empty).
            Accepts str or int; always serialized as string in the payload.
    """

    class Meta:
        effect_type = EffectType.JUNK_DOCUMENT
        apply_required_fields = ("document_id",)

    document_id: str | int | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The effect's values to be sent in the payload."""
        return {
            "document_id": str(self.document_id).strip() if self.document_id is not None else None,
        }

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        """Validate the effect fields and return any error details."""
        errors = super()._get_error_details(method)

        # Validate document_id is non-empty if provided as string
        if isinstance(self.document_id, str) and not self.document_id.strip():
            errors.append(
                self._create_error_detail(
                    "value_error",
                    "document_id must be a non-empty string",
                    self.document_id,
                )
            )

        return errors


__exports__ = ("JunkDocument",)
