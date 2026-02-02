from uuid import UUID

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.base import _BaseEffect
from canvas_sdk.effects.claim.claim_comment import _AddClaimComment
from canvas_sdk.effects.claim.claim_label import ColorEnum, Label, _AddClaimLabel, _RemoveClaimLabel
from canvas_sdk.effects.claim.claim_queue import _MoveClaimToQueue


class ClaimEffect(_BaseEffect):
    """
    Effect for performing actions on a Claim.

    Attributes:
        claim_id (UUID | str): The unique identifier for the claim instance.
    """

    class Meta:
        effect_type = EffectType.UNKNOWN_EFFECT

    claim_id: UUID | str

    def add_comment(self, comment: str) -> Effect:
        """
        Adds a comment to the claim.

        Args:
            comment (str): The comment text to add to the claim.

        Returns:
            Effect: An effect that adds the comment to the claim.
        """
        return _AddClaimComment(claim_id=self.claim_id, comment=comment).apply()

    def add_label(self, labels: list[str | Label]) -> Effect:
        """
        Adds one or more labels to the claim.

        Args:
            labels (list[str | Label]): A list of label names (str) or Label objects with color and name.

        Returns:
            Effect: An effect that adds the labels to the claim.
        """
        return _AddClaimLabel(claim_id=self.claim_id, labels=labels).apply()

    def remove_label(self, labels: list[str]) -> Effect:
        """
        Removes one or more labels from the claim.

        Args:
            labels (list[str]): A list of label names to remove.

        Returns:
            Effect: An effect that removes the labels from the claim.
        """
        return _RemoveClaimLabel(claim_id=self.claim_id, labels=labels).apply()

    def move_to_queue(self, queue: str) -> Effect:
        """
        Moves the claim to a queue.

        Args:
            queue (str): The name of the queue to move the claim to.

        Returns:
            Effect: An effect that moves the claim to the specified queue.
        """
        return _MoveClaimToQueue(claim_id=self.claim_id, queue=queue).apply()


__all__ = __exports__ = (
    "ClaimEffect",
    "Label",
    "ColorEnum",
)
