import json
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects import Effect


class RoleDomain(StrEnum):
    """api.Role.DOMAIN_CHOICES."""

    CLINICAL = "CLI"
    ADMINISTRATIVE = "ADM"
    HYBRID = "HYB"


class Role(TrackableFieldsModel):
    """
    Effect to create, update, or delete a Role.

    Note: changing a Role's `domain` on the home-app side fans out via
    Role.update_user_groups() so every staff member with that role gets
    their CanvasUser groups recomputed. The home-app interpreter is
    responsible for invoking it.
    """

    class Meta:
        effect_type = "ROLE"

    id: str | UUID | None = None
    name: str | None = None
    internal_code: str | None = None
    public_abbreviation: str | None = None
    domain: RoleDomain | None = Field(default=None, strict=False)
    domain_privilege_level: int | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if method == "create":
            for required in ("name", "internal_code", "domain"):
                if not getattr(self, required):
                    errors.append(
                        self._create_error_detail(
                            "missing",
                            f"Field '{required}' is required to create a role.",
                            getattr(self, required),
                        )
                    )

        if method in ("update", "delete") and not self.id:
            errors.append(
                self._create_error_detail(
                    "missing",
                    f"Field 'id' is required to {method} a role.",
                    self.id,
                )
            )

        return errors

    def create(self) -> Effect:
        """Create a Role."""
        self._validate_before_effect("create")
        return Effect(
            type=f"CREATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )

    def update(self) -> Effect:
        """Update a Role."""
        self._validate_before_effect("update")
        return Effect(
            type=f"UPDATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )

    def delete(self) -> Effect:
        """Delete a Role."""
        self._validate_before_effect("delete")
        return Effect(
            type=f"DELETE_{self.Meta.effect_type}",
            payload=json.dumps({"data": {"id": str(self.id)}}),
        )


class StaffRole(TrackableFieldsModel):
    """
    Effect to assign or remove a Role from a Staff member. The home-app side
    invokes StaffRole.update_user_groups() automatically.

    Example:
        StaffRole(staff_id="<uuid>", role_code="MD").assign()
        StaffRole(staff_id="<uuid>", role_code="MD").remove()
    """

    class Meta:
        effect_type = "STAFF_ROLE"

    staff_id: str | UUID | None = None
    role_code: str | None = None
    role_id: str | UUID | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        if method in ("assign", "remove"):
            if not self.staff_id:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        f"Field 'staff_id' is required to {method} a staff role.",
                        self.staff_id,
                    )
                )
            if not (self.role_code or self.role_id):
                errors.append(
                    self._create_error_detail(
                        "missing",
                        "Either 'role_code' or 'role_id' is required.",
                        None,
                    )
                )
        return errors

    def assign(self) -> Effect:
        """Assign a role to a staff member."""
        self._validate_before_effect("assign")
        return Effect(
            type=f"ASSIGN_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )

    def remove(self) -> Effect:
        """Remove a role from a staff member."""
        self._validate_before_effect("remove")
        return Effect(
            type=f"REMOVE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )


__exports__ = ("Role", "RoleDomain", "StaffRole")
