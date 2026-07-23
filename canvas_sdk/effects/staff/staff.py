import json
from datetime import date
from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects import Effect
from canvas_sdk.v1.data import Staff as StaffModel


class Staff(TrackableFieldsModel):
    """
    Effect to create, update, activate, deactivate, or delete a Staff record.

    Creating a Staff via the SDK invokes Staff.user_setup() on the home-app side,
    which provisions the associated CanvasUser. Updating roles invokes
    update_user_groups() so Django auth groups stay in sync. Plugins must not
    bypass either step.

    Example (create):
        Staff(
            first_name="Ada",
            last_name="Lovelace",
            email="ada@example.com",
            primary_practice_location_id="<uuid>",
            role_codes=["MD"],
        ).create()
    """

    class Meta:
        effect_type = "STAFF"

    id: str | UUID | None = None
    first_name: str | None = None
    last_name: str | None = None
    prefix: str | None = None
    suffix: str | None = None
    birth_date: date | None = None
    email: str | None = None
    phone: str | None = None
    fax: str | None = None
    npi_number: str | None = None
    group_npi_number: str | None = None
    tax_id: str | None = None
    tax_id_type: str | None = None
    bill_through_organization: bool | None = None
    primary_practice_location_id: str | UUID | None = None
    role_codes: list[str] | None = None
    personal_meeting_room_link: str | None = None
    photo_url: str | None = None
    signature_url: str | None = None
    active: bool | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if method == "create":
            if self.id:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "ID should not be set when creating new staff.",
                        self.id,
                    )
                )
            for required in ("first_name", "last_name", "email", "primary_practice_location_id"):
                if not getattr(self, required):
                    errors.append(
                        self._create_error_detail(
                            "missing",
                            f"Field '{required}' is required to create staff.",
                            getattr(self, required),
                        )
                    )

        if method in ("update", "delete", "activate", "deactivate"):
            if not self.id:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        f"Field 'id' is required to {method} staff.",
                        self.id,
                    )
                )
            elif not StaffModel.objects.filter(id=self.id).exists():
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Staff with id: {self.id} does not exist.",
                        self.id,
                    )
                )

        return errors

    def create(self) -> Effect:
        """Create new Staff."""
        self._validate_before_effect("create")
        return Effect(
            type=f"CREATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )

    def update(self) -> Effect:
        """Update Staff."""
        self._validate_before_effect("update")
        return Effect(
            type=f"UPDATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )

    def delete(self) -> Effect:
        """Delete Staff."""
        self._validate_before_effect("delete")
        return Effect(
            type=f"DELETE_{self.Meta.effect_type}",
            payload=json.dumps({"data": {"id": str(self.id)}}),
        )

    def activate(self) -> Effect:
        """Activate Staff (set active=True)."""
        self._validate_before_effect("activate")
        return Effect(
            type=f"ACTIVATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": {"id": str(self.id)}}),
        )

    def deactivate(self) -> Effect:
        """Deactivate Staff (set active=False)."""
        self._validate_before_effect("deactivate")
        return Effect(
            type=f"DEACTIVATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": {"id": str(self.id)}}),
        )


__exports__ = ("Staff",)
