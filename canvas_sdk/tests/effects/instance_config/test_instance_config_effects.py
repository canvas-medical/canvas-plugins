"""Round-trip tests for the Instance Configuration effect classes.

Each domain has a CRUD trio backed by the same TrackableFieldsModel pattern
(plus a few specials: Organization is update-only, *Setting are upsert,
StaffRole / TeamMember / RolePermissionGroup are assign/remove, ConstanceValue
is set, AuditLog is write, FileUpload is upload, SetupCompletion is upsert).

These tests intentionally avoid hitting the database — they only verify the
shape of the resulting protobuf Effect and the validation rules.
"""

import json
from collections.abc import Generator
from datetime import date
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from pydantic_core import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.address import Address, AddressUse
from canvas_sdk.effects.audit_log import AuditAction, AuditLog
from canvas_sdk.effects.billing_catalog import Discount, FeeSchedule, PayorCharge, PostingRule
from canvas_sdk.effects.codings import (
    PatientConsentCoding,
    PatientConsentRejectionCoding,
    ReasonForVisitSettingCoding,
)
from canvas_sdk.effects.constance import ConstanceValue
from canvas_sdk.effects.file_upload import FileUpload
from canvas_sdk.effects.insurer import Insurer
from canvas_sdk.effects.note_type import NoteType, NoteTypeCategory
from canvas_sdk.effects.organization import (
    Organization,
    OrganizationBranding,
    OrganizationSetting,
)
from canvas_sdk.effects.practice_location import PracticeLocation, PracticeLocationSetting
from canvas_sdk.effects.role import (
    PermissionGroup,
    Role,
    RoleDomain,
    RolePermissionGroup,
    StaffRole,
)
from canvas_sdk.effects.setup_completion import SetupCompletion, SetupCompletionStatus
from canvas_sdk.effects.staff import Staff, StaffExternalIdentifier, StaffLicense
from canvas_sdk.effects.staff.staff_license import LicenseType
from canvas_sdk.effects.team import CareTeamRole, Team, TeamMember
from canvas_sdk.effects.vaccine_catalog import Vaccine, VaccineLot

# Each row: (factory callable, expected EffectType name, expected payload keys to spot-check)
CREATE_CASES = [
    (
        lambda: PracticeLocation(
            full_name="Main", short_name="M", place_of_service_code="11"
        ).create(),
        "CREATE_PRACTICE_LOCATION",
        {"full_name", "short_name", "place_of_service_code"},
    ),
    (
        lambda: Staff(
            first_name="Ada",
            last_name="L",
            email="a@l.com",
            primary_practice_location_id="loc-1",
        ).create(),
        "CREATE_STAFF",
        {"first_name", "last_name", "email", "primary_practice_location_id"},
    ),
    (
        lambda: Role(name="Physician", internal_code="MD", domain=RoleDomain.CLINICAL).create(),
        "CREATE_ROLE",
        {"name", "internal_code", "domain"},
    ),
    (
        lambda: PermissionGroup(name="Edit Notes", internal_code="EDIT_NOTES").create(),
        "CREATE_PERMISSION_GROUP",
        {"name", "internal_code"},
    ),
    (lambda: Team(name="Care").create(), "CREATE_TEAM", {"name"}),
    (
        lambda: CareTeamRole(display="PCP", system="http://snomed.info/sct").create(),
        "CREATE_CARE_TEAM_ROLE",
        {"display", "system"},
    ),
    (
        lambda: NoteType(
            name="visit", display="Visit", category=NoteTypeCategory.ENCOUNTER
        ).create(),
        "CREATE_NOTE_TYPE",
        {"name", "display", "category"},
    ),
    (
        lambda: FeeSchedule(code="99213", price="100.00").create(),
        "CREATE_FEE_SCHEDULE",
        {"code", "price"},
    ),
    (
        lambda: PostingRule(name="Auto", action="POST").create(),
        "CREATE_POSTING_RULE",
        {"name", "action"},
    ),
    (
        lambda: PayorCharge(insurer_id="aaa", code="99213", price="80.00").create(),
        "CREATE_PAYOR_CHARGE",
        {"insurer_id", "code", "price"},
    ),
    (lambda: Discount(name="Sliding").create(), "CREATE_DISCOUNT", {"name"}),
    (
        lambda: Insurer(name="Aetna", transactor_type="payer").create(),
        "CREATE_INSURER",
        {"name", "transactor_type"},
    ),
    (
        lambda: Vaccine(name="COVID", cvx_code="208").create(),
        "CREATE_VACCINE",
        {"name", "cvx_code"},
    ),
    (
        lambda: VaccineLot(
            vaccine_id="vax-1",
            lot_number="L1",
            expiration_date=date(2030, 1, 1),
        ).create(),
        "CREATE_VACCINE_LOT",
        {"vaccine_id", "lot_number", "expiration_date"},
    ),
    (
        lambda: StaffLicense(
            staff_id="staff-1",
            license_type=LicenseType.DEA,
            license_or_certification_identifier="AB1234567",
        ).create(),
        "CREATE_STAFF_LICENSE",
        {"staff_id", "license_type", "license_or_certification_identifier"},
    ),
    (
        lambda: Address(
            parent_type="practice_location",
            parent_id="loc-1",
            use=AddressUse.WORK,
            line1="1",
            city="B",
            state="MA",
            postal_code="02101",
        ).create(),
        "CREATE_ADDRESS",
        {"parent_type", "parent_id", "use", "line1", "city", "state", "postal_code"},
    ),
]


