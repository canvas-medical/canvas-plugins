from canvas_sdk.commands.commands.review.base import _BaseReview
from canvas_sdk.v1.data import LabReport


class LabReviewCommand(_BaseReview):
    """A class for managing a Lab Review command within a specific note."""

    class Meta:
        key = "labReview"
        model = LabReport


__exports__ = ("LabReviewCommand",)
