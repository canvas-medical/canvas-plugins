"""Patch-coverage tests for Instance Configuration CRUD effects.

The companion `test_instance_config_effects.py` covers the create-happy-path
plus a handful of specials. This file fills in the gaps the codecov/patch
check flagged:

- The three coding subclasses (PatientConsentCoding /
  PatientConsentRejectionCoding / ReasonForVisitSettingCoding) had no test
  at all, so their shared `_base.py` sat at 58% patch coverage.
- The update / delete branches for every CRUD effect (only PracticeLocation
  exercised them before).
- The "missing required field" validation branches in _get_error_details.
- FormField's optional widget-config keys (`help_text`, `group`,
  `placeholder`, `min_value`, `max_value`) — the to_dict() emit-when-set
  branches that were only covered for `widget_config`.
"""

import json
from collections.abc import Generator
from unittest.mock import patch

import pytest
from pydantic_core import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.address import Address
from canvas_sdk.effects.billing_catalog import Discount, FeeSchedule, PayorCharge, PostingRule
from canvas_sdk.effects.codings import (
    PatientConsentCoding,
    PatientConsentRejectionCoding,
    ReasonForVisitSettingCoding,
)
from canvas_sdk.effects.form import FormField, InputType
from canvas_sdk.effects.insurer import Insurer
from canvas_sdk.effects.note_type import NoteType
from canvas_sdk.effects.practice_location import PracticeLocationSetting
from canvas_sdk.effects.role import (
    PermissionGroup,
    Role,
    RolePermissionGroup,
    StaffRole,
)
from canvas_sdk.effects.staff import Staff, StaffLicense
from canvas_sdk.effects.team import CareTeamRole, Team, TeamMember
from canvas_sdk.effects.vaccine_catalog import Vaccine, VaccineLot

# ---------- Codings (shared _base.py) ----------

CODING_CLASSES = [
    (PatientConsentCoding, "PATIENT_CONSENT_CODING"),
    (PatientConsentRejectionCoding, "PATIENT_CONSENT_REJECTION_CODING"),
    (ReasonForVisitSettingCoding, "REASON_FOR_VISIT_SETTING_CODING"),
]


@pytest.mark.parametrize("cls,prefix", CODING_CLASSES)
def test_coding_create_round_trip(cls: type, prefix: str) -> None:
    """Each coding subclass produces a CREATE_<PREFIX> effect carrying its fields."""
    effect = cls(display="Yes", code="Y", system="http://example.com").create()
    assert EffectType.Name(effect.type) == f"CREATE_{prefix}"
    data = json.loads(effect.payload)["data"]
    assert data["display"] == "Yes"
    assert data["code"] == "Y"
    assert data["system"] == "http://example.com"


@pytest.mark.parametrize("cls,prefix", CODING_CLASSES)
def test_coding_update_round_trip(cls: type, prefix: str) -> None:
    """Each coding subclass produces an UPDATE_<PREFIX> effect when given an id."""
    effect = cls(id="c-1", active=False).update()
    assert EffectType.Name(effect.type) == f"UPDATE_{prefix}"


@pytest.mark.parametrize("cls,prefix", CODING_CLASSES)
def test_coding_delete_round_trip(cls: type, prefix: str) -> None:
    """Each coding subclass produces a DELETE_<PREFIX> effect carrying only the id."""
    effect = cls(id="c-1").delete()
    assert EffectType.Name(effect.type) == f"DELETE_{prefix}"
    assert json.loads(effect.payload) == {"data": {"id": "c-1"}}


@pytest.mark.parametrize("cls,_prefix", CODING_CLASSES)
def test_coding_create_requires_display_code_system(cls: type, _prefix: str) -> None:
    """create() raises when display/code/system are missing."""
    with pytest.raises(ValidationError):
        cls().create()


@pytest.mark.parametrize("cls,_prefix", CODING_CLASSES)
def test_coding_update_requires_id(cls: type, _prefix: str) -> None:
    """update() raises without an id."""
    with pytest.raises(ValidationError):
        cls(active=True).update()


