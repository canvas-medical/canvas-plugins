from canvas_sdk.effects.billing_catalog._base import BillingCatalogCrudEffect


class Discount(BillingCatalogCrudEffect):
    """Effect to create/update/delete a Discount template.

    Percentages and fixed amounts are passed as strings to preserve decimal
    precision on the wire.
    """

    class Meta:
        effect_type = "DISCOUNT"

    _entity_label: str = "discount"
    _create_required: tuple[str, ...] = ("name",)

    name: str | None = None
    description: str | None = None
    percentage: str | None = None
    fixed_amount: str | None = None
    active: bool | None = None


__exports__ = ("Discount",)
