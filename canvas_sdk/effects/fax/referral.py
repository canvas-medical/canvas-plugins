from typing import Any, Literal
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.fax.base import BaseFaxEffectOptionalRecipient
from canvas_sdk.v1.data import Referral


class FaxReferralEffect(BaseFaxEffectOptionalRecipient):
    """Fax a referral and its attachments, by default to its service provider."""

    class Meta:
        effect_type = EffectType.FAX_REFERRAL

    referral_id: str | UUID

    def _get_error_details(self, method: Literal["apply"]) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        if self.referral_id and not Referral.objects.filter(id=self.referral_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Referral with ID {self.referral_id} does not exist.",
                    self.referral_id,
                )
            )

        return errors

    @property
    def values(self) -> dict[str, Any]:
        """Return the values of the referral fax effect."""
        return {**super().values, "referral_id": str(self.referral_id)}


__exports__ = ()