@pytest.mark.parametrize("cls,_prefix", CODING_CLASSES)
def test_coding_delete_requires_id(cls: type, _prefix: str) -> None:
    """delete() raises without an id."""
    with pytest.raises(ValidationError):
        cls().delete()


# ---------- Role / StaffRole ----------


def test_role_update_and_delete_round_trip() -> None:
    """Role update / delete produce the expected effect types."""
    upd = Role(id="r-1", name="Updated").update()
    assert EffectType.Name(upd.type) == "UPDATE_ROLE"
    deletion = Role(id="r-1").delete()
    assert EffectType.Name(deletion.type) == "DELETE_ROLE"
    assert json.loads(deletion.payload) == {"data": {"id": "r-1"}}


def test_role_create_requires_name_internal_code_domain() -> None:
    """Role.create() raises when name / internal_code / domain are missing."""
    with pytest.raises(ValidationError):
        Role().create()


def test_role_update_requires_id() -> None:
    """Role.update() raises without an id."""
    with pytest.raises(ValidationError):
        Role(name="x").update()


def test_role_delete_requires_id() -> None:
    """Role.delete() raises without an id."""
    with pytest.raises(ValidationError):
        Role().delete()


def test_staff_role_assign_requires_staff_id() -> None:
    """StaffRole.assign() raises without staff_id."""
    with pytest.raises(ValidationError):
        StaffRole(role_code="MD").assign()


def test_staff_role_assign_requires_role_ref() -> None:
    """StaffRole.assign() raises without role_code or role_id."""
    with pytest.raises(ValidationError):
        StaffRole(staff_id="s-1").assign()


def test_staff_role_remove_requires_staff_id() -> None:
    """StaffRole.remove() raises without staff_id."""
    with pytest.raises(ValidationError):
        StaffRole(role_code="MD").remove()


# ---------- PermissionGroup / RolePermissionGroup ----------


def test_permission_group_update_and_delete_round_trip() -> None:
    """PermissionGroup update / delete produce the expected effect types."""
    upd = PermissionGroup(id="pg-1", description="x").update()
    assert EffectType.Name(upd.type) == "UPDATE_PERMISSION_GROUP"
    deletion = PermissionGroup(id="pg-1").delete()
    assert EffectType.Name(deletion.type) == "DELETE_PERMISSION_GROUP"
    assert json.loads(deletion.payload) == {"data": {"id": "pg-1"}}


def test_permission_group_create_requires_name_and_internal_code() -> None:
    """PermissionGroup.create() raises when name or internal_code are missing."""
    with pytest.raises(ValidationError):
        PermissionGroup().create()


def test_permission_group_update_requires_id() -> None:
    """PermissionGroup.update() raises without an id."""
    with pytest.raises(ValidationError):
        PermissionGroup(name="x").update()


def test_permission_group_delete_requires_id() -> None:
    """PermissionGroup.delete() raises without an id."""
    with pytest.raises(ValidationError):
        PermissionGroup().delete()


def test_role_permission_group_assign_requires_role_id() -> None:
    """RolePermissionGroup.assign() raises without role_id."""
    with pytest.raises(ValidationError):
        RolePermissionGroup(permission_group_id="pg-1").assign()


def test_role_permission_group_assign_requires_permission_group_id() -> None:
    """RolePermissionGroup.assign() raises without permission_group_id."""
    with pytest.raises(ValidationError):
        RolePermissionGroup(role_id="r-1").assign()


def test_role_permission_group_remove_requires_both_ids() -> None:
    """RolePermissionGroup.remove() raises when both ids are missing."""
    with pytest.raises(ValidationError):
        RolePermissionGroup().remove()


# ---------- Team / TeamMember / CareTeamRole ----------


def test_team_update_and_delete_round_trip() -> None:
    """Team update / delete produce the expected effect types."""
    upd = Team(id="t-1", phone="6175551212").update()
    assert EffectType.Name(upd.type) == "UPDATE_TEAM"
    deletion = Team(id="t-1").delete()
    assert EffectType.Name(deletion.type) == "DELETE_TEAM"


