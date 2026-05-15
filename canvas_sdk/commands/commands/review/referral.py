from canvas_sdk.commands.commands.review.base import _BaseReview
from canvas_sdk.v1.data import ReferralReport


class ReferralReviewCommand(_BaseReview):
    """A class for managing a Referral Review command within a specific note."""

    class Meta:
        key = "referralReview"
        model = ReferralReport


__exports__ = ("ReferralReviewCommand",)
