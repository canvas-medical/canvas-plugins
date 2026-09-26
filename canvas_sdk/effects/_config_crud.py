import json
from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects import Effect


class ConfigCrudEffect(TrackableFieldsModel):
    """Create / update / delete plumbing shared by the instance configuration effects.

    Subclasses set ``Meta.effect_type`` to the protobuf base name (``CREATE_<name>``,
    ``UPDATE_<name>``, ``DELETE_<name>``) and ``_create_required`` to the fields a
    create must carry. Update and delete identify the record by ``id``.
    """

    class Meta:
        effect_type = "CONFIG_ENTRY"

    id: str | UUID | int | None = None

    _entity_label: str = "record"
    _create_required: tuple[str, ...] = ()

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)
        if method == "create":
            for required in self._create_required:
                if getattr(self, required) in (None, ""):
                    errors.append(
                        self._create_error_detail(
                            "missing",
                            f"Field '{required}' is required to create a {self._entity_label}.",
                            getattr(self, required),
                        )
                    )
        if method in ("update", "delete") and not self.id:
            errors.append(
                self._create_error_detail(
                    "missing",
                    f"Field 'id' is required to {method} a {self._entity_label}.",
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


__exports__ = ("ConfigCrudEffect",)