@pytest.mark.parametrize("factory,expected_type,expected_keys", CREATE_CASES)
def test_create_effects_produce_correct_type_and_payload(
    factory: Any, expected_type: str, expected_keys: set[str]
) -> None:
    """Create effects produce correct type and payload."""
    effect = factory()
    assert EffectType.Name(effect.type) == expected_type
    data = json.loads(effect.payload)["data"]
    assert expected_keys.issubset(data.keys())


@pytest.fixture
def mock_existence_checks() -> Generator[None, None, None]:
    """Make `Model.objects.filter(id=...).exists()` return True for the
    SDK data models the instance-config effects reference in their
    validators. We're not testing DB behavior here, only effect payloads.
    """
    paths = [
        "canvas_sdk.effects.practice_location.practice_location.PracticeLocationModel.objects",
        "canvas_sdk.effects.staff.staff.StaffModel.objects",
    ]
    patches = [patch(p) for p in paths]
    mocks: list[MagicMock] = [p.start() for p in patches]
    for m in mocks:
        m.filter.return_value.exists.return_value = True
    yield
    for p in patches:
        p.stop()


def test_update_effects_use_update_prefix(mock_existence_checks: None) -> None:
    """Update effects use update prefix."""
    effect = PracticeLocation(id="loc-1", active=False).update()
    assert EffectType.Name(effect.type) == "UPDATE_PRACTICE_LOCATION"


def test_delete_effects_carry_only_id(mock_existence_checks: None) -> None:
    """Delete effects carry only id."""
    effect = PracticeLocation(id="loc-1").delete()
    assert EffectType.Name(effect.type) == "DELETE_PRACTICE_LOCATION"
    assert json.loads(effect.payload) == {"data": {"id": "loc-1"}}


def test_staff_activate_and_deactivate(mock_existence_checks: None) -> None:
    """Staff activate and deactivate."""
    activate = Staff(id="s-1").activate()
    assert EffectType.Name(activate.type) == "ACTIVATE_STAFF"
    deactivate = Staff(id="s-1").deactivate()
    assert EffectType.Name(deactivate.type) == "DEACTIVATE_STAFF"


def test_staff_role_assign_and_remove() -> None:
    """Staff role assign and remove."""
    assign = StaffRole(staff_id="s-1", role_code="MD").assign()
    remove = StaffRole(staff_id="s-1", role_code="MD").remove()
    assert EffectType.Name(assign.type) == "ASSIGN_STAFF_ROLE"
    assert EffectType.Name(remove.type) == "REMOVE_STAFF_ROLE"


