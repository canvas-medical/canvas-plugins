import json

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects import Effect


class CreateStaffExternalIdentifier(TrackableFieldsModel):
    """Effect to create a Staff External Identifier record."""

    class Meta:
        effect_type = "STAFF_EXTERNAL_IDENTIFIER"

    value: str
    system: str | None = None
    staff_id: str | None = None

    @property
    def values(self) -> dict[str, str | None]:
        """Return the values of the external identifier."""
        return {
            "value": self.value,
            "system": self.system,
            "staff_id": self.staff_id,
        }

    def create(self) -> Effect:
        """Create a new Staff External Identifier."""
        self._validate_before_effect("create")

        return Effect(
            type=f"CREATE_{self.Meta.effect_type}",
            payload=json.dumps(
                {
                    "data": self.values,
                }
            ),
        )


__exports__ = ("CreateStaffExternalIdentifier",)