def test_team_create_requires_name() -> None:
    """Team.create() raises without a name."""
    with pytest.raises(ValidationError):
        Team().create()


def test_team_update_requires_id() -> None:
    """Team.update() raises without an id."""
    with pytest.raises(ValidationError):
        Team(name="x").update()


def test_team_delete_requires_id() -> None:
    """Team.delete() raises without an id."""
    with pytest.raises(ValidationError):
        Team().delete()


def test_team_member_assign_requires_team_id() -> None:
    """TeamMember.assign() raises without team_id."""
    with pytest.raises(ValidationError):
        TeamMember(staff_id="s-1").assign()


def test_team_member_assign_requires_staff_id() -> None:
    """TeamMember.assign() raises without staff_id."""
    with pytest.raises(ValidationError):
        TeamMember(team_id="t-1").assign()


def test_team_member_remove_requires_both_ids() -> None:
    """TeamMember.remove() raises when both ids are missing."""
    with pytest.raises(ValidationError):
        TeamMember().remove()


def test_care_team_role_update_and_delete_round_trip() -> None:
    """CareTeamRole update / delete produce the expected effect types."""
    upd = CareTeamRole(id="ctr-1", display="Updated", active=False).update()
    assert EffectType.Name(upd.type) == "UPDATE_CARE_TEAM_ROLE"
    deletion = CareTeamRole(id="ctr-1").delete()
    assert EffectType.Name(deletion.type) == "DELETE_CARE_TEAM_ROLE"


def test_care_team_role_create_requires_display_and_system() -> None:
    """CareTeamRole.create() raises without display / system."""
    with pytest.raises(ValidationError):
        CareTeamRole().create()


def test_care_team_role_update_requires_id() -> None:
    """CareTeamRole.update() raises without an id."""
    with pytest.raises(ValidationError):
        CareTeamRole(display="x").update()


def test_care_team_role_delete_requires_id() -> None:
    """CareTeamRole.delete() raises without an id."""
    with pytest.raises(ValidationError):
        CareTeamRole().delete()


# ---------- Insurer ----------


def test_insurer_update_and_delete_round_trip() -> None:
    """Insurer update / delete produce the expected effect types."""
    upd = Insurer(id="i-1", phone="6175551212").update()
    assert EffectType.Name(upd.type) == "UPDATE_INSURER"
    deletion = Insurer(id="i-1").delete()
    assert EffectType.Name(deletion.type) == "DELETE_INSURER"
    assert json.loads(deletion.payload) == {"data": {"id": "i-1"}}


def test_insurer_create_requires_name_and_transactor_type() -> None:
    """Insurer.create() raises without name / transactor_type."""
    with pytest.raises(ValidationError):
        Insurer().create()


def test_insurer_update_requires_id() -> None:
    """Insurer.update() raises without an id."""
    with pytest.raises(ValidationError):
        Insurer(name="x").update()


def test_insurer_delete_requires_id() -> None:
    """Insurer.delete() raises without an id."""
    with pytest.raises(ValidationError):
        Insurer().delete()


# ---------- Vaccine / VaccineLot ----------


def test_vaccine_update_and_delete_round_trip() -> None:
    """Vaccine update / delete produce the expected effect types."""
    upd = Vaccine(id="v-1", active=False).update()
    assert EffectType.Name(upd.type) == "UPDATE_VACCINE"
    deletion = Vaccine(id="v-1").delete()
    assert EffectType.Name(deletion.type) == "DELETE_VACCINE"


def test_vaccine_create_requires_name_and_cvx_code() -> None:
    """Vaccine.create() raises without name / cvx_code."""
    with pytest.raises(ValidationError):
        Vaccine().create()


def test_vaccine_update_requires_id() -> None:
    """Vaccine.update() raises without an id."""
    with pytest.raises(ValidationError):
        Vaccine(active=True).update()


