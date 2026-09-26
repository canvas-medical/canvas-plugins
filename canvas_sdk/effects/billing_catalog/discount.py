from canvas_sdk.effects._config_crud import ConfigCrudEffect


class Discount(ConfigCrudEffect):
    """Create, update, or delete a discount (a percentage adjustment with its adjustment codes).

    ``id`` is the discount's ``dbid``. ``discount`` is a percentage passed as a string.
    """

    class Meta:
        effect_type = "DISCOUNT"

    _entity_label: str = "discount"
    _create_required: tuple[str, ...] = ("name", "adjustment_group", "adjustment_code")

    name: str | None = None
    adjustment_group: str | None = None
    adjustment_code: str | None = None
    discount: str | None = None


__exports__ = ("Discount",)