def test_role_permission_group_assign_and_remove() -> None:
    """Role permission group assign and remove."""
    assign = RolePermissionGroup(role_id="r-1", permission_group_id="pg-1").assign()
    remove = RolePermissionGroup(role_id="r-1", permission_group_id="pg-1").remove()
    assert EffectType.Name(assign.type) == "ASSIGN_ROLE_PERMISSION_GROUP"
    assert EffectType.Name(remove.type) == "REMOVE_ROLE_PERMISSION_GROUP"


def test_team_member_assign_and_remove() -> None:
    """Team member assign and remove."""
    assign = TeamMember(team_id="t-1", staff_id="s-1").assign()
    remove = TeamMember(team_id="t-1", staff_id="s-1").remove()
    assert EffectType.Name(assign.type) == "ASSIGN_TEAM_MEMBER"
    assert EffectType.Name(remove.type) == "REMOVE_TEAM_MEMBER"


def test_organization_is_update_only() -> None:
    """Organization is update only."""
    effect = Organization(short_name="Co").update()
    assert EffectType.Name(effect.type) == "UPDATE_ORGANIZATION"
    assert not hasattr(Organization, "create")
    assert not hasattr(Organization, "delete")


def test_organization_branding_update() -> None:
    """Organization branding update."""
    effect = OrganizationBranding(header_color="#01A4FF").update()
    assert EffectType.Name(effect.type) == "UPDATE_ORGANIZATION_BRANDING"
    data = json.loads(effect.payload)["data"]
    assert data["header_color"] == "#01A4FF"


def test_organization_setting_upsert() -> None:
    """Organization setting upsert."""
    effect = OrganizationSetting(name="brand_color", value="#01A4FF").upsert()
    assert EffectType.Name(effect.type) == "UPSERT_ORGANIZATION_SETTING"


def test_organization_setting_requires_name() -> None:
    """Organization setting requires name."""
    with pytest.raises(ValidationError):
        OrganizationSetting(value="x").upsert()


def test_practice_location_setting_upsert_requires_id_and_name() -> None:
    """Practice location setting upsert requires id and name."""
    with pytest.raises(ValidationError):
        PracticeLocationSetting(value="x").upsert()


def test_constance_value_set_requires_key_and_value() -> None:
    """Constance value set requires key and value."""
    effect = ConstanceValue(key="FEATURE_FLAG_X", value=True).set()
    assert EffectType.Name(effect.type) == "SET_CONSTANCE_VALUE"
    with pytest.raises(ValidationError):
        ConstanceValue().set()


def test_audit_log_write_round_trip() -> None:
    """Audit log write round trip."""
    effect = AuditLog(
        section="roles",
        action=AuditAction.CREATE,
        record_id="r-1",
        changes={"name": ["", "Physician"]},
    ).write()
    assert EffectType.Name(effect.type) == "WRITE_AUDIT_LOG"
    data = json.loads(effect.payload)["data"]
    assert data["section"] == "roles"
    assert data["action"] == "create"


def test_audit_log_requires_section_and_action() -> None:
    """Audit log requires section and action."""
    with pytest.raises(ValidationError):
        AuditLog().write()


def test_file_upload_round_trip() -> None:
    """File upload round trip."""
    effect = FileUpload(
        filename="logo.png",
        content_type="image/png",
        content_base64="Zm9v",
        folder="branding",
    ).upload()
    assert EffectType.Name(effect.type) == "UPLOAD_FILE"


def test_setup_completion_upsert_round_trip() -> None:
    """Setup completion upsert round trip."""
    effect = SetupCompletion(
        section_id="organization",
        status=SetupCompletionStatus.COMPLETED,
    ).upsert()
    assert EffectType.Name(effect.type) == "UPSERT_SETUP_COMPLETION"


def test_staff_create_validates_required_fields() -> None:
    """Staff create validates required fields."""
    with pytest.raises(ValidationError):
        Staff().create()


def test_address_create_rejects_id() -> None:
    """Address create rejects id."""
    with pytest.raises(ValidationError):
        Address(
            id="addr-1",
            parent_type="practice_location",
            parent_id="loc-1",
            use=AddressUse.WORK,
            line1="1",
            city="B",
            state="MA",
            postal_code="02101",
        ).create()


