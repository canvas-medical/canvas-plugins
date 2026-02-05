import importlib.metadata

import deprecation

from canvas_sdk.effects.claim.claim_label import Label, _AddClaimLabel, _RemoveClaimLabel
from canvas_sdk.v1.data.common import ColorEnum

version = importlib.metadata.version("canvas")


@deprecation.deprecated(
    deprecated_in="0.95.0",
    removed_in="1.0.0",
    current_version=version,
    details="Instead, use canvas_sdk.effects.claim.Claim::add_labels",
)
class AddClaimLabel(_AddClaimLabel):
    """Deprecated. Instead, use canvas_sdk.effects.claim.Claim::add_labels."""

    pass


@deprecation.deprecated(
    deprecated_in="0.95.0",
    removed_in="1.0.0",
    current_version=version,
    details="Instead, use canvas_sdk.effects.claim.Claim::remove_labels",
)
class RemoveClaimLabel(_RemoveClaimLabel):
    """Deprecated. Instead, use canvas_sdk.effects.claim.Claim::remove_labels."""

    pass


__all__ = __exports__ = (
    "Label",
    "ColorEnum",
    "AddClaimLabel",
    "RemoveClaimLabel",
)
