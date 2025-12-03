from enum import StrEnum
from typing import Any
from uuid import UUID

from django.core.exceptions import ImproperlyConfigured
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


class _BaseReview(_BaseCommand):
    """A base class for review commands."""

    class Meta:
        abstract = True
        model = None

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Validate that concrete review commands have a unique key and model."""
        super().__init_subclass__(**kwargs)

        if not hasattr(cls.Meta, "model") or cls.Meta.model is None:
            raise ImproperlyConfigured(f"Review command {cls.__name__!r} must specify Meta.model.")

    report_ids: list[str | UUID] | None = None
    message_to_patient: str | None = None
    communication_method: ReportReviewCommunicationMethod | None = None
    linked_items_urns: list[str] | None = None
    comment: str | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if self.report_ids:
            for report_id in self.report_ids:
                can_be_reviewed = self.Meta.model.objects.filter(  # type: ignore[attr-defined]
                    Q(id=report_id),
                    Q(review_mode=ReviewMode.REVIEW_REQUIRED),
                    (Q(review__committer__isnull=True) | Q(review__entered_in_error__isnull=False)),
                ).exists()
                if not can_be_reviewed:
                    errors.append(
                        self._create_error_detail(
                            "value",
                            f"{self.Meta.model.__class__.__name__} with ID {report_id} cannot be reviewed.",
                            self.report_ids,
                        )
                    )

        return errors


__exports__ = ()
