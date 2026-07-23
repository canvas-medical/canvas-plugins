from canvas_sdk.effects.billing_catalog._base import BillingCatalogCrudEffect


class FeeSchedule(BillingCatalogCrudEffect):
    """Effect to create/update/delete a FeeSchedule line item (code + price).

    Prices are passed as strings to preserve decimal precision on the wire.
    """

    class Meta:
        effect_type = "FEE_SCHEDULE"

    _entity_label: str = "fee schedule entry"
    _create_required: tuple[str, ...] = ("code", "price")

    code: str | None = None
    code_system: str | None = None
    description: str | None = None
    price: str | None = None
    modifier: str | None = None
    active: bool | None = None


__exports__ = ("FeeSchedule",)