def test_vaccine_delete_requires_id() -> None:
    """Vaccine.delete() raises without an id."""
    with pytest.raises(ValidationError):
        Vaccine().delete()


def test_vaccine_lot_update_and_delete_round_trip() -> None:
    """VaccineLot update / delete produce the expected effect types."""
    upd = VaccineLot(id="vl-1", quantity_on_hand=5).update()
    assert EffectType.Name(upd.type) == "UPDATE_VACCINE_LOT"
    deletion = VaccineLot(id="vl-1").delete()
    assert EffectType.Name(deletion.type) == "DELETE_VACCINE_LOT"


def test_vaccine_lot_create_requires_required_fields() -> None:
    """VaccineLot.create() raises without vaccine_id / lot_number / expiration_date."""
    with pytest.raises(ValidationError):
        VaccineLot().create()


def test_vaccine_lot_update_requires_id() -> None:
    """VaccineLot.update() raises without an id."""
    with pytest.raises(ValidationError):
        VaccineLot(quantity_on_hand=5).update()


def test_vaccine_lot_delete_requires_id() -> None:
    """VaccineLot.delete() raises without an id."""
    with pytest.raises(ValidationError):
        VaccineLot().delete()


# ---------- Billing catalog (shared _base.py + subclasses) ----------


def test_fee_schedule_update_and_delete_round_trip() -> None:
    """FeeSchedule update / delete produce the expected effect types."""
    upd = FeeSchedule(id="fs-1", price="120.00").update()
    assert EffectType.Name(upd.type) == "UPDATE_FEE_SCHEDULE"
    deletion = FeeSchedule(id="fs-1").delete()
    assert EffectType.Name(deletion.type) == "DELETE_FEE_SCHEDULE"


def test_fee_schedule_create_requires_required_fields() -> None:
    """FeeSchedule.create() raises without code / price."""
    with pytest.raises(ValidationError):
        FeeSchedule().create()


def test_fee_schedule_update_requires_id() -> None:
    """FeeSchedule.update() raises without an id."""
    with pytest.raises(ValidationError):
        FeeSchedule(price="100").update()


def test_fee_schedule_delete_requires_id() -> None:
    """FeeSchedule.delete() raises without an id."""
    with pytest.raises(ValidationError):
        FeeSchedule().delete()


def test_posting_rule_update_and_delete_round_trip() -> None:
    """PostingRule update / delete produce the expected effect types."""
    upd = PostingRule(id="pr-1", action="HOLD").update()
    assert EffectType.Name(upd.type) == "UPDATE_POSTING_RULE"
    deletion = PostingRule(id="pr-1").delete()
    assert EffectType.Name(deletion.type) == "DELETE_POSTING_RULE"


def test_posting_rule_create_requires_required_fields() -> None:
    """PostingRule.create() raises without name / action."""
    with pytest.raises(ValidationError):
        PostingRule().create()


def test_posting_rule_update_requires_id() -> None:
    """PostingRule.update() raises without an id."""
    with pytest.raises(ValidationError):
        PostingRule(action="POST").update()


def test_payor_charge_update_and_delete_round_trip() -> None:
    """PayorCharge update / delete produce the expected effect types."""
    upd = PayorCharge(id="pc-1", price="90.00").update()
    assert EffectType.Name(upd.type) == "UPDATE_PAYOR_CHARGE"
    deletion = PayorCharge(id="pc-1").delete()
    assert EffectType.Name(deletion.type) == "DELETE_PAYOR_CHARGE"


def test_payor_charge_create_requires_required_fields() -> None:
    """PayorCharge.create() raises without insurer_id / code / price."""
    with pytest.raises(ValidationError):
        PayorCharge().create()


def test_discount_update_and_delete_round_trip() -> None:
    """Discount update / delete produce the expected effect types."""
    upd = Discount(id="d-1", name="New").update()
    assert EffectType.Name(upd.type) == "UPDATE_DISCOUNT"
    deletion = Discount(id="d-1").delete()
    assert EffectType.Name(deletion.type) == "DELETE_DISCOUNT"


