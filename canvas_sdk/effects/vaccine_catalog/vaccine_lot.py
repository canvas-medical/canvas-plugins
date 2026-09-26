from datetime import date
from uuid import UUID

from canvas_sdk.effects._config_crud import ConfigCrudEffect


class VaccineLot(ConfigCrudEffect):
    """Create, update, or delete a vaccine lot.

    ``id`` and ``vaccine_id`` are ids of the lot and its vaccine. On-hand
    inventory is computed from ``starting_inventory`` plus ``quantity_adjustment``
    minus doses used.
    """

    class Meta:
        effect_type = "VACCINE_LOT"

    _entity_label: str = "vaccine lot"
    _create_required: tuple[str, ...] = ("lot_number", "starting_inventory")

    vaccine_id: str | UUID | None = None
    lot_number: str | None = None
    ndc_code: str | None = None
    mvx_code: str | None = None
    expiration_date: date | None = None
    diluent_lot_number: str | None = None
    diluent_expiration_date: date | None = None
    starting_inventory: int | None = None
    quantity_adjustment: int | None = None
    adjustment_notes: str | None = None


__exports__ = ("VaccineLot",)
