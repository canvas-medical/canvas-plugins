from typing import Any

from canvas_sdk.effects.metadata import BaseMetadata
from canvas_sdk.v1.data import Command


class _CommandMetadata(BaseMetadata):
    """Effect to upsert a Command Metadata record."""

    class Meta:
        effect_type = "COMMAND_METADATA"

    command_id: str
    schema_key: str

    def _get_error_details(self, method: Any) -> list:
        errors = super()._get_error_details(method)

        if not Command.objects.filter(id=self.command_id, schema_key=self.schema_key).exists():
            errors.append(
                self._create_error_detail(
                    "command_id",
                    f"{self.schema_key} with id: {self.command_id} does not exist.",
                    self.command_id,
                )
            )

        return errors


__exports__ = ()
