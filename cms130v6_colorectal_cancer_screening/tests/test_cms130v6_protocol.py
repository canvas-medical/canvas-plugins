"""Tests for CMS130v6 Colorectal Cancer Screening protocol."""

import json
import uuid
from typing import Iterable, Tuple

import arrow
import pytest

from canvas_sdk.effects import EffectType
from canvas_sdk.effects.protocol_card.protocol_card import ProtocolCard
from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.test_utils.factories import CanvasUserFactory, NoteFactory, PatientFactory
from canvas_sdk.v1.data import (
    Condition,
    ConditionCoding,
    ImagingReport,
    ImagingReportCoding,
    LabReport,
    LabValue,
    LabValueCoding,
    NoteType,
    ReferralReport,
    ReferralReportCoding,
)
from canvas_sdk.v1.data.note import PracticeLocationPOS
from canvas_sdk.value_set.v2022.diagnostic_study import CtColonography
from canvas_sdk.value_set.v2022.laboratory_test import FecalOccultBloodTestFobt, FitDna
from canvas_sdk.value_set.v2022.procedure import (
    CMS130v6CtColonography,
    Colonoscopy,
    FlexibleSigmoidoscopy,
    TotalColectomy,
)
from cms130v6_colorectal_cancer_screening.cms130v6_colorectal_cancer_screening.protocols.cms130v6_protocol import \
    CMS130v6ColorectalCancerScreening


# ---------- Helpers ----------

def first_or_skip(codes: Iterable[str], reason: str) -> str:
    """Return first code or skip when value set is empty (env-dependent)."""
    codes = list(codes or [])
    if not codes:
        pytest.skip(reason)
    return codes[0]


def extract_card(effects) -> dict:
    """Return protocol card 'data' from a single effect."""
    assert len(effects) == 1, f"Expected 1 effect, got {len(effects)}"
    eff = effects[0]
    assert eff.type == EffectType.ADD_OR_UPDATE_PROTOCOL_CARD
    return json.loads(eff.payload)["data"]


def set_patient_context(protocol: CMS130v6ColorectalCancerScreening, patient_id):
    protocol.event.context = {"patient": {"id": str(patient_id)}}


def mk_patient_age(now, years: int):
    return PatientFactory.create(birth_date=now.shift(years=-years).date())


def mk_lab_with_loinc(patient, when_dt, code: str, name: str = "") -> Tuple[LabReport, LabValue]:
    report = LabReport.objects.create(
        patient=patient,
        original_date=when_dt,
        assigned_date=when_dt,
        date_performed=when_dt,
        junked=False,
        requires_signature=False,
        for_test_only=False,
        version=1,
    )
    value = LabValue.objects.create(
        report=report,
        value="Negative",
        units="",
        abnormal_flag="",
        reference_range="",
        low_threshold="",
        high_threshold="",
        comment="",
        observation_status="final",
    )
    LabValueCoding.objects.create(value=value, code=code, system="http://loinc.org", name=name or code)
    return report, value


def mk_imaging_with_cpt(patient, when_date, when_assigned_dt, code: str, display: str):
    report = ImagingReport.objects.create(
        patient=patient,
        original_date=when_date,
        result_date=when_date,
        assigned_date=when_assigned_dt,
        junked=False,
        requires_signature=False,
        name=display,
    )
    ImagingReportCoding.objects.create(report=report, code=code, system="http://www.ama-assn.org/go/cpt", display=display)
    return report


def mk_referral_with_cpt(patient, when_date, code: str, display: str, specialty="Gastroenterology"):
    report = ReferralReport.objects.create(
        patient=patient,
        original_date=when_date,
        junked=False,
        requires_signature=False,
        specialty=specialty,
    )
    ReferralReportCoding.objects.create(report=report, code=code, system="http://www.ama-assn.org/go/cpt", display=display)
    return report


# ---------- Fixtures ----------

@pytest.fixture
def now():
    return arrow.get("2025-01-15T12:00:00Z")


@pytest.fixture
def protocol_instance(now):
    event_request = EventRequest(type=EventType.CRON, context='{"patient": {"id": "test-patient-id"}}')
    event = Event(event_request=event_request)
    protocol = CMS130v6ColorectalCancerScreening(event=event, secrets={}, environment={})
    protocol.now = now
    return protocol


@pytest.fixture
def patient_age_62(now):
    return mk_patient_age(now, 62)


@pytest.fixture
def patient_age_45(now):
    return mk_patient_age(now, 45)


