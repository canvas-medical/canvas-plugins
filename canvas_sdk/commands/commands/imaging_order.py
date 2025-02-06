from enum import Enum

from canvas_sdk.commands.base import _BaseCommand as BaseCommand


class ImagingOrderCommand(BaseCommand):
    """A class for managing an Imaging Order command within a specific note."""

    class Meta:
        key = "imagingOrder"
        commit_required_fields = (
            "image_code",
            "diagnosis_codes",
            "ordering_provider",
        )

    class Priority(Enum):
        ROUTINE = "Routine"
        URGENT = "Urgent"

    image_code: str | None = None
    diagnosis_codes: list[str] = []
    priority: Priority | None = None
    additional_details: str | None = None
    imaging_center: str | None = None
    comment: str | None = None
    ordering_provider_key: str | None = None
    linked_items_urns: list[str] | None = None

    @property
    def values(self) -> dict:
        """The Imaging Order command's field values."""
        return {
            "image_code": self.image_code,
            "diagnosis_codes": self.diagnosis_codes,
            "priority": self.priority.value if self.priority else None,
            "additional_details": self.additional_details,
            "comment": self.comment,
            "ordering_provider_key": self.ordering_provider_key,
            "linked_items_urns": self.linked_items_urns,
        }
