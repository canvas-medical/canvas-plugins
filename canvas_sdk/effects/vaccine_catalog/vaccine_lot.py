import json
from datetime import date
from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects import Effect


class VaccineLot(TrackableFieldsModel):
    """Effect to create, update, or delete a VaccineLot entry."""

    class Meta:
        effect_type = "VACCINE_LOT"

    id: str | UUID | None = None
    vaccine_id: str | UUID | None = None
    lot_number: str | None = None
    expiration_date: date | None = None
    quantity_on_hand: int | None = None
    active: bool | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        if method == "create":
            for required in ("vaccine_id", "lot_number", "expiration_date"):
                if not getattr(self, required):
                    errors.append(
                        self._create_error_detail(
                            "missing",
                            f"Field '{required}' is required to create a vaccine lot.",
                            getattr(self, required),
                        )
                    )
        if method in ("update", "delete") and not self.id:
            errors.append(
                self._create_error_detail(
                    "missing",
                    f"Field 'id' is required to {method} a vaccine lot.",
                    self.id,
                )
            )
        return errors

    def create(self) -> Effect:
        """Build the CREATE effect."""
        self._validate_before_effect("create")
        return Effect(
            type=f"CREATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )

    def update(self) -> Effect:
        """Build the UPDATE effect."""
        self._validate_before_effect("update")
        return Effect(
            type=f"UPDATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )

    def delete(self) -> Effect:
        """Build the DELETE effect (carries only the id)."""
        self._validate_before_effect("delete")
        return Effect(
            type=f"DELETE_{self.Meta.effect_type}",
            payload=json.dumps({"data": {"id": str(self.id)}}),
        )


__exports__ = ("VaccineLot",)
