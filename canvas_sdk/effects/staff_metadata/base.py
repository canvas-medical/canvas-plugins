import json
from typing import Any

from pydantic_core import InitErrorDetails

from canvas_sdk.effects import Effect
from canvas_sdk.effects.metadata import BaseMetadata
from canvas_sdk.v1.data import Staff


class StaffMetadata(BaseMetadata):
    """Effect to upsert or delete a Staff Metadata record."""

    class Meta:
        effect_type = "STAFF_METADATA"

    staff_id: str

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if not Staff.objects.filter(id=self.staff_id).exists():
            errors.append(
                self._create_error_detail(
                    "staff_id",
                    f"Staff with id: {self.staff_id} does not exist.",
                    self.staff_id,
                )
            )

        return errors

    def delete(self) -> Effect:
        """Delete a Staff Metadata record by (staff_id, key)."""
        self._validate_before_effect("delete")

        return Effect(
            type=f"DELETE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )


__exports__ = ("StaffMetadata",)