def test_note_type_create_requires_category() -> None:
    """Note type create requires category."""
    with pytest.raises(ValidationError):
        NoteType(name="x", display="X").create()


def test_setup_completion_status_enum_serializes_to_value() -> None:
    """Setup completion status enum serializes to value."""
    effect = SetupCompletion(section_id="org", status=SetupCompletionStatus.SKIPPED).upsert()
    data = json.loads(effect.payload)["data"]
    assert data["status"] == "skipped"


# ---------------------------------------------------------------------------
# update() / delete() round-trips for entities whose validator does not hit
# the DB (i.e. every CRUD effect except PracticeLocation / Staff /
# StaffExternalIdentifier).
# ---------------------------------------------------------------------------

UPDATE_CASES = [
    (lambda: Role(id="r-1", name="Updated").update(), "UPDATE_ROLE"),
    (lambda: PermissionGroup(id="pg-1", description="x").update(), "UPDATE_PERMISSION_GROUP"),
    (lambda: Team(id="t-1", name="Updated").update(), "UPDATE_TEAM"),
    (lambda: NoteType(id="n-1", display="Updated").update(), "UPDATE_NOTE_TYPE"),
    (lambda: Insurer(id="i-1", name="Aetna").update(), "UPDATE_INSURER"),
    (lambda: Vaccine(id="v-1", name="COVID").update(), "UPDATE_VACCINE"),
    (lambda: VaccineLot(id="vl-1", lot_number="L2").update(), "UPDATE_VACCINE_LOT"),
    (lambda: Discount(id="d-1", name="Updated").update(), "UPDATE_DISCOUNT"),
    (lambda: FeeSchedule(id="fs-1", price="200.00").update(), "UPDATE_FEE_SCHEDULE"),
    (lambda: PostingRule(id="pr-1", action="HOLD").update(), "UPDATE_POSTING_RULE"),
    (lambda: PayorCharge(id="pc-1", price="90.00").update(), "UPDATE_PAYOR_CHARGE"),
    (lambda: CareTeamRole(id="ct-1", display="PCP-2").update(), "UPDATE_CARE_TEAM_ROLE"),
    (
        lambda: StaffLicense(id="sl-1", license_or_certification_identifier="X").update(),
        "UPDATE_STAFF_LICENSE",
    ),
    (lambda: Address(id="a-1", line1="2").update(), "UPDATE_ADDRESS"),
]


@pytest.mark.parametrize("factory,expected_type", UPDATE_CASES)
def test_update_effects_round_trip(factory: Any, expected_type: str) -> None:
    """Update effects round trip for all non-DB-checking entities."""
    effect = factory()
    assert EffectType.Name(effect.type) == expected_type
    data = json.loads(effect.payload)["data"]
    assert data["id"] is not None


DELETE_CASES = [
    (lambda: Role(id="r-1").delete(), "DELETE_ROLE"),
    (lambda: PermissionGroup(id="pg-1").delete(), "DELETE_PERMISSION_GROUP"),
    (lambda: Team(id="t-1").delete(), "DELETE_TEAM"),
    (lambda: NoteType(id="n-1").delete(), "DELETE_NOTE_TYPE"),
    (lambda: Insurer(id="i-1").delete(), "DELETE_INSURER"),
    (lambda: Vaccine(id="v-1").delete(), "DELETE_VACCINE"),
    (lambda: VaccineLot(id="vl-1").delete(), "DELETE_VACCINE_LOT"),
    (lambda: Discount(id="d-1").delete(), "DELETE_DISCOUNT"),
    (lambda: FeeSchedule(id="fs-1").delete(), "DELETE_FEE_SCHEDULE"),
    (lambda: PostingRule(id="pr-1").delete(), "DELETE_POSTING_RULE"),
    (lambda: PayorCharge(id="pc-1").delete(), "DELETE_PAYOR_CHARGE"),
    (lambda: CareTeamRole(id="ct-1").delete(), "DELETE_CARE_TEAM_ROLE"),
    (lambda: StaffLicense(id="sl-1").delete(), "DELETE_STAFF_LICENSE"),
    (lambda: Address(id="a-1").delete(), "DELETE_ADDRESS"),
]


