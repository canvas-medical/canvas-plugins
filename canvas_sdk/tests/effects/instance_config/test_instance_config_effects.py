import json
from datetime import date
from typing import Any

import pytest
from pydantic import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects import Effect
from canvas_sdk.effects._config_crud import ConfigCrudEffect
from canvas_sdk.effects.billing_catalog import (
    Discount,
    FeeSchedule,
    PayorCharge,
    PostingRule,
    PostingRuleBehavior,
)
from canvas_sdk.effects.codings import (
    ConsentExpirationRule,
    PatientConsentCoding,
    PatientConsentRejectionCoding,
    ReasonForVisitSettingCoding,
)
from canvas_sdk.effects.insurer import Insurer, InsurerType
from canvas_sdk.effects.note_type import NoteType, NoteTypeCategory
from canvas_sdk.effects.practice_location import (
    PracticeLocation,
    PracticeLocationAddress,
    PracticeLocationSetting,
    PracticeLocationSettingName,
)
from canvas_sdk.effects.team import CareTeamRole, Team, TeamMember
from canvas_sdk.effects.vaccine_catalog import Vaccine, VaccineLot

VALID_CREATES: list[tuple[ConfigCrudEffect, str]] = [
    (
        PracticeLocation(full_name="Main Street Clinic", short_name="Main"),
        "PRACTICE_LOCATION",
    ),
    (
        PracticeLocationAddress(
            practice_location_id="9f2c6f6e-8a39-4a61-8d5e-3f1d8a0d2b10",
            line1="1 Main St",
            city="Oakland",
            state_code="CA",
            postal_code="94612",
            country="US",
        ),
        "PRACTICE_LOCATION_ADDRESS",
    ),
    (Team(name="Front Desk"), "TEAM"),
    (CareTeamRole(system="http://snomed.info/sct", display="Case manager"), "CARE_TEAM_ROLE"),
    (
        NoteType(
            name="Nutrition visit",
            display="Nutrition visit",
            code="NUTR",
            system="INTERNAL",
            category=NoteTypeCategory.ENCOUNTER,
            icon="apple",
        ),
        "NOTE_TYPE",
    ),
    (
        PatientConsentCoding(
            system="INTERNAL", display="Telehealth", expiration_rule=ConsentExpirationRule.NEVER
        ),
        "PATIENT_CONSENT_CODING",
    ),
    (
        PatientConsentRejectionCoding(system="INTERNAL", display="Declined"),
        "PATIENT_CONSENT_REJECTION_CODING",
    ),
    (
        ReasonForVisitSettingCoding(system="INTERNAL", display="Annual physical"),
        "REASON_FOR_VISIT_SETTING_CODING",
    ),
    (Insurer(name="Acme Health", transactor_type=InsurerType.COMMERCIAL), "INSURER"),
    (FeeSchedule(cpt_code="99213", name="Office visit", short_name="OV"), "FEE_SCHEDULE"),
    (
        Discount(name="Prompt pay", adjustment_group="CO", adjustment_code="45", discount="10"),
        "DISCOUNT",
    ),
    (
        PayorCharge(
            insurer_id="1c0e5a52-2b4a-4b38-9d1c-0c6a7c2f9f11",
            fee_schedule_id=12,
            charge_amount="95.00",
        ),
        "PAYOR_CHARGE",
    ),
    (
        PostingRule(
            description="CO-45 write-off",
            adjustment_group="CO",
            behavior=PostingRuleBehavior.WRITE_OFF,
        ),
        "POSTING_RULE",
    ),
    (Vaccine(cvx_code="208", name="COVID-19 vaccine", short_name="COVID-19"), "VACCINE"),
    (VaccineLot(lot_number="LOT-1", starting_inventory=10), "VACCINE_LOT"),
]


