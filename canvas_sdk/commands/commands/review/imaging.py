from canvas_sdk.commands.commands.review.base import _BaseReview
from canvas_sdk.v1.data import ImagingReport


class ImagingReviewCommand(_BaseReview):
    """A class for managing an Imaging Review command within a specific note."""

    class Meta:
        key = "imagingReview"
        model = ImagingReport


__exports__ = ("ImagingReviewCommand",)