@pytest.mark.parametrize("factory,expected_type", DELETE_CASES)
def test_delete_effects_round_trip(factory: Any, expected_type: str) -> None:
    """Delete effects carry only the id for every CRUD entity."""
    effect = factory()
    assert EffectType.Name(effect.type) == expected_type
    assert json.loads(effect.payload) == {"data": {"id": effect_id_from(effect)}}


def effect_id_from(effect: Any) -> str:
    """Extract the id from a delete-effect payload (helper)."""
    return json.loads(effect.payload)["data"]["id"]


# Missing-id validation for the same set of entities.

MISSING_ID_FACTORIES = [
    lambda: Role(name="X").update(),
    lambda: Role().delete(),
    lambda: PermissionGroup().update(),
    lambda: PermissionGroup().delete(),
    lambda: Team().update(),
    lambda: Team().delete(),
    lambda: NoteType().update(),
    lambda: NoteType().delete(),
    lambda: Insurer().update(),
    lambda: Insurer().delete(),
    lambda: Vaccine().update(),
    lambda: Vaccine().delete(),
    lambda: VaccineLot().update(),
    lambda: VaccineLot().delete(),
    lambda: Discount().update(),
    lambda: Discount().delete(),
    lambda: FeeSchedule().update(),
    lambda: FeeSchedule().delete(),
    lambda: PostingRule().update(),
    lambda: PostingRule().delete(),
    lambda: PayorCharge().update(),
    lambda: PayorCharge().delete(),
    lambda: CareTeamRole().update(),
    lambda: CareTeamRole().delete(),
    lambda: StaffLicense().update(),
    lambda: StaffLicense().delete(),
    lambda: Address().update(),
    lambda: Address().delete(),
]


@pytest.mark.parametrize("factory", MISSING_ID_FACTORIES)
def test_update_or_delete_without_id_raises(factory: Any) -> None:
    """update() / delete() without an id raises ValidationError."""
    with pytest.raises(ValidationError):
        factory()


# Missing-required-fields validation for create() across the catalog.

MISSING_CREATE_FACTORIES = [
    lambda: Role().create(),
    lambda: PermissionGroup().create(),
    lambda: Team().create(),
    lambda: Insurer().create(),
    lambda: Vaccine().create(),
    lambda: VaccineLot().create(),
    lambda: FeeSchedule().create(),
    lambda: PostingRule().create(),
    lambda: PayorCharge().create(),
    lambda: CareTeamRole().create(),
    lambda: StaffLicense().create(),
    lambda: Address().create(),
]


@pytest.mark.parametrize("factory", MISSING_CREATE_FACTORIES)
def test_create_without_required_fields_raises(factory: Any) -> None:
    """create() without required fields raises ValidationError."""
    with pytest.raises(ValidationError):
        factory()


# ---------------------------------------------------------------------------
# Staff update / delete need the existing DB-mocking fixture.
# ---------------------------------------------------------------------------


def test_staff_update_round_trip(mock_existence_checks: None) -> None:
    """Staff update round trip."""
    effect = Staff(id="s-1", email="updated@example.com").update()
    assert EffectType.Name(effect.type) == "UPDATE_STAFF"
    data = json.loads(effect.payload)["data"]
    assert data["id"] == "s-1"
    assert data["email"] == "updated@example.com"


def test_staff_delete_round_trip(mock_existence_checks: None) -> None:
    """Staff delete round trip."""
    effect = Staff(id="s-1").delete()
    assert EffectType.Name(effect.type) == "DELETE_STAFF"
    assert json.loads(effect.payload) == {"data": {"id": "s-1"}}


def test_staff_create_rejects_id() -> None:
    """Staff create rejects an explicitly set id."""
    with pytest.raises(ValidationError):
        Staff(
            id="s-1",
            first_name="Ada",
            last_name="L",
            email="a@l.com",
            primary_practice_location_id="loc-1",
        ).create()


