import json
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.base import _BaseEffect
from canvas_sdk.effects.claim.claim_label import Label
from canvas_sdk.v1.data import Claim as ClaimModel
from canvas_sdk.v1.data import ClaimQueue


class Claim(_BaseEffect):
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
        self._validate_before_effect("add_comment")
        return Effect(
            type=EffectType.ADD_CLAIM_COMMENT,
            payload=json.dumps({"data": {"claim_id": str(self.claim_id), "comment": comment}}),
        )

    def add_label(self, labels: list[str | Label]) -> Effect:
        """
        Adds one or more labels to the claim.

        Args:
            labels (list[str | Label]): A list of label names (str) or Label objects with color and name.

        Returns:
            Effect: An effect that adds the labels to the claim.
        """
        self._validate_before_effect("add_label")
        label_data = {
            "claim_id": str(self.claim_id),
            "labels": [
                label.to_dict() if isinstance(label, Label) else {"name": label} for label in labels
            ],
        }
        return Effect(
            type=EffectType.ADD_CLAIM_LABEL,
            payload=json.dumps({"data": label_data}),
        )

    def remove_label(self, labels: list[str]) -> Effect:
        """
        Removes one or more labels from the claim.

        Args:
            labels (list[str]): A list of label names to remove.

        Returns:
            Effect: An effect that removes the labels from the claim.
        """
        self._validate_before_effect("remove_label")
        return Effect(
            type=EffectType.REMOVE_CLAIM_LABEL,
            payload=json.dumps({"data": {"claim_id": str(self.claim_id), "labels": list(labels)}}),
        )

    def move_to_queue(self, queue: str) -> Effect:
        """
        Moves the claim to a queue.

        Args:
            queue (str): The name of the queue to move the claim to.

        Returns:
            Effect: An effect that moves the claim to the specified queue.
        """
        self._queue = queue
        self._validate_before_effect("move_to_queue")
        return Effect(
            type=EffectType.MOVE_CLAIM_TO_QUEUE,
            payload=json.dumps({"data": {"claim_id": str(self.claim_id), "queue": queue}}),
        )

    def _get_error_details(self, method: str) -> list[InitErrorDetails]:
        """
        Validates the claim and returns a list of error details if validation fails.

        Args:
            method (str): The method being validated.

        Returns:
            list[InitErrorDetails]: A list of error details for validation failures.
        """
        errors = super()._get_error_details(method)

        if not ClaimModel.objects.filter(id=self.claim_id).exists():
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Claim with id {self.claim_id} does not exist.",
                    self.claim_id,
                )
            )

        if method == "move_to_queue":
            queue = getattr(self, "_queue", None)
            if queue and not ClaimQueue.objects.filter(name=queue).exists():
                errors.append(
                    self._create_error_detail(
                        "value",
                        "Queue does not exist",
                        queue,
                    )
                )

        return errors


__exports__ = ("Claim", "Label")