@pytest.fixture
def patient_age_80(now):
    return mk_patient_age(now, 80)


@pytest.fixture
def eligible_note(now, patient_age_62):
    """Encounter within period with NoteType coded as Office Visit (SNOMED 308335008)."""
    note = NoteFactory.create(patient=patient_age_62, datetime_of_service=now.shift(months=-6).datetime)
    from canvas_sdk.v1.data.note import NoteTypeCategories

    note_type = NoteType.objects.create(
        code="308335008",
        system="http://snomed.info/sct",
        display="Office Visit",
        name="Office Visit",
        icon="office",
        category=NoteTypeCategories.ENCOUNTER,
        rank=1,
        is_default_appointment_type=False,
        is_scheduleable=True,
        is_telehealth=False,
        is_billable=True,
        defer_place_of_service_to_practice_location=False,
        available_places_of_service=[],
        default_place_of_service=PracticeLocationPOS.OFFICE,
        is_system_managed=False,
        is_visible=True,
        is_active=True,
        unique_identifier=uuid.uuid4(),
        deprecated_at=now.shift(years=100).datetime,
        is_patient_required=False,
        allow_custom_title=False,
        is_scheduleable_via_patient_portal=False,
        online_duration=0,
    )
    note.note_type_version = note_type
    note.save()
    return note


# ---------- Tests ----------

@pytest.mark.django_db
class TestComputeGuards:
    def test_returns_empty_when_no_patient_in_context(self, protocol_instance):
        protocol_instance.event.context = {}
        assert protocol_instance.compute() == []

    def test_returns_empty_when_patient_not_found(self, protocol_instance):
        protocol_instance.event.context = {"patient": {"id": "00000000-0000-0000-0000-000000000000"}}
        assert protocol_instance.compute() == []


@pytest.mark.django_db
class TestDue_NoScreening:
    def test_due_when_in_population_and_no_prior_screening(self, protocol_instance, patient_age_62, eligible_note):
        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())
        assert card["status"] == ProtocolCard.Status.DUE.value
        assert "colorectal cancer screening" in card["narrative"].lower()
        assert isinstance(card.get("recommendations", []), list)


@pytest.mark.django_db
class TestNumeratorByLabs:
    def test_fobt_within_1_year_satisfies(self, now, protocol_instance, patient_age_62, eligible_note):
        code = first_or_skip(FecalOccultBloodTestFobt.LOINC, "FOBT LOINC set is empty")
        mk_lab_with_loinc(patient_age_62, now.shift(months=-3).datetime, code, "FOBT")
        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())
        assert card["status"] == ProtocolCard.Status.SATISFIED.value
        assert "fobt" in card["narrative"].lower() or "screening" in card["narrative"].lower()

    def test_fitdna_within_3_years_satisfies(self, now, protocol_instance, patient_age_62, eligible_note):
        code = first_or_skip(FitDna.LOINC, "FIT-DNA LOINC set is empty")
        mk_lab_with_loinc(patient_age_62, now.shift(years=-2).datetime, code, "FIT-DNA")
        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())
        assert card["status"] == ProtocolCard.Status.SATISFIED.value


@pytest.mark.django_db
class TestNumeratorByProcedures:
    def test_colonoscopy_within_10_years_satisfies(self, now, protocol_instance, patient_age_62, eligible_note):
        cpt = first_or_skip(getattr(Colonoscopy, "CPT", []), "Colonoscopy CPT set is empty")
        mk_imaging_with_cpt(
            patient_age_62, when_date=now.shift(years=-5).date(), when_assigned_dt=now.shift(years=-5).datetime, code=cpt, display="Colonoscopy"
        )
        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())
        assert card["status"] == ProtocolCard.Status.SATISFIED.value

    def test_flexible_sigmoidoscopy_within_5_years_satisfies(self, now, protocol_instance, patient_age_62, eligible_note):
        cpt = first_or_skip(getattr(FlexibleSigmoidoscopy, "CPT", []), "Flexible Sigmoidoscopy CPT set is empty")
        mk_referral_with_cpt(patient_age_62, when_date=now.shift(years=-3).date(), code=cpt, display="Flexible Sigmoidoscopy")
        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())
        assert card["status"] == ProtocolCard.Status.SATISFIED.value

    def test_ct_colonography_within_5_years_satisfies(self, now, protocol_instance, patient_age_62, eligible_note):
        cpt_codes = list(getattr(CMS130v6CtColonography, "CPT", []) or getattr(CtColonography, "CPT", []))
        cpt = first_or_skip(cpt_codes, "CT Colonography CPT set is empty")
        mk_imaging_with_cpt(
            patient_age_62, when_date=now.shift(years=-2).date(), when_assigned_dt=now.shift(years=-2).datetime, code=cpt, display="CT Colonography"
        )
        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())
        assert card["status"] == ProtocolCard.Status.SATISFIED.value