# ---------------------------------------------------------------------------
# CodingCrudEffect — shared across PatientConsentCoding,
# PatientConsentRejectionCoding, and ReasonForVisitSettingCoding.
# ---------------------------------------------------------------------------

CODING_CLASSES = [
    (PatientConsentCoding, "PATIENT_CONSENT_CODING"),
    (PatientConsentRejectionCoding, "PATIENT_CONSENT_REJECTION_CODING"),
    (ReasonForVisitSettingCoding, "REASON_FOR_VISIT_SETTING_CODING"),
]


@pytest.mark.parametrize("cls,expected_type", CODING_CLASSES)
def test_coding_create_round_trip(cls: Any, expected_type: str) -> None:
    """Coding create round trips with the right EffectType and payload keys."""
    effect = cls(
        display="Verbal consent", code="V", system="http://snomed.info/sct", active=True
    ).create()
    assert EffectType.Name(effect.type) == f"CREATE_{expected_type}"
    data = json.loads(effect.payload)["data"]
    assert {"display", "code", "system", "active"}.issubset(data.keys())


@pytest.mark.parametrize("cls,expected_type", CODING_CLASSES)
def test_coding_update_round_trip(cls: Any, expected_type: str) -> None:
    """Coding update round trips."""
    effect = cls(id="c-1", display="Updated").update()
    assert EffectType.Name(effect.type) == f"UPDATE_{expected_type}"


@pytest.mark.parametrize("cls,expected_type", CODING_CLASSES)
def test_coding_delete_round_trip(cls: Any, expected_type: str) -> None:
    """Coding delete round trips and carries only the id."""
    effect = cls(id="c-1").delete()
    assert EffectType.Name(effect.type) == f"DELETE_{expected_type}"
    assert json.loads(effect.payload) == {"data": {"id": "c-1"}}


@pytest.mark.parametrize("cls,_expected_type", CODING_CLASSES)
def test_coding_create_requires_display_code_system(cls: Any, _expected_type: str) -> None:
    """create() without display / code / system raises."""
    with pytest.raises(ValidationError):
        cls().create()


@pytest.mark.parametrize("cls,_expected_type", CODING_CLASSES)
def test_coding_update_or_delete_without_id_raises(cls: Any, _expected_type: str) -> None:
    """update() / delete() on a coding without id raises."""
    with pytest.raises(ValidationError):
        cls().update()
    with pytest.raises(ValidationError):
        cls().delete()


# ---------------------------------------------------------------------------
# StaffExternalIdentifier — both Staff and StaffExternalIdentifierModel are
# consulted on the validator path, so we mock both.
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_staff_external_identifier_checks() -> Generator[None, None, None]:
    """Mock both DB existence checks the StaffExternalIdentifier validator runs."""
    paths = [
        "canvas_sdk.effects.staff.staff_external_identifier.Staff.objects",
        "canvas_sdk.effects.staff.staff_external_identifier.StaffExternalIdentifierModel.objects",
    ]
    patches = [patch(p) for p in paths]
    mocks: list[MagicMock] = [p.start() for p in patches]
    for m in mocks:
        m.filter.return_value.exists.return_value = True
    yield
    for p in patches:
        p.stop()


def test_staff_external_identifier_create_round_trip(
    mock_staff_external_identifier_checks: None,
) -> None:
    """Staff external identifier create round trip."""
    effect = StaffExternalIdentifier(
        staff_id="s-1",
        system="https://hr.example.com/",
        value="EMP-001",
    ).create()
    assert EffectType.Name(effect.type) == "CREATE_STAFF_EXTERNAL_IDENTIFIER"
    data = json.loads(effect.payload)["data"]
    assert data["staff_id"] == "s-1"
    assert data["value"] == "EMP-001"
    assert data["system"] == "https://hr.example.com/"
    assert data["id"] is None


