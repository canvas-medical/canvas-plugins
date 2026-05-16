import json
from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects import Effect
from canvas_sdk.v1.data import Staff
from canvas_sdk.v1.data.staff import StaffExternalIdentifier as StaffExternalIdentifierModel


class StaffExternalIdentifier(TrackableFieldsModel):
    """
    Effect to create, update, or delete a Staff External Identifier.

    Example (create):
        StaffExternalIdentifier(
            staff_id="4150cd20de8a470aa570a852859ac87e",
            system="https://hr.example.com/",
            value="EMP-001234",
        ).create()

    Example (update):
        StaffExternalIdentifier(
            id="existing-identifier-uuid",
            value="EMP-005678",
        ).update()

    Example (delete):
        StaffExternalIdentifier(id="existing-identifier-uuid").delete()
    """

    class Meta:
        effect_type = "STAFF_EXTERNAL_IDENTIFIER"

    id: str | UUID | None = None
    value: str | None = None
    system: str | None = None
    staff_id: str | UUID | None = None

    @property
    def values(self) -> dict[str, Any]:
        """Return the values of the external identifier."""
        return {
            "id": str(self.id) if self.id is not None else None,
            "value": self.value,
            "system": self.system,
            "staff_id": str(self.staff_id) if self.staff_id is not None else None,
        }

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if method == "create":
            if self.id:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "ID should not be set when creating a new staff external identifier.",
                        self.id,
                    )
                )
            if not self.value:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'value' is required to create a staff external identifier.",
                        self.value,
                    )
                )
            if not self.staff_id:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Field 'staff_id' is required to create a staff external identifier.",
                        self.staff_id,
                    )
                )
            elif not Staff.objects.filter(id=self.staff_id).exists():
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Staff with id: {self.staff_id} does not exist.",
                        self.staff_id,
                    )
                )

        if method in ("update", "delete"):
            if not self.id:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        f"Field 'id' is required to {method} a staff external identifier.",
                        self.id,
                    )
                )
            elif not StaffExternalIdentifierModel.objects.filter(id=self.id).exists():
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Staff external identifier with id: {self.id} does not exist.",
                        self.id,
                    )
                )

        return errors

    def create(self) -> Effect:
        """Create a new Staff External Identifier."""
        self._validate_before_effect("create")

        return Effect(
            type=f"CREATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )

    def update(self) -> Effect:
        """Update an existing Staff External Identifier."""
        self._validate_before_effect("update")

        return Effect(
            type=f"UPDATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )

    def delete(self) -> Effect:
        """Delete an existing Staff External Identifier."""
        self._validate_before_effect("delete")

        return Effect(
            type=f"DELETE_{self.Meta.effect_type}",
            payload=json.dumps({"data": {"id": str(self.id)}}),
        )


__exports__ = ("StaffExternalIdentifier",)
