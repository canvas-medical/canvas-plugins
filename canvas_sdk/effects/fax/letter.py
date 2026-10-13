from typing import Any, Literal
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.fax.base import BaseFaxEffect
from canvas_sdk.v1.data import Letter


class FaxLetterEffect(BaseFaxEffect):
    """Fax a letter and its attachments."""

    class Meta:
        effect_type = EffectType.FAX_LETTER

    letter_id: str | UUID

    def _get_error_details(self, method: Literal["apply"]) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        if self.letter_id and not Letter.objects.filter(id=self.letter_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Letter with ID {self.letter_id} does not exist.",
                    self.letter_id,
                )
            )

        return errors

    @property
    def values(self) -> dict[str, Any]:
        """Return the values of the letter fax effect."""
        return {**super().values, "letter_id": str(self.letter_id)}


__exports__ = ()
