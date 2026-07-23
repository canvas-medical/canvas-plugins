import json
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import Field
from pydantic_core import InitErrorDetails

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects import Effect


class AddressUse(StrEnum):
    """Tag distinguishing the purpose of an address attached to a parent record."""

    WORK = "work"
    BILLING = "billing"
    HOME = "home"
    TEMP = "temp"
    OLD = "old"


class Address(TrackableFieldsModel):
    """
    Effect to create, update, or delete an Address attached to a parent record
    (Organization, PracticeLocation, Staff, or Patient). The Notion gap analysis
    calls out multi-address management as a single SDK primitive worth shipping
    so plugin authors don't reinvent work-vs-billing dispatch.

    The parent is identified by `parent_type` ("organization" / "practice_location"
    / "staff" / "patient") and `parent_id`. Use `use` to tag work vs billing.

    Example (create work address on a practice location):
        Address(
            parent_type="practice_location",
            parent_id="<uuid>",
            use=AddressUse.WORK,
            line1="123 Main St",
            city="Boston",
            state="MA",
            postal_code="02101",
        ).create()
    """

    class Meta:
        effect_type = "ADDRESS"

    id: str | UUID | None = None

    parent_type: str | None = None
    parent_id: str | UUID | None = None

    use: AddressUse | None = Field(default=None, strict=False)
    line1: str | None = None
    line2: str | None = None
    city: str | None = None
    district: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str = "US"

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if method == "create":
            if self.id:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "ID should not be set when creating a new address.",
                        self.id,
                    )
                )
            for required in ("parent_type", "parent_id", "line1", "city", "state", "postal_code"):
                if not getattr(self, required):
                    errors.append(
                        self._create_error_detail(
                            "missing",
                            f"Field '{required}' is required to create an address.",
                            getattr(self, required),
                        )
                    )

        if method in ("update", "delete") and not self.id:
            errors.append(
                self._create_error_detail(
                    "missing",
                    f"Field 'id' is required to {method} an address.",
                    self.id,
                )
            )

        return errors

    def create(self) -> Effect:
        """Create a new Address."""
        self._validate_before_effect("create")
        return Effect(
            type=f"CREATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )

    def update(self) -> Effect:
        """Update an existing Address."""
        self._validate_before_effect("update")
        return Effect(
            type=f"UPDATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )

    def delete(self) -> Effect:
        """Delete an Address."""
        self._validate_before_effect("delete")
        return Effect(
            type=f"DELETE_{self.Meta.effect_type}",
            payload=json.dumps({"data": {"id": str(self.id)}}),
        )


__exports__ = ("Address", "AddressUse")