def test_discount_create_requires_name() -> None:
    """Discount.create() raises without a name."""
    with pytest.raises(ValidationError):
        Discount().create()


def test_discount_delete_requires_id() -> None:
    """Discount.delete() raises without an id."""
    with pytest.raises(ValidationError):
        Discount().delete()


# ---------- NoteType ----------


def test_note_type_update_and_delete_round_trip() -> None:
    """NoteType update / delete produce the expected effect types."""
    upd = NoteType(id="nt-1", is_active=False).update()
    assert EffectType.Name(upd.type) == "UPDATE_NOTE_TYPE"
    deletion = NoteType(id="nt-1").delete()
    assert EffectType.Name(deletion.type) == "DELETE_NOTE_TYPE"


def test_note_type_update_requires_id() -> None:
    """NoteType.update() raises without an id."""
    with pytest.raises(ValidationError):
        NoteType(name="x").update()


def test_note_type_delete_requires_id() -> None:
    """NoteType.delete() raises without an id."""
    with pytest.raises(ValidationError):
        NoteType().delete()


# ---------- StaffLicense ----------


def test_staff_license_update_and_delete_round_trip() -> None:
    """StaffLicense update / delete produce the expected effect types."""
    upd = StaffLicense(id="sl-1", primary=True).update()
    assert EffectType.Name(upd.type) == "UPDATE_STAFF_LICENSE"
    deletion = StaffLicense(id="sl-1").delete()
    assert EffectType.Name(deletion.type) == "DELETE_STAFF_LICENSE"


def test_staff_license_create_requires_required_fields() -> None:
    """StaffLicense.create() raises without staff_id / license_type / identifier."""
    with pytest.raises(ValidationError):
        StaffLicense().create()


def test_staff_license_update_requires_id() -> None:
    """StaffLicense.update() raises without an id."""
    with pytest.raises(ValidationError):
        StaffLicense(primary=True).update()


def test_staff_license_delete_requires_id() -> None:
    """StaffLicense.delete() raises without an id."""
    with pytest.raises(ValidationError):
        StaffLicense().delete()


# ---------- Address ----------


def test_address_update_and_delete_round_trip() -> None:
    """Address update / delete produce the expected effect types."""
    upd = Address(id="a-1", line2="Apt 2").update()
    assert EffectType.Name(upd.type) == "UPDATE_ADDRESS"
    deletion = Address(id="a-1").delete()
    assert EffectType.Name(deletion.type) == "DELETE_ADDRESS"


def test_address_create_requires_required_fields() -> None:
    """Address.create() raises when parent_type / parent_id / line1 / city / state / postal_code are missing."""
    with pytest.raises(ValidationError):
        Address().create()


def test_address_update_requires_id() -> None:
    """Address.update() raises without an id."""
    with pytest.raises(ValidationError):
        Address(line1="x").update()


def test_address_delete_requires_id() -> None:
    """Address.delete() raises without an id."""
    with pytest.raises(ValidationError):
        Address().delete()


# ---------- Staff (DB-backed validator) ----------


@pytest.fixture
def staff_model_exists() -> Generator[None, None, None]:
    """Patch StaffModel.objects so .filter(id=...).exists() returns True."""
    p = patch("canvas_sdk.effects.staff.staff.StaffModel.objects")
    m = p.start()
    m.filter.return_value.exists.return_value = True
    yield
    p.stop()


@pytest.fixture
def staff_model_missing() -> Generator[None, None, None]:
    """Patch StaffModel.objects so .filter(id=...).exists() returns False."""
    p = patch("canvas_sdk.effects.staff.staff.StaffModel.objects")
    m = p.start()
    m.filter.return_value.exists.return_value = False
    yield
    p.stop()


