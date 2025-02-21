from enum import Enum

from canvas_sdk.commands.base import _BaseCommand as BaseCommand
from canvas_sdk.commands.constants import ServiceProvider


class ReferCommand(BaseCommand):
    """A class for managing a Refer command within a specific note."""

    class Meta:
        key = "refer"
        commit_required_fields = (
            "service_provider",
            "diagnosis_codes",
            "clinical_question",
            "notes_to_specialist",
        )

    class ClinicalQuestion(Enum):
        """Clinical question choices."""

        COGNITIVE_ASSISTANCE = "Cognitive Assistance (Advice/Guidance)"
        ASSISTANCE_WITH_ONGOING_MANAGEMENT = "Assistance with Ongoing Management"
        SPECIALIZED_INTERVENTION = "Specialized intervention"
        DIAGNOSTIC_UNCERTAINTY = "Diagnostic Uncertainty"

    class Priority(Enum):
        """Priority choices."""

        ROUTINE = "Routine"
        URGENT = "Urgent"

    service_provider: ServiceProvider | None = None
    diagnosis_codes: list[str] = []
    clinical_question: ClinicalQuestion | None = None
    priority: Priority | None = None
    notes_to_specialist: str | None = None
    include_visit_note: bool = False
    comment: str | None = None
    linked_items_urns: list[str] | None = None

    @property
    def values(self) -> dict:
        """The Refer command's field values."""
        values = super().values

        if self.is_dirty("service_provider"):
            values["service_provider"] = self.service_provider.__dict__

        return values
