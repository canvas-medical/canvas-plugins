from typing import Any

from pydantic_core import InitErrorDetails

from canvas_sdk.effects.metadata import BaseMetadata
from canvas_sdk.v1.data import Staff


class StaffMetadata(BaseMetadata):
    """Effect to upsert a Staff Metadata record."""

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


__exports__ = ("StaffMetadata",)
