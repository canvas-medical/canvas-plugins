from canvas_sdk.commands.commands.review.base import _BaseReview
from canvas_sdk.v1.data import UncategorizedClinicalDocument


class UncategorizedDocumentReviewCommand(_BaseReview):
    """A class for managing an Uncategorized Document Review command within a specific note."""

    class Meta:
        key = "uncategorizedDocumentReview"
        model = UncategorizedClinicalDocument


__exports__ = ("UncategorizedDocumentReviewCommand",)
