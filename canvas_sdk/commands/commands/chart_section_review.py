from enum import Enum

from canvas_sdk.commands.base import _BaseCommand


class ChartSectionReviewCommand(_BaseCommand):
    """A class for managing a Chart Section Review command within a specific note."""

    class Meta:
        key = "chartSectionReview"

    class Sections(Enum):
        CONDITIONS = "conditions"
        SURGICAL_HISTORY = "surgical_history"
        MEDICATIONS = "medications"
        FAMILY_HISTORY = "family_histories"
        ALLERGIES = "allergies"
        IMMUNIZATIONS = "immunizations"

    section: Sections


__exports__ = ("ChartSectionReviewCommand",)