def test_staff_external_identifier_update_round_trip(
    mock_staff_external_identifier_checks: None,
) -> None:
    """Staff external identifier update round trip."""
    effect = StaffExternalIdentifier(id="id-1", value="EMP-002").update()
    assert EffectType.Name(effect.type) == "UPDATE_STAFF_EXTERNAL_IDENTIFIER"
    data = json.loads(effect.payload)["data"]
    assert data["id"] == "id-1"
    assert data["value"] == "EMP-002"


def test_staff_external_identifier_delete_round_trip(
    mock_staff_external_identifier_checks: None,
) -> None:
    """Staff external identifier delete round trip."""
    effect = StaffExternalIdentifier(id="id-1").delete()
    assert EffectType.Name(effect.type) == "DELETE_STAFF_EXTERNAL_IDENTIFIER"
    assert json.loads(effect.payload) == {"data": {"id": "id-1"}}


def test_staff_external_identifier_create_rejects_id(
    mock_staff_external_identifier_checks: None,
) -> None:
    """create() must not be given an id."""
    with pytest.raises(ValidationError):
        StaffExternalIdentifier(id="id-1", staff_id="s-1", system="x", value="EMP-001").create()


def test_staff_external_identifier_create_requires_value_and_staff_id() -> None:
    """create() requires value and staff_id."""
    with pytest.raises(ValidationError):
        StaffExternalIdentifier().create()


def test_staff_external_identifier_update_and_delete_require_id(
    mock_staff_external_identifier_checks: None,
) -> None:
    """update() / delete() require id."""
    with pytest.raises(ValidationError):
        StaffExternalIdentifier().update()
    with pytest.raises(ValidationError):
        StaffExternalIdentifier().delete()


def test_staff_external_identifier_rejects_unknown_staff() -> None:
    """create() rejects a staff_id that doesn't exist."""
    with patch("canvas_sdk.effects.staff.staff_external_identifier.Staff.objects") as staff_objects:
        staff_objects.filter.return_value.exists.return_value = False
        with pytest.raises(ValidationError):
            StaffExternalIdentifier(staff_id="ghost", system="x", value="EMP-001").create()


# ---------------------------------------------------------------------------
# Settings — exercise the success path for PracticeLocationSetting upsert.
# ---------------------------------------------------------------------------


def test_practice_location_setting_upsert_round_trip() -> None:
    """PracticeLocationSetting upsert round trips."""
    effect = PracticeLocationSetting(
        practice_location_id="loc-1",
        name="printed_prescription_format",
        value={"format": "letter"},
    ).upsert()
    assert EffectType.Name(effect.type) == "UPSERT_PRACTICE_LOCATION_SETTING"
    data = json.loads(effect.payload)["data"]
    assert data["practice_location_id"] == "loc-1"
    assert data["name"] == "printed_prescription_format"


# ---------------------------------------------------------------------------
# A few miscellaneous validation paths that weren't exercised above.
# ---------------------------------------------------------------------------


def test_address_create_requires_parent_and_location_fields() -> None:
    """Address create requires parent fields and a location triple."""
    with pytest.raises(ValidationError):
        Address(use=AddressUse.WORK).create()


def test_role_create_requires_name_internal_code_domain() -> None:
    """Role create requires name / internal_code / domain."""
    with pytest.raises(ValidationError):
        Role().create()


def test_staff_role_assign_requires_staff_id_and_role_identifier() -> None:
    """StaffRole assign requires staff_id and either role_code or role_id."""
    with pytest.raises(ValidationError):
        StaffRole().assign()
    # staff_id alone is still not enough — needs role_code or role_id.
    with pytest.raises(ValidationError):
        StaffRole(staff_id="s-1").assign()


def test_role_permission_group_assign_requires_both_ids() -> None:
    """RolePermissionGroup assign requires both role_id and permission_group_id."""
    with pytest.raises(ValidationError):
        RolePermissionGroup().assign()


def test_team_member_assign_requires_team_and_staff_ids() -> None:
    """TeamMember assign requires both team_id and staff_id."""
    with pytest.raises(ValidationError):
        TeamMember().assign()


def test_file_upload_requires_filename_content_type_and_payload() -> None:
    """FileUpload requires filename, content_type and content_base64."""
    with pytest.raises(ValidationError):
        FileUpload().upload()
