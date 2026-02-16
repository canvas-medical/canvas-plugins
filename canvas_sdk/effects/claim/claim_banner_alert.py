from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.effects.base import EffectType, _BaseEffect
from canvas_sdk.v1.data import Claim


class BannerAlertIntent(StrEnum):
    """BannerAlertIntent."""

    INFO = "info"
    WARNING = "warning"
    ALERT = "alert"


class _AddClaimBannerAlert(_BaseEffect):
    """Effect to add a banner alert to a Claim."""

    class Meta:
        effect_type = EffectType.ADD_CLAIM_BANNER_ALERT

    claim_id: UUID | str
    key: str
    narrative: str = Field(max_length=90)
    intent: BannerAlertIntent = Field(strict=False)
    href: str | None = None

    @property
    def values(self) -> dict[str, Any]:
        """The values for adding a claim banner alert."""
        return {
            "claim_id": str(self.claim_id),
            "key": self.key,
            "narrative": self.narrative,
            "intent": self.intent.value,
            "href": self.href,
        }

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        if not Claim.objects.filter(id=self.claim_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Claim with id {self.claim_id} does not exist.",
                    self.claim_id,
                )
            )
        return errors


class _RemoveClaimBannerAlert(_BaseEffect):
    """Effect to remove/inactivate a banner alert for a Claim."""

    class Meta:
        effect_type = EffectType.REMOVE_CLAIM_BANNER_ALERT

    claim_id: UUID | str
    key: str

    @property
    def values(self) -> dict[str, Any]:
        """The values for removing the claim banner alert."""
        return {"claim_id": str(self.claim_id), "key": self.key}

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        if not Claim.objects.filter(id=self.claim_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Claim with id {self.claim_id} does not exist.",
                    self.claim_id,
                )
            )
        return errors


__exports__ = ()