@pytest.mark.parametrize(("effect", "base_name"), VALID_CREATES)
def test_create_update_delete_effect_types(effect: ConfigCrudEffect, base_name: str) -> None:
    """Each effect builds CREATE/UPDATE/DELETE effects whose types exist in the protobuf enum."""
    created = effect.create()
    assert created.type == EffectType.Value(f"CREATE_{base_name}")
    assert json.loads(created.payload)["data"] == json.loads(json.dumps(effect.values))

    effect.id = "42"
    assert effect.update().type == EffectType.Value(f"UPDATE_{base_name}")
    deleted = effect.delete()
    assert deleted.type == EffectType.Value(f"DELETE_{base_name}")
    assert json.loads(deleted.payload) == {"data": {"id": "42"}}


@pytest.mark.parametrize(("effect", "_base_name"), VALID_CREATES)
def test_create_requires_fields(effect: ConfigCrudEffect, _base_name: str) -> None:
    """Creating an effect with none of its fields set names every required field."""
    empty = type(effect)()
    with pytest.raises(ValidationError) as exc_info:
        empty.create()
    messages = " ".join(error["msg"] for error in exc_info.value.errors())
    for required in effect._create_required:
        assert f"'{required}'" in messages


@pytest.mark.parametrize("method", ["update", "delete"])
def test_update_and_delete_require_id(method: str) -> None:
    """Update and delete refuse to build an effect without an id."""
    with pytest.raises(ValidationError, match="'id' is required"):
        getattr(Team(name="Front Desk"), method)()


def test_dates_and_enums_serialize_as_strings() -> None:
    """Dates serialize as ISO strings and enums as their values."""
    lot = VaccineLot(
        lot_number="LOT-2",
        starting_inventory=5,
        expiration_date=date(2027, 1, 31),
    )
    assert json.loads(lot.create().payload)["data"]["expiration_date"] == "2027-01-31"

    rule = PostingRule(
        description="Transfer", adjustment_group="PR", behavior=PostingRuleBehavior.TRANSFER
    )
    assert json.loads(rule.create().payload)["data"]["behavior"] == "transfer"


def test_note_type_rejects_system_managed_category() -> None:
    """Only encounter and schedule_event note types can be written."""
    with pytest.raises(ValidationError):
        NoteType(category="letter")  # type: ignore[arg-type]


def test_practice_location_setting_upsert() -> None:
    """A practice location setting upserts one known setting name."""
    setting = PracticeLocationSetting(
        practice_location_id="9f2c6f6e-8a39-4a61-8d5e-3f1d8a0d2b10",
        name=PracticeLocationSettingName.SERVICE_AREA_ZIP_CODES,
        value=["94612"],
    )
    effect = setting.upsert()
    assert effect.type == EffectType.UPSERT_PRACTICE_LOCATION_SETTING
    assert json.loads(effect.payload)["data"] == {
        "practice_location_id": "9f2c6f6e-8a39-4a61-8d5e-3f1d8a0d2b10",
        "name": "serviceAreaZipCodes",
        "value": ["94612"],
    }


def test_practice_location_setting_rejects_unknown_name() -> None:
    """Setting names outside the known per-location settings are rejected."""
    with pytest.raises(ValidationError):
        PracticeLocationSetting(
            practice_location_id="x",
            name="googleAPICredentials",  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    ("method", "effect_type"),
    [("assign", EffectType.ASSIGN_TEAM_MEMBER), ("remove", EffectType.REMOVE_TEAM_MEMBER)],
)
def test_team_member(method: str, effect_type: int) -> None:
    """Team membership effects carry the team id and the staff id."""
    effect: Effect = getattr(TeamMember(team_id="t-1", staff_id="s-1"), method)()
    assert effect.type == effect_type
    assert json.loads(effect.payload) == {"data": {"team_id": "t-1", "staff_id": "s-1"}}


@pytest.mark.parametrize("missing", ["team_id", "staff_id"])
def test_team_member_requires_both_ids(missing: str) -> None:
    """Team membership needs both ids."""
    fields: dict[str, Any] = {"team_id": "t-1", "staff_id": "s-1"}
    del fields[missing]
    with pytest.raises(ValidationError, match=f"'{missing}' is required"):
        TeamMember(**fields).assign()
