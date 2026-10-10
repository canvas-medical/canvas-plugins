from typing import Self

from pydantic import Field, model_validator

from canvas_sdk.commands.base import _BaseCommand as BaseCommand
from canvas_sdk.commands.base import _SignCommandMixin
from canvas_sdk.commands.constants import ServiceProvider


class OrderDmeCommand(_SignCommandMixin, BaseCommand):
    """A class for managing an Order DME command within a specific note."""

    class Meta:
        key = "orderDme"

    dme_product_id: str | None = Field(
        default=None, json_schema_extra={"commands_api_name": "item"}
    )
    free_text_item: str | None = Field(
        default=None, max_length=255, json_schema_extra={"commands_api_name": "item"}
    )
    diagnosis_codes: list[str] | None = Field(
        default=None, json_schema_extra={"commands_api_name": "indications"}
    )
    quantity: int | None = Field(default=None, ge=1)
    length_of_need: int | None = Field(default=None, ge=1, le=99)
    service_provider: ServiceProvider | None = Field(
        default=None, json_schema_extra={"commands_api_name": "send_to"}
    )
    ordering_provider_key: str | None = Field(
        default=None, json_schema_extra={"commands_api_name": "ordering_provider"}
    )

    @model_validator(mode="after")
    def _one_item(self) -> Self:
        if self.dme_product_id and self.free_text_item:
            raise ValueError("Set either dme_product_id or free_text_item, not both")
        return self

    @property
    def values(self) -> dict:
        """The Order DME command's field values."""
        values = super().values

        if self.is_dirty("service_provider") and self.service_provider:
            values["service_provider"] = self.service_provider.__dict__

        return values


__exports__ = ("OrderDmeCommand",)
