from canvas_sdk.effects.billing_catalog._base import BillingCatalogCrudEffect


class PostingRule(BillingCatalogCrudEffect):
    """Effect to create/update/delete a PostingRule used in ERA posting."""

    class Meta:
        effect_type = "POSTING_RULE"

    _entity_label: str = "posting rule"
    _create_required: tuple[str, ...] = ("name", "action")

    name: str | None = None
    description: str | None = None
    action: str | None = None
    conditions: dict | None = None
    priority: int | None = None
    active: bool | None = None


__exports__ = ("PostingRule",)
