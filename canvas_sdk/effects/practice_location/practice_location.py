import json
from typing import Any
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects import Effect
from canvas_sdk.v1.data.practicelocation import PracticeLocation as PracticeLocationModel


class PracticeLocation(TrackableFieldsModel):
    """
    Effect to create, update, or delete a Practice Location.

    Practice Locations are the physical sites a Canvas instance operates from.
    Creating one in home-app additionally bootstraps the location's default
    PracticeLocationSetting rows; the home-app interpreter mirrors that here.

    Example (create):
        PracticeLocation(
            full_name="Main Clinic",
            short_name="Main",
            place_of_service_code="11",
            phone="6175551212",
            email="info@example.com",
            tax_id="123456789",
            tax_id_type="E",
        ).create()

    Example (update):
        PracticeLocation(id="<uuid>", active=False).update()

    Example (delete):
        PracticeLocation(id="<uuid>").delete()
    """

    class Meta:
        effect_type = "PRACTICE_LOCATION"

    id: str | UUID | None = None
    full_name: str | None = None
    short_name: str | None = None
    place_of_service_code: str | None = None
    active: bool | None = None
    phone: str | None = None
    fax: str | None = None
    email: str | None = None
    npi_number: str | None = None
    bill_through_organization: bool | None = None
    tax_id: str | None = None
    tax_id_type: str | None = None
    billing_location_name: str | None = None
    group_npi_number: str | None = None
    taxonomy_number: str | None = None
    include_zz_qualifier: bool | None = None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if method == "create":
            if self.id:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "ID should not be set when creating a new practice location.",
                        self.id,
                    )
                )
            for required in ("full_name", "short_name", "place_of_service_code"):
                if not getattr(self, required):
                    errors.append(
                        self._create_error_detail(
                            "missing",
                            f"Field '{required}' is required to create a practice location.",
                            getattr(self, required),
                        )
                    )

        if method in ("update", "delete"):
            if not self.id:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        f"Field 'id' is required to {method} a practice location.",
                        self.id,
                    )
                )
            elif not PracticeLocationModel.objects.filter(id=self.id).exists():
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Practice location with id: {self.id} does not exist.",
                        self.id,
                    )
                )

        return errors

    def create(self) -> Effect:
        """Create a new Practice Location."""
        self._validate_before_effect("create")
        return Effect(
            type=f"CREATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )

    def update(self) -> Effect:
        """Update an existing Practice Location."""
        self._validate_before_effect("update")
        return Effect(
            type=f"UPDATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )

    def delete(self) -> Effect:
        """Delete an existing Practice Location."""
        self._validate_before_effect("delete")
        return Effect(
            type=f"DELETE_{self.Meta.effect_type}",
            payload=json.dumps({"data": {"id": str(self.id)}}),
        )


__exports__ = ("PracticeLocation",)
