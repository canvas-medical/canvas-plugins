import importlib.metadata

import deprecation

from canvas_sdk.effects.claim.claim_comment import _AddClaimComment

version = importlib.metadata.version("canvas")


@deprecation.deprecated(
    deprecated_in="0.95.0",
    removed_in="1.0.0",
    current_version=version,
    details="Use canvas_sdk.effects.claim.Claim::add_comment instead",
)
class AddClaimComment(_AddClaimComment):
    """Deprecated. Instead, use canvas_sdk.effects.claim.Claim::add_comment."""

    pass


__all__ = __exports__ = ("AddClaimComment",)