@pytest.mark.django_db
class TestExclusions_NotApplicable:
    @pytest.mark.parametrize("age", [45, 80], ids=["too_young_45", "too_old_80"])
    def test_age_out_of_range_is_not_applicable(self, now, protocol_instance, eligible_note, age):
        patient = mk_patient_age(now, age)
        set_patient_context(protocol_instance, patient.id)
        card = extract_card(protocol_instance.compute())
        assert card["status"] == ProtocolCard.Status.NOT_APPLICABLE.value

    def test_hospice_place_of_service_within_period_is_not_applicable(self, now, protocol_instance, patient_age_62):
        NoteFactory.create(
            patient=patient_age_62,
            datetime_of_service=now.shift(months=-6).datetime,
            place_of_service=PracticeLocationPOS.HOSPICE,
        )
        NoteFactory.create(patient=patient_age_62, datetime_of_service=now.shift(months=-6).datetime)
        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())
        assert card["status"] == ProtocolCard.Status.NOT_APPLICABLE.value


@pytest.mark.django_db
class TestDueWhenScreeningsStale:
    @pytest.mark.parametrize(
        "months_ago,code_getter,display",
        [
            (24, lambda: first_or_skip(FecalOccultBloodTestFobt.LOINC, "FOBT LOINC empty"), "FOBT"),
            (48, lambda: first_or_skip(FitDna.LOINC, "FIT-DNA LOINC empty"), "FIT-DNA"),
        ],
        ids=["fobt_too_old", "fitdna_too_old"],
    )
    def test_lab_screenings_outside_window_yield_due(self, now, protocol_instance, patient_age_62, eligible_note, months_ago, code_getter, display):
        code = code_getter()
        mk_lab_with_loinc(patient_age_62, now.shift(months=-months_ago).datetime, code, display)
        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())
        assert card["status"] == ProtocolCard.Status.DUE.value

    @pytest.mark.parametrize(
        "years_ago,code_getter,display",
        [
            (12, lambda: first_or_skip(getattr(Colonoscopy, "CPT", []), "Colonoscopy CPT empty"), "Colonoscopy"),
            (6, lambda: first_or_skip(getattr(FlexibleSigmoidoscopy, "CPT", []), "Flexible Sigmoidoscopy CPT empty"), "Flexible Sigmoidoscopy"),
            (6, lambda: first_or_skip(list(getattr(CMS130v6CtColonography, "CPT", [])) or list(getattr(CtColonography, "CPT", [])), "CT Colonography CPT empty"), "CT Colonography"),
        ],
        ids=["colonoscopy_too_old", "flex_sig_too_old", "ct_colonography_too_old"],
    )
    def test_procedure_screenings_outside_window_yield_due(self, now, protocol_instance, patient_age_62, eligible_note, years_ago, code_getter, display):
        code = code_getter()
        if display == "Flexible Sigmoidoscopy":
            mk_referral_with_cpt(patient_age_62, now.shift(years=-years_ago).date(), code, display)
        else:
            mk_imaging_with_cpt(
                patient_age_62,
                when_date=now.shift(years=-years_ago).date(),
                when_assigned_dt=now.shift(years=-years_ago).datetime,
                code=code,
                display=display,
            )
        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())
        assert card["status"] == ProtocolCard.Status.DUE.value


