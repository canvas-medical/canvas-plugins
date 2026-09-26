from uuid import UUID

from canvas_sdk.effects._config_crud import ConfigCrudEffect


class Vaccine(ConfigCrudEffect):
    """Create, update, or delete a vaccine catalog entry.

    ``id`` and ``insurer_id`` (the billing payer, optional) are ids of the vaccine
    and insurer.
    """

    class Meta:
        effect_type = "VACCINE"

    _entity_label: str = "vaccine"
    _create_required: tuple[str, ...] = ("cvx_code", "name", "short_name")

    cvx_code: str | None = None
    name: str | None = None
    short_name: str | None = None
    inventory: str | None = None
    ndc_code: str | None = None
    mvx_code: str | None = None
    route: str | None = None
    units: int | None = None
    active: bool | None = None
    insurer_id: str | UUID | None = None


__exports__ = ("Vaccine",)
