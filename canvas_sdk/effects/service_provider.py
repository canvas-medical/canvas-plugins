import json
from typing import Any, cast
from uuid import UUID

from pydantic_core import InitErrorDetails

from canvas_sdk.base import TrackableFieldsModel
from canvas_sdk.effects import Effect
from canvas_sdk.v1.data.service_provider import ServiceProvider as ServiceProviderModel

# Fields that can be supplied on create and update. `id` and `science_contact_id`
# are handled separately (id keys the record; science_contact_id only informs the
# create-time dedup and is never updated through this effect).
UPDATABLE_FIELDS: tuple[str, ...] = (
    "first_name",
    "last_name",
    "specialty",
    "business_address",
    "business_phone",
    "business_fax",
    "practice_name",
    "notes",
    "is_active",
    "npi",
    "direct_address",
)

# The subset of fields that identify a provider for create-time deduplication.
# `last_name` is intentionally excluded: organization providers legitimately have
# no last name, so requiring it would reject them.
CREATE_REQUIRED_FIELDS: tuple[str, ...] = ("first_name", "specialty", "business_address")

# NOT NULL identifier columns that must never be set to null on update. `last_name`
# is excluded (it is legitimately blank-able and is coerced to "" downstream);
# `business_address` is excluded (it is a nullable column).
UPDATE_NON_NULLABLE_FIELDS: tuple[str, ...] = ("first_name", "specialty")

NPI_LENGTH = cast(int, ServiceProviderModel._meta.get_field("npi").max_length)
DIRECT_ADDRESS_MAX_LENGTH = cast(
    int, ServiceProviderModel._meta.get_field("direct_address").max_length
)


def _is_valid_npi(npi: str) -> bool:
    """Return whether the value is exactly 10 ASCII digits.

    ASCII too, since isdigit() alone accepts non-ASCII numerals.
    """
    return len(npi) == NPI_LENGTH and npi.isascii() and npi.isdigit()


def _is_valid_direct_address(direct_address: str) -> bool:
    """Return whether the value fits the column."""
    return len(direct_address) <= DIRECT_ADDRESS_MAX_LENGTH


class ServiceProvider(TrackableFieldsModel):
    """
    Effect to create, update, or deactivate a ServiceProvider.

    Example (create):
        ServiceProvider(
            first_name="Jane",
            last_name="Doe",
            specialty="Cardiology",
            business_address="123 Main St",
            npi="1234567890",
        ).create()

    Example (update):
        ServiceProvider(id="existing-provider-uuid", notes="Prefers fax").update()

    Example (reactivate a deactivated provider):
        # Reactivation is always explicit — set is_active=True on update().
        ServiceProvider(id="existing-provider-uuid", is_active=True).update()

    Example (deactivate):
        ServiceProvider(id="existing-provider-uuid").deactivate()
    """

    class Meta:
        effect_type = "SERVICE_PROVIDER"

    id: str | UUID | None = None
    first_name: str | None = None
    last_name: str | None = None
    specialty: str | None = None
    business_address: str | None = None
    business_phone: str | None = None
    business_fax: str | None = None
    practice_name: str | None = None
    notes: str | None = None
    is_active: bool | None = None
    npi: str | None = None
    direct_address: str | None = None
    science_contact_id: int | None = None

    @property
    def values(self) -> dict[str, Any]:
        """Build the create payload: the required fields plus ONLY the optional fields the
        author explicitly set.

        Omitted optional fields are absent from the payload (never sent as null or a
        forced default), so a create can never null-clobber an existing provider's
        fields nor silently reactivate a deactivated one — reactivation stays explicit
        via ``update(is_active=True)``.
        """
        data: dict[str, Any] = {field: getattr(self, field) for field in CREATE_REQUIRED_FIELDS}
        for field in UPDATABLE_FIELDS:
            if field not in CREATE_REQUIRED_FIELDS and self.is_dirty(field):
                data[field] = getattr(self, field)
        if self.science_contact_id is not None:
            data["science_contact_id"] = self.science_contact_id
        return data

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if method == "create":
            if self.id:
                errors.append(
                    self._create_error_detail(
                        "value",
                        "ID should not be set when creating a new service provider.",
                        self.id,
                    )
                )
            for field in CREATE_REQUIRED_FIELDS:
                if not getattr(self, field):
                    errors.append(
                        self._create_error_detail(
                            "missing",
                            f"Field '{field}' is required to create a service provider.",
                            getattr(self, field),
                        )
                    )

        if method in ("update", "deactivate"):
            if not self.id:
                errors.append(
                    self._create_error_detail(
                        "missing",
                        f"Field 'id' is required to {method} a service provider.",
                        self.id,
                    )
                )
            elif not ServiceProviderModel.objects.filter(id=self.id).exists():
                errors.append(
                    self._create_error_detail(
                        "value",
                        f"Service provider with id: {self.id} does not exist.",
                        self.id,
                    )
                )

        if method == "update":
            for field in UPDATE_NON_NULLABLE_FIELDS:
                if self.is_dirty(field) and getattr(self, field) is None:
                    errors.append(
                        self._create_error_detail(
                            "value",
                            f"Field '{field}' cannot be set to null when updating a "
                            "service provider.",
                            getattr(self, field),
                        )
                    )

        # Only checked when npi is actually sent, so omitting it or clearing it stays valid.
        if (
            method in ("create", "update")
            and self.is_dirty("npi")
            and self.npi is not None
            and not _is_valid_npi(self.npi)
        ):
            errors.append(
                self._create_error_detail(
                    "value",
                    "Field 'npi' must be exactly 10 digits.",
                    self.npi,
                )
            )

        if (
            method in ("create", "update")
            and self.is_dirty("direct_address")
            and self.direct_address is not None
            and not _is_valid_direct_address(self.direct_address)
        ):
            errors.append(
                self._create_error_detail(
                    "value",
                    f"Field 'direct_address' must be at most {DIRECT_ADDRESS_MAX_LENGTH} "
                    "characters.",
                    self.direct_address,
                )
            )

        return errors

    def create(self) -> Effect:
        """Create a new ServiceProvider."""
        self._validate_before_effect("create")

        return Effect(
            type=f"CREATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": self.values}),
        )

    def update(self) -> Effect:
        """Update an existing ServiceProvider, sending only the fields that were set."""
        self._validate_before_effect("update")

        data: dict[str, Any] = {"id": str(self.id)}
        for field in UPDATABLE_FIELDS:
            if self.is_dirty(field):
                data[field] = getattr(self, field)

        return Effect(
            type=f"UPDATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": data}),
        )

    def deactivate(self) -> Effect:
        """Soft-deactivate an existing ServiceProvider (sets is_active=False)."""
        self._validate_before_effect("deactivate")

        return Effect(
            type=f"DEACTIVATE_{self.Meta.effect_type}",
            payload=json.dumps({"data": {"id": str(self.id)}}),
        )


__exports__ = ("ServiceProvider",)