def test_staff_update_and_delete_round_trip(staff_model_exists: None) -> None:
    """Staff update / delete produce the expected effect types."""
    upd = Staff(id="s-1", phone="6175551212").update()
    assert EffectType.Name(upd.type) == "UPDATE_STAFF"
    deletion = Staff(id="s-1").delete()
    assert EffectType.Name(deletion.type) == "DELETE_STAFF"


def test_staff_create_rejects_id() -> None:
    """Staff.create() raises when an id is provided."""
    with pytest.raises(ValidationError):
        Staff(
            id="s-1",
            first_name="Ada",
            last_name="L",
            email="a@l.com",
            primary_practice_location_id="loc-1",
        ).create()


def test_staff_update_requires_id() -> None:
    """Staff.update() raises without an id (db check is skipped on the missing-id branch)."""
    with pytest.raises(ValidationError):
        Staff(phone="555").update()


def test_staff_delete_requires_id() -> None:
    """Staff.delete() raises without an id."""
    with pytest.raises(ValidationError):
        Staff().delete()


def test_staff_activate_requires_id() -> None:
    """Staff.activate() raises without an id."""
    with pytest.raises(ValidationError):
        Staff().activate()


def test_staff_deactivate_requires_id() -> None:
    """Staff.deactivate() raises without an id."""
    with pytest.raises(ValidationError):
        Staff().deactivate()


def test_staff_update_rejects_nonexistent_id(staff_model_missing: None) -> None:
    """Staff.update() raises when the referenced id does not exist."""
    with pytest.raises(ValidationError):
        Staff(id="missing").update()


def test_staff_delete_rejects_nonexistent_id(staff_model_missing: None) -> None:
    """Staff.delete() raises when the referenced id does not exist."""
    with pytest.raises(ValidationError):
        Staff(id="missing").delete()


def test_staff_activate_rejects_nonexistent_id(staff_model_missing: None) -> None:
    """Staff.activate() raises when the referenced id does not exist."""
    with pytest.raises(ValidationError):
        Staff(id="missing").activate()


# ---------- PracticeLocationSetting upsert happy path ----------


def test_practice_location_setting_upsert_round_trip() -> None:
    """PracticeLocationSetting.upsert() produces the expected effect type."""
    effect = PracticeLocationSetting(
        practice_location_id="loc-1",
        name="printed_prescription_format",
        value={"format": "letter"},
    ).upsert()
    assert EffectType.Name(effect.type) == "UPSERT_PRACTICE_LOCATION_SETTING"


# ---------- FormField extended emission ----------


def test_form_field_emits_help_text_when_set() -> None:
    """FormField.to_dict() emits `help_text` when it is set."""
    out = FormField(key="x", label="X", help_text="hi").to_dict()
    assert out["help_text"] == "hi"


def test_form_field_emits_group_when_set() -> None:
    """FormField.to_dict() emits `group` when it is set."""
    out = FormField(key="x", label="X", group="Identity").to_dict()
    assert out["group"] == "Identity"


def test_form_field_emits_placeholder_when_set() -> None:
    """FormField.to_dict() emits `placeholder` when it is set."""
    out = FormField(key="x", label="X", placeholder="enter text").to_dict()
    assert out["placeholder"] == "enter text"


def test_form_field_emits_min_value_when_set() -> None:
    """FormField.to_dict() emits `min_value` when it is set (including 0)."""
    out = FormField(key="x", label="X", type=InputType.NUMBER, min_value=0).to_dict()
    assert out["min_value"] == 0


def test_form_field_emits_max_value_when_set() -> None:
    """FormField.to_dict() emits `max_value` when it is set."""
    out = FormField(key="x", label="X", type=InputType.NUMBER, max_value=100).to_dict()
    assert out["max_value"] == 100


def test_form_field_omits_widget_config_when_empty() -> None:
    """FormField.to_dict() does not emit `widget_config` when it is an empty dict."""
    out = FormField(key="x", label="X").to_dict()
    assert "widget_config" not in out
    assert "help_text" not in out
    assert "group" not in out
    assert "placeholder" not in out
    assert "min_value" not in out
    assert "max_value" not in out
