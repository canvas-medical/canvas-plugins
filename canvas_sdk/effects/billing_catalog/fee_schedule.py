from datetime import date
from enum import StrEnum

from pydantic import Field

from canvas_sdk.effects._config_crud import ConfigCrudEffect


class FeeScheduleCodeSystem(StrEnum):
    """Code system of a fee schedule entry."""

    CPT = "CPT"
    INTERNAL = "INTERNAL"


class FeeSchedule(ConfigCrudEffect):
    """Create, update, or delete a fee schedule entry (a billable code and its default charge).

    ``id`` is the entry's ``dbid``. Amounts are strings to keep decimal precision.
    """

    class Meta:
        effect_type = "FEE_SCHEDULE"

    _entity_label: str = "fee schedule entry"
    _create_required: tuple[str, ...] = ("cpt_code", "name", "short_name")

    cpt_code: str | None = None
    name: str | None = None
    short_name: str | None = None
    charge_amount: str | None = None
    eff_date: date | None = None
    end_date: date | None = None
    code_system: FeeScheduleCodeSystem | None = Field(default=None, strict=False)
    ndc_code: str | None = None
    ndc_dosage: str | None = None
    ndc_measure: str | None = None


__exports__ = ("FeeSchedule", "FeeScheduleCodeSystem")
