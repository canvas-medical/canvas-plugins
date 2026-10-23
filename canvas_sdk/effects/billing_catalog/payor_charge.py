from datetime import date
from uuid import UUID

from canvas_sdk.effects._config_crud import ConfigCrudEffect


class PayorCharge(ConfigCrudEffect):
    """Create, update, or delete an insurer-specific charge for a fee schedule entry.

    ``id`` is the charge's ``dbid``; ``insurer_id`` is the insurer's id and
    ``fee_schedule_id`` the fee schedule entry's ``dbid``. Amounts are strings.
    """

    class Meta:
        effect_type = "PAYOR_CHARGE"

    _entity_label: str = "payor charge"
    _create_required: tuple[str, ...] = ("insurer_id", "fee_schedule_id", "charge_amount")

    insurer_id: str | UUID | None = None
    fee_schedule_id: int | None = None
    charge_amount: str | None = None
    eff_date: date | None = None
    end_date: date | None = None
    part_of_capitated_set: bool | None = None


__exports__ = ("PayorCharge",)
