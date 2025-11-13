from abc import ABC
from enum import StrEnum
from typing import Any
from uuid import UUID

from django.db.models import Q
from pydantic_core import InitErrorDetails

from canvas_sdk.commands.base import _BaseCommand


class ReportReviewCommunicationMethod(StrEnum):
    """Communication methods for a report review."""

    DELEGATED_CALL_CAN_LEAVE_MESSAGE = "DM"
    DELEGATED_CALL_NEED_ANSWER = "DA"
    DELEGATED_LETTER = "DL"
    ALREADY_LEFT_MESSAGE = "AM"
    ALREADY_REVIEWED_WITH_PATIENT = "AR"


class ReviewMode(StrEnum):
    """Review modes for a report review."""

    REVIEW_REQUIRED = "RR"
    ALREADY_REVIEWED_OFFLINE = "AR"
    REVIEW_NOT_REQUIRED = "RN"


class _BaseReview(_BaseCommand, ABC):
    """A base class for review commands."""

    class Meta:
        key = "review"  # we have to set a key because this is a _BaseCommand
        model = None

    report_ids: list[str | UUID] | None = None
    message_to_patient: str | None = None
    communication_method: ReportReviewCommunicationMethod | None = None
    linked_items_urns: list[str] | None = None
    comment: str | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if self.report_ids:
            for report_id in self.report_ids:
                try:
                    can_be_reviewed = self.Meta.model.objects.filter(  # type: ignore[attr-defined]
                        Q(id=report_id),
                        Q(review_mode=ReviewMode.REVIEW_REQUIRED),
                        (
                            Q(review__committer__isnull=True)
                            | Q(review__entered_in_error__isnull=False)
                        ),
                    ).exists()
                    if not can_be_reviewed:
                        errors.append(
                            self._create_error_detail(
                                "value",
                                f"{self.Meta.model.__class__.__name__} with ID {report_id} cannot be reviewed.",
                                self.report_ids,
                            )
                        )
                except self.Meta.model.DoesNotExist:  # type: ignore[attr-defined]
                    errors.append(
                        self._create_error_detail(
                            "value",
                            f"{self.Meta.model.__class__.__name__} with ID {report_id} does not exist.",
                            self.report_ids,
                        )
                    )

        return errors


__exports__ = ()
