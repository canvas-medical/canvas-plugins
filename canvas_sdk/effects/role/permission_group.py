import json
from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects import Effect


class PermissionGroup(TrackableFieldsModel):
    """
    Effect to create, update, or delete a PermissionGroup.
    """

    class Meta:
        effect_type = "PERMISSION_GROUP"

    id: str | UUID | None = None
    name: str | None = None
    internal_code: str | None = None
    description: str | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        if method == "create":
            for required in ("name", "internal_code"):
                if not getattr(self, required):
                    errors.append(
                        self._create_error_detail(
                            "missing",
                            f"Field '{required}' is required to create a permission group.",
                            getattr(self, required),
                        )
                    )
        if method in ("update", "delete") and not self.id:
            errors.append(
                self._create_error_detail(
                    "missing",
                    f"Field 'id' is required to {method} a permission group.",
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


class RolePermissionGroup(TrackableFieldsModel):
    """
    Effect to attach or detach a PermissionGroup from a Role.
    """

    class Meta:
        effect_type = "ROLE_PERMISSION_GROUP"

    role_id: str | UUID | None = None
    permission_group_id: str | UUID | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        if method in ("assign", "remove"):
            for required in ("role_id", "permission_group_id"):
                if not getattr(self, required):
                    errors.append(
                        self._create_error_detail(
                            "missing",
                            f"Field '{required}' is required to {method} a role permission group.",
                            getattr(self, required),
                        )
                    )
        return errors

    def assign(self) -> Effect:
        """Build the ASSIGN effect (attach the relation)."""
        self._validate_before_effect("assign")
        return Effect(
            type=f"ASSIGN_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )

    def remove(self) -> Effect:
        """Build the REMOVE effect (detach the relation)."""
        self._validate_before_effect("remove")
        return Effect(
            type=f"REMOVE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )


__exports__ = ("PermissionGroup", "RolePermissionGroup")
