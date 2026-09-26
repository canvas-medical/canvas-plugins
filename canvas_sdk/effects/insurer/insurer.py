from enum import StrEnum

from pydantic import Field

from canvas_sdk.effects._config_crud import ConfigCrudEffect


class InsurerType(StrEnum):
    """Kind of payer."""

    COMMERCIAL = "commercial"
    WORKERS_COMP = "workerscomp"
    CHAMPUS = "champus"
    MEDICAID = "medicaid"
    MEDICARE = "medicare"
    MEDICARE_ADVANTAGE = "medicare_advantage"
    CHIP = "CHIP"
    AUTOMOBILE = "automobile"
    EMPLOYER = "employer"
    DIRECT_CARE = "direct_care"
    BCBS = "bcbs"


class Insurer(ConfigCrudEffect):
    """Create, update, or delete an insurer (payer). ``id`` is the insurer's id."""

    class Meta:
        effect_type = "INSURER"

    _entity_label: str = "insurer"
    _create_required: tuple[str, ...] = ("name",)

    name: str | None = None
    payer_id: str | None = None
    type: str | None = None
    transactor_type: InsurerType | None = Field(default=None, strict=False)
    description: str | None = None
    state: str | None = None
    active: bool | None = None
    clearinghouse_payer: bool | None = None
    institutional: bool | None = None
    institutional_enrollment_req: bool | None = None
    professional: bool | None = None
    professional_enrollment_req: bool | None = None
    era: bool | None = None
    era_enrollment_req: bool | None = None
    eligibility: bool | None = None
    eligibility_enrollment_req: bool | None = None
    workers_comp: bool | None = None
    secondary_support: bool | None = None
    claim_fee: bool | None = None
    remit_fee: bool | None = None
    use_provider_for_eligibility: bool | None = None
    coverage_types: list[str] | None = None


__exports__ = ("Insurer", "InsurerType")
