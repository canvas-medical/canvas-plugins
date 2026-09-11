from uuid import UUID

from canvas_sdk.effects.billing_catalog._base import BillingCatalogCrudEffect


class PayorCharge(BillingCatalogCrudEffect):
    """Effect to create/update/delete a payor-specific charge override.

    Prices are passed as strings to preserve decimal precision on the wire.
    """

    class Meta:
        effect_type = "PAYOR_CHARGE"

    _entity_label: str = "payor charge"
    _create_required: tuple[str, ...] = ("insurer_id", "code", "price")

    insurer_id: str | UUID | None = None
    fee_schedule_id: str | UUID | None = None
    code: str | None = None
    code_system: str | None = None
    description: str | None = None
    price: str | None = None
    modifier: str | None = None
    active: bool | None = None


__exports__ = ("PayorCharge",)
