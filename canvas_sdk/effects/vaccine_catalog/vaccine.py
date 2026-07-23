import json
from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects import Effect


class Vaccine(TrackableFieldsModel):
    """Effect to create, update, or delete a Vaccine catalog entry."""

    class Meta:
        effect_type = "VACCINE"

    id: str | UUID | None = None
    name: str | None = None
    cvx_code: str | None = None
    cvx_display: str | None = None
    manufacturer: str | None = None
    active: bool | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        if method == "create":
            for required in ("name", "cvx_code"):
                if not getattr(self, required):
                    errors.append(
                        self._create_error_detail(
                            "missing",
                            f"Field '{required}' is required to create a vaccine.",
                            getattr(self, required),
                        )
                    )
        if method in ("update", "delete") and not self.id:
            errors.append(
                self._create_error_detail(
                    "missing",
                    f"Field 'id' is required to {method} a vaccine.",
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


__exports__ = ("Vaccine",)
