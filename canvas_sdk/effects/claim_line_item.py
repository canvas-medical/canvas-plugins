import importlib.metadata

import deprecation

from canvas_sdk.effects.claim.claim_line_item import UpdateClaimLineItem as _UpdateClaimLineItem

version = importlib.metadata.version("canvas")


@deprecation.deprecated(
    deprecated_in="0.95.0",
    removed_in="1.0.0",
    current_version=version,
    details="Use canvas_sdk.effects.claim.UpdateClaimLineItem instead",
)
class UpdateClaimLineItem(_UpdateClaimLineItem):
    """Deprecated. Instead, use canvas_sdk.effects.claim.UpdateClaimLineItem."""

    pass


__all__ = __exports__ = ("UpdateClaimLineItem",)
