import importlib.metadata

import deprecation

from canvas_sdk.effects.claim.claim_payment import _PostClaimPayment

version = importlib.metadata.version("canvas")


@deprecation.deprecated(
    deprecated_in="0.95.0",
    removed_in="1.0.0",
    current_version=version,
    details="Use canvas_sdk.effects.claim.ClaimEffect::post_payment instead",
)
class PostClaimPayment(_PostClaimPayment):
    """Deprecated. Instead, use canvas_sdk.effects.claim.ClaimEffect::post_payment."""

    pass


__exports__ = ("PostClaimPayment",)
