import importlib.metadata

import deprecation

from canvas_sdk.effects.claim.claim_queue import MoveClaimToQueue as _MoveClaimToQueue

version = importlib.metadata.version("canvas")


@deprecation.deprecated(
    deprecated_in="0.95.0",
    removed_in="1.0.0",
    current_version=version,
    details="Use canvas_sdk.effects.claim.Claim::move_to_queue instead",
)
class MoveClaimToQueue(_MoveClaimToQueue):
    """Deprecated. Instead, use canvas_sdk.effects.claim.Claim::move_to_queue."""

    pass


__all__ = __exports__ = ("MoveClaimToQueue",)