@pytest.mark.django_db
class TestAgeBoundaries_InPopulationWithFloor365:
    @pytest.mark.parametrize("age", [50, 75], ids=["exact_50", "exact_75"])
    def test_boundary_ages_in_population(self, now, protocol_instance, eligible_note, age):
        patient = mk_patient_age(now, age)
        n = NoteFactory.create(patient=patient, datetime_of_service=now.shift(months=-6).datetime)
        n.note_type_version = eligible_note.note_type_version
        n.save()
        set_patient_context(protocol_instance, patient.id)
        card = extract_card(protocol_instance.compute())
        assert card["status"] in (ProtocolCard.Status.DUE.value, ProtocolCard.Status.SATISFIED.value)

    def test_49y_364d_is_in_population_with_floor_calc(self, now, protocol_instance, eligible_note):
        patient = PatientFactory.create(birth_date=now.shift(years=-50, days=+1).date())
        n = NoteFactory.create(patient=patient, datetime_of_service=now.shift(months=-2).datetime)
        n.note_type_version = eligible_note.note_type_version
        n.save()
        set_patient_context(protocol_instance, patient.id)
        card = extract_card(protocol_instance.compute())
        assert card["status"] in (ProtocolCard.Status.DUE.value, ProtocolCard.Status.SATISFIED.value)

    def test_75y_plus_1d_is_in_population_with_floor_calc(self, now, protocol_instance, eligible_note):
        patient = PatientFactory.create(birth_date=now.shift(years=-75, days=-1).date())
        n = NoteFactory.create(patient=patient, datetime_of_service=now.shift(months=-2).datetime)
        n.note_type_version = eligible_note.note_type_version
        n.save()
        set_patient_context(protocol_instance, patient.id)
        card = extract_card(protocol_instance.compute())
        assert card["status"] in (ProtocolCard.Status.DUE.value, ProtocolCard.Status.SATISFIED.value)


@pytest.mark.django_db
class TestMostRecentScreeningWins:
    def test_most_recent_colonoscopy_overrides_older_fobt(self, now, protocol_instance, patient_age_62, eligible_note):
        fobt_code = first_or_skip(FecalOccultBloodTestFobt.LOINC, "FOBT LOINC empty")
        mk_lab_with_loinc(patient_age_62, now.shift(years=-2).datetime, fobt_code, "FOBT")
        col_cpt = first_or_skip(getattr(Colonoscopy, "CPT", []), "Colonoscopy CPT empty")
        mk_imaging_with_cpt(
            patient_age_62, when_date=now.shift(years=-1).date(), when_assigned_dt=now.shift(years=-1).datetime, code=col_cpt, display="Colonoscopy"
        )
        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())
        assert card["status"] == ProtocolCard.Status.SATISFIED.value
        assert "colonoscopy" in card["narrative"].lower()


@pytest.mark.django_db
class TestPopulationEdgeBehaviors:
    def test_optimistic_encounter_rule_allows_processing(self, now, protocol_instance, patient_age_62):
        set_patient_context(protocol_instance, patient_age_62.id)
        effects = protocol_instance.compute()
        assert effects  # compute proceeds even if no eligible encounter is matched

    def test_hospice_note_outside_period_does_not_exclude(self, now, protocol_instance, eligible_note, patient_age_62):
        NoteFactory.create(
            patient=patient_age_62,
            datetime_of_service=now.shift(years=-2).datetime,
            place_of_service=PracticeLocationPOS.HOSPICE,
        )
        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())
        assert card["status"] in (ProtocolCard.Status.DUE.value, ProtocolCard.Status.SATISFIED.value)

    def test_total_colectomy_resolved_before_period_does_not_exclude(self, now, protocol_instance, eligible_note, patient_age_62):
        user = CanvasUserFactory()
        condition = Condition.objects.create(
            patient=patient_age_62,
            onset_date=now.shift(years=-8).date(),
            resolution_date=now.shift(years=-6).date(),
            clinical_status="resolved",
            deleted=False,
            surgical=False,
            committer=user,
        )
        codes = list(getattr(TotalColectomy, "SNOMEDCT", [])) or list(getattr(TotalColectomy, "CPT", []))
        if not codes:
            pytest.skip("TotalColectomy codes missing in this environment")
        ConditionCoding.objects.create(
            condition=condition,
            code=codes[0],
            system="http://snomed.info/sct" if getattr(TotalColectomy, "SNOMEDCT", []) else "http://www.ama-assn.org/go/cpt",
            display="Total Colectomy",
        )
        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())
        assert card["status"] in (ProtocolCard.Status.DUE.value, ProtocolCard.Status.SATISFIED.value)


@pytest.mark.django_db
class TestDueCardRecommendations:
    def test_recommendations_include_known_titles_when_available(self, protocol_instance, patient_age_62, eligible_note):
        set_patient_context(protocol_instance, patient_age_62.id)
        card = extract_card(protocol_instance.compute())
        titles = {r.get("title", "") for r in card.get("recommendations", [])}
        expected = [
            "Order FOBT",
            "Order FIT-DNA",
            "Order CT Colonography",
            "Refer for Colonoscopy",
            "Refer for Flexible Sigmoidoscopy",
        ]
        assert any(any(bit in t for bit in expected) for t in titles)
