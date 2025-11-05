from pydantic import Field

from canvas_sdk.commands.base import _BaseCommand as BaseCommand
from canvas_sdk.commands.constants import ServiceProvider
from canvas_sdk.v1.data.task import TaskPriority


class ImagingOrderCommand(BaseCommand):
    """A class for managing an Imaging Order command within a specific note."""

    class Meta:
        key = "imagingOrder"

    image_code: str | None = Field(default=None, json_schema_extra={"commands_api_name": "image"})
    diagnosis_codes: list[str] | None = Field(
        default=None, json_schema_extra={"commands_api_name": "indications"}
    )
    priority: TaskPriority | None = None
    additional_details: str | None = None
    service_provider: ServiceProvider | None = Field(
        default=None, json_schema_extra={"commands_api_name": "ordering_provider"}
    )
    comment: str | None = None
    ordering_provider_key: str | None = None
    linked_items_urns: list[str] | None = None

    @property
    def values(self) -> dict:
        """The Imaging Order command's field values."""
        values = super().values

        if self.is_dirty("service_provider"):
            values["service_provider"] = self.service_provider.__dict__

        return values


__exports__ = ("ImagingOrderCommand",)
