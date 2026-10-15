from django.db import models

from canvas_sdk.v1.data.base import Model
from canvas_sdk.v1.data.common import DocumentReviewMode


class Report(Model):
    """Fields shared by every document that goes through review: who it is assigned to and how.

    A document is assigned to staff (each type's `reviewers`) or to a team (`team`). Each type
    declares its own `reviewers` and `review`, since those point at type-specific views and models.
    """

    class Meta:
        abstract = True

    review_mode = models.CharField(choices=DocumentReviewMode.choices, max_length=2)
    junked = models.BooleanField(default=False)
    assigned_date = models.DateTimeField(null=True)
    team = models.ForeignKey(
        "v1.Team",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="%(class)s_set",
        related_query_name="%(class)s",
    )
    team_assigned_date = models.DateTimeField(null=True)
    assigned_by = models.ForeignKey(
        "v1.CanvasUser", on_delete=models.DO_NOTHING, null=True, related_name="+"
    )


__exports__ = ("Report",)
