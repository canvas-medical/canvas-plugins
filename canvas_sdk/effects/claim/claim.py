from uuid import UUID

from canvas_sdk.base import Model
from canvas_sdk.effects import Effect
from canvas_sdk.effects.claim.claim_banner_alert import (
    BannerAlertIntent,
    _AddClaimBannerAlert,
    _RemoveClaimBannerAlert,
)


class ClaimEffect(Model):
    """
    Effect for performing actions on a Claim.

    Attributes:
        claim_id (UUID | str): The unique identifier for the claim instance.
    """

    claim_id: UUID | str

    def add_banner(
        self, key: str, narrative: str, intent: BannerAlertIntent, href: str | None = None
    ) -> Effect:
        """
        Adds a banner alert to a claim.

        Args:
            key (str): A unique identifier for the banner alert.
            narrative (str): The text content to display in the banner.
            intent (BannerAlertIntent): The intent/severity level of the banner (info, warning, or alert).
            href (str | None): Optional URL link for the banner. Defaults to None.

        Returns:
            Effect: An effect that adds the banner alert to the claim.
        """
        return _AddClaimBannerAlert(
            claim_id=self.claim_id, key=key, narrative=narrative, intent=intent, href=href
        ).apply()

    def remove_banner(self, key: str) -> Effect:
        """
        Removes a banner alert from a claim.

        Args:
            key (str): A unique identifier for the banner alert.

        Returns:
            Effect: An effect that removes the banner alert from the claim.
        """
        return _RemoveClaimBannerAlert(claim_id=self.claim_id, key=key).apply()


__all__ = __exports__ = (
    "ClaimEffect",
    "BannerAlertIntent",
)
