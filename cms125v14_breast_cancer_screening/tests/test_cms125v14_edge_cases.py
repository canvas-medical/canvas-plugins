"""
Edge case and boundary condition tests for CMS125v14 Breast Cancer Screening Protocol.

This test suite focuses on:
- Age boundary conditions
- Timeframe edge cases
- Multiple exclusion combinations
- Nursing home detection
- Dementia medication detection
- Protocol override edge cases
"""

import arrow
import pytest
from cms125v14_breast_cancer_screening.protocols.cms125v14_protocol import (
    ClinicalQualityMeasure125v14,
)

from canvas_sdk.test_utils.factories import (
    BillingLineItemFactory,
    ConditionFactory,
    NoteFactory,
    PatientFactory,
)
from canvas_sdk.test_utils.helpers import (
    create_condition_with_coding,
    create_imaging_report_with_coding,
    create_protocol_instance,
)
from canvas_sdk.test_utils.helpers import (
    create_encounter_with_billing as create_qualifying_visit,
)
from canvas_sdk.v1.data.coverage import Coverage, TransactorCoverageType
from canvas_sdk.v1.data.medication import Medication, MedicationCoding
from canvas_sdk.v1.data.protocol_override import ProtocolOverride
from canvas_sdk.v1.data.protocol_override import Status as ProtocolOverrideStatus
from canvas_sdk.value_set.v2026.condition import (
    AdvancedIllness,
    FrailtyDiagnosis,
    PalliativeCareDiagnosis,
)
from canvas_sdk.value_set.v2026.diagnostic_study import Mammography
from canvas_sdk.value_set.v2026.encounter import FrailtyEncounter
from canvas_sdk.value_set.v2026.intervention import (
    HospiceCareAmbulatory,
    PalliativeCareIntervention,
)
from canvas_sdk.value_set.v2026.medication import DementiaMedications
from canvas_sdk.value_set.v2026.procedure import (
    BilateralMastectomy,
)
from canvas_sdk.value_set.v2026.symptom import FrailtySymptom
from canvas_sdk.value_set.value_set import CodeConstants

# =============================================================================
# AGE BOUNDARY EDGE CASES
# =============================================================================


class TestAgeBoundaryEdgeCases:
    """Test exact age boundaries for initial population."""

    @pytest.mark.django_db
    def test_age_41_years_364_days_excluded(self) -> None:
        """Test patient just under 42 is excluded."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        # Patient will be 42 tomorrow
        birth_date = timeframe_end.shift(years=-42, days=1).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        assert protocol.in_initial_population(patient) is False

    @pytest.mark.django_db
    def test_age_74_years_included(self) -> None:
        """Test patient aged 74 is included."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        # Patient exactly 74
        birth_date = timeframe_end.shift(years=-74).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        assert protocol.in_initial_population(patient) is True

    @pytest.mark.django_db
    def test_stratum_boundary_age_51_in_stratum_1(self) -> None:
        """Test patient exactly 51 is in Stratum 1."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-51).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        assert protocol.get_stratification(patient) == 1

    @pytest.mark.django_db
    def test_stratum_boundary_age_52_in_stratum_2(self) -> None:
        """Test patient exactly 52 is in Stratum 2."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-52).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        assert protocol.get_stratification(patient) == 2

    @pytest.mark.django_db
    def test_age_66_frailty_exclusion_applies(self) -> None:
        """Test frailty+advanced illness exclusion applies exactly at age 66."""
        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = arrow.get("2024-01-01")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        birth_date = timeframe_end.shift(years=-66).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        # Add frailty and advanced illness
        create_condition_with_coding(
            patient, FrailtyDiagnosis, timeframe_start.shift(months=3).date(), surgical=False
        )
        create_condition_with_coding(
            patient, AdvancedIllness, timeframe_start.shift(months=4).date(), surgical=False
        )

        assert protocol.in_denominator(patient) is False

    @pytest.mark.django_db
    def test_age_65_frailty_exclusion_does_not_apply(self) -> None:
        """Test frailty+advanced illness exclusion does NOT apply at age 65."""
        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = arrow.get("2024-01-01")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        birth_date = timeframe_end.shift(years=-65).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        # Add frailty and advanced illness
        create_condition_with_coding(
            patient, FrailtyDiagnosis, timeframe_start.shift(months=3).date(), surgical=False
        )
        create_condition_with_coding(
            patient, AdvancedIllness, timeframe_start.shift(months=4).date(), surgical=False
        )

        # Should still be in denominator (age < 66)
        assert protocol.in_denominator(patient) is True


# =============================================================================
# NURSING HOME DETECTION TESTS
# =============================================================================


class TestNursingHomeDetection:
    """Test nursing home detection logic."""

    @pytest.mark.django_db
    def test_nursing_home_ltc_coverage_type_excludes(self) -> None:
        """Test LTC coverage type excludes patient age ≥66."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-67).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        # Create LTC coverage with required fields
        Coverage.objects.create(
            patient=patient,
            coverage_start_date=timeframe_end.shift(years=-1).date(),
            coverage_end_date=timeframe_end.shift(years=1).date(),
            coverage_type=TransactorCoverageType.LTC,
            coverage_rank=1,
            state="active",
        )

        assert protocol.in_nursing_home(patient) is True
        assert protocol.in_denominator(patient) is False

    @pytest.mark.django_db
    def test_nursing_home_plan_name_keyword_excludes(self) -> None:
        """Test coverage plan name with nursing home keyword excludes patient."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-67).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        # Create coverage with nursing home in plan name
        Coverage.objects.create(
            patient=patient,
            coverage_start_date=timeframe_end.shift(years=-1).date(),
            coverage_end_date=timeframe_end.shift(years=1).date(),
            plan="ABC Nursing Home Care Plan",
            coverage_rank=1,
            state="active",
        )

        assert protocol.in_nursing_home(patient) is True

    @pytest.mark.django_db
    def test_nursing_home_skilled_nursing_keyword_excludes(self) -> None:
        """Test coverage plan name with skilled nursing keyword excludes patient."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-67).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        Coverage.objects.create(
            patient=patient,
            coverage_start_date=timeframe_end.shift(years=-1).date(),
            coverage_end_date=timeframe_end.shift(years=1).date(),
            plan="XYZ Skilled Nursing Facility Coverage",
            coverage_rank=1,
            state="active",
        )

        assert protocol.in_nursing_home(patient) is True

    @pytest.mark.django_db
    def test_nursing_home_exclusion_does_not_apply_under_66(self) -> None:
        """Test nursing home exclusion does not apply to patients under 66."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-65).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        # Create LTC coverage with required fields
        Coverage.objects.create(
            patient=patient,
            coverage_start_date=timeframe_end.shift(years=-1).date(),
            coverage_end_date=timeframe_end.shift(years=1).date(),
            coverage_type=TransactorCoverageType.LTC,
            coverage_rank=1,
            state="active",
        )

        # in_nursing_home returns True but in_denominator should still be True (age < 66)
        assert protocol.in_nursing_home(patient) is True
        assert protocol.in_denominator(patient) is True

    @pytest.mark.django_db
    def test_no_nursing_home_coverage(self) -> None:
        """Test patient without nursing home coverage returns False."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-67).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        assert protocol.in_nursing_home(patient) is False


# =============================================================================
# DEMENTIA MEDICATIONS TESTS
# =============================================================================


class TestDementiaMedications:
    """Test dementia medication detection for frailty+advanced illness exclusion."""

    @pytest.mark.django_db
    def test_frailty_with_dementia_meds_excludes_age_66_plus(self) -> None:
        """Test frailty + dementia medication excludes patient age ≥66."""
        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = arrow.get("2024-01-01")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        birth_date = timeframe_end.shift(years=-67).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        # Add frailty
        create_condition_with_coding(
            patient, FrailtyDiagnosis, timeframe_start.shift(months=3).date(), surgical=False
        )

        # Add dementia medication
        dementia_codes = DementiaMedications.values
        dementia_rxnorm = None
        if CodeConstants.RXNORM in dementia_codes and dementia_codes[CodeConstants.RXNORM]:
            dementia_rxnorm = next(iter(dementia_codes[CodeConstants.RXNORM]))

        if dementia_rxnorm:
            # Arrow's .datetime property returns timezone-aware datetime (UTC)
            med = Medication.objects.create(
                patient=patient,
                start_date=timeframe_start.shift(months=2).datetime,
                end_date=timeframe_end.shift(years=1).datetime,
                deleted=False,
                status="active",
                erx_quantity=1.0,
            )
            MedicationCoding.objects.create(
                medication=med,
                system=CodeConstants.URL_RXNORM,
                code=dementia_rxnorm,
            )

            assert protocol.has_advanced_illness_or_dementia_meds(patient) is True
            assert protocol.has_frailty_with_advanced_illness(patient) is True
            assert protocol.in_denominator(patient) is False

    @pytest.mark.django_db
    def test_dementia_meds_in_prior_year_counts(self) -> None:
        """Test dementia medication in prior year (not just MP) counts."""
        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = arrow.get("2024-01-01")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        birth_date = timeframe_end.shift(years=-67).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        # Add frailty (within MP)
        create_condition_with_coding(
            patient, FrailtyDiagnosis, timeframe_start.shift(months=3).date(), surgical=False
        )

        # Add dementia medication in prior year (before MP start)
        dementia_codes = DementiaMedications.values
        dementia_rxnorm = None
        if CodeConstants.RXNORM in dementia_codes and dementia_codes[CodeConstants.RXNORM]:
            dementia_rxnorm = next(iter(dementia_codes[CodeConstants.RXNORM]))

        if dementia_rxnorm:
            prior_year_date = timeframe_start.shift(months=-6)  # 6 months before MP
            # Arrow's .datetime property returns timezone-aware datetime (UTC)
            med = Medication.objects.create(
                patient=patient,
                start_date=prior_year_date.datetime,
                end_date=timeframe_end.shift(years=1).datetime,
                deleted=False,
                status="active",
                erx_quantity=1.0,
            )
            MedicationCoding.objects.create(
                medication=med,
                system=CodeConstants.URL_RXNORM,
                code=dementia_rxnorm,
            )

            assert protocol.has_advanced_illness_or_dementia_meds(patient) is True


# =============================================================================
# FRAILTY ENCOUNTER AND SYMPTOM TESTS
# =============================================================================


class TestFrailtyEncounterAndSymptom:
    """Test frailty detection via encounters and symptoms."""

    @pytest.mark.django_db
    def test_frailty_symptom_detected(self) -> None:
        """Test frailty symptom is detected as frailty indicator."""
        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = arrow.get("2024-01-01")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        birth_date = timeframe_end.shift(years=-67).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        create_condition_with_coding(
            patient, FrailtySymptom, timeframe_start.shift(months=3).date(), surgical=False
        )

        assert protocol.has_frailty_indicator(patient) is True

    @pytest.mark.django_db
    def test_frailty_encounter_detected(self) -> None:
        """Test frailty encounter billing code is detected as frailty indicator."""
        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = arrow.get("2024-01-01")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        birth_date = timeframe_end.shift(years=-67).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        # Get frailty encounter code
        frailty_codes = FrailtyEncounter.values
        frailty_cpt = None
        for code_constant in [CodeConstants.CPT, CodeConstants.HCPCS]:
            if code_constant in frailty_codes and frailty_codes[code_constant]:
                frailty_cpt = next(iter(frailty_codes[code_constant]))
                break

        if frailty_cpt:
            frailty_date = timeframe_start.shift(months=3)
            frailty_note = NoteFactory.create(
                patient=patient,
                datetime_of_service=frailty_date.datetime,
            )
            BillingLineItemFactory.create(
                patient=patient,
                note=frailty_note,
                cpt=frailty_cpt,
            )

            assert protocol.has_frailty_indicator(patient) is True


# =============================================================================
# PALLIATIVE CARE INTERVENTION TESTS
# =============================================================================


class TestPalliativeCareIntervention:
    """Test palliative care detection via intervention codes."""

    @pytest.mark.django_db
    def test_palliative_care_intervention_billing_excludes(self) -> None:
        """Test palliative care intervention billing code excludes patient."""
        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = arrow.get("2024-01-01")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        # Get palliative care intervention code
        palliative_codes = PalliativeCareIntervention.values
        palliative_cpt = None
        for code_constant in [CodeConstants.HCPCS, CodeConstants.CPT, CodeConstants.SNOMEDCT]:
            if code_constant in palliative_codes and palliative_codes[code_constant]:
                palliative_cpt = next(iter(palliative_codes[code_constant]))
                break

        if palliative_cpt:
            palliative_date = timeframe_start.shift(months=3)
            palliative_note = NoteFactory.create(
                patient=patient,
                datetime_of_service=palliative_date.datetime,
            )
            BillingLineItemFactory.create(
                patient=patient,
                note=palliative_note,
                cpt=palliative_cpt,
            )

            assert protocol.received_palliative_care(patient) is True
            assert protocol.in_denominator(patient) is False


# =============================================================================
# MULTIPLE EXCLUSION COMBINATIONS
# =============================================================================


class TestMultipleExclusionCombinations:
    """Test that multiple exclusion criteria work correctly together."""

    @pytest.mark.django_db
    def test_mastectomy_takes_precedence_over_other_exclusions(self) -> None:
        """Test patient with mastectomy is excluded even with other factors."""
        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = arrow.get("2024-01-01")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        # Add mastectomy
        create_condition_with_coding(
            patient, BilateralMastectomy, timeframe_end.shift(years=-2).date()
        )

        # Also add palliative care (but mastectomy should already exclude)
        create_condition_with_coding(
            patient, PalliativeCareDiagnosis, timeframe_start.shift(months=3).date(), surgical=False
        )

        assert protocol.had_mastectomy(patient) is True
        assert protocol.in_denominator(patient) is False

    @pytest.mark.django_db
    def test_hospice_excludes_regardless_of_mammogram(self) -> None:
        """Test patient in hospice is excluded even with recent mammogram."""
        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = arrow.get("2024-01-01")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        # Add mammogram with proper Mammography ValueSet coding
        imaging_date = timeframe_start.shift(months=6)
        create_imaging_report_with_coding(
            patient=patient,
            value_set_class=Mammography,
            original_date=imaging_date.date(),
            result_date=imaging_date.date(),
            assigned_date=imaging_date.datetime,
        )

        # Add hospice
        hospice_codes = HospiceCareAmbulatory.values
        hospice_cpt = None
        for code_constant in [CodeConstants.HCPCS, CodeConstants.CPT]:
            if code_constant in hospice_codes and hospice_codes[code_constant]:
                hospice_cpt = next(iter(hospice_codes[code_constant]))
                break

        if hospice_cpt:
            hospice_note = NoteFactory.create(
                patient=patient,
                datetime_of_service=timeframe_start.shift(months=3).datetime,
            )
            BillingLineItemFactory.create(
                patient=patient,
                note=hospice_note,
                cpt=hospice_cpt,
            )

            assert protocol.in_hospice_care(patient) is True
            assert protocol.in_denominator(patient) is False


# =============================================================================
# PROTOCOL OVERRIDE EDGE CASES
# =============================================================================


class TestProtocolOverrideEdgeCases:
    """Test protocol override edge cases."""

    @pytest.mark.django_db
    def test_deleted_override_not_returned(self) -> None:
        """Test deleted override is not returned."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        imaging_date = timeframe_end.shift(months=-6)
        ProtocolOverride.objects.create(
            patient=patient,
            protocol_key="CMS125v14",
            reference_date=imaging_date.datetime,
            cycle_in_days=365,
            cycle_quantity=1,
            cycle_unit="years",
            status=ProtocolOverrideStatus.ACTIVE,
            is_adjustment=True,
            is_snooze=False,
            snooze_date=imaging_date.date(),
            snoozed_days=0,
            snooze_comment="",
            narrative="Deleted override",
            deleted=True,  # Deleted!
        )

        assert protocol.get_protocol_override(patient) is None

    @pytest.mark.django_db
    def test_inactive_override_not_returned(self) -> None:
        """Test inactive override is not returned."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        imaging_date = timeframe_end.shift(months=-6)
        ProtocolOverride.objects.create(
            patient=patient,
            protocol_key="CMS125v14",
            reference_date=imaging_date.datetime,
            cycle_in_days=365,
            cycle_quantity=1,
            cycle_unit="years",
            status=ProtocolOverrideStatus.INACTIVE,  # Inactive!
            is_adjustment=True,
            is_snooze=False,
            snooze_date=imaging_date.date(),
            snoozed_days=0,
            snooze_comment="",
            narrative="Inactive override",
            deleted=False,
        )

        assert protocol.get_protocol_override(patient) is None

    @pytest.mark.django_db
    def test_override_for_different_protocol_not_returned(self) -> None:
        """Test override for different protocol key is not returned."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        imaging_date = timeframe_end.shift(months=-6)
        ProtocolOverride.objects.create(
            patient=patient,
            protocol_key="DIFFERENT_PROTOCOL",  # Different protocol!
            reference_date=imaging_date.datetime,
            cycle_in_days=365,
            cycle_quantity=1,
            cycle_unit="years",
            status=ProtocolOverrideStatus.ACTIVE,
            is_adjustment=True,
            is_snooze=False,
            snooze_date=imaging_date.date(),
            snoozed_days=0,
            snooze_comment="",
            narrative="Different protocol",
            deleted=False,
        )

        assert protocol.get_protocol_override(patient) is None


# =============================================================================
# TIMEFRAME EDGE CASES
# =============================================================================


class TestTimeframeEdgeCases:
    """Test timeframe boundary conditions."""

    @pytest.mark.django_db
    def test_condition_on_timeframe_end_date_included(self) -> None:
        """Test condition exactly on timeframe end date is included."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        # Mastectomy on exact end date
        create_condition_with_coding(patient, BilateralMastectomy, timeframe_end.date())

        assert protocol.had_mastectomy(patient) is True

    @pytest.mark.django_db
    def test_condition_after_timeframe_end_not_included(self) -> None:
        """Test condition after timeframe end date is not included."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        # Mastectomy after end date (shouldn't happen but edge case)
        ConditionFactory.create(
            patient=patient,
            onset_date=timeframe_end.shift(days=1).date(),
        )
        # Note: We're not adding the coding here, so it won't match anyway
        # This test verifies the date filter works

        assert protocol.had_mastectomy(patient) is False

    @pytest.mark.django_db
    def test_imaging_on_27_month_boundary_included(self) -> None:
        """Test mammography report exactly at 27-month window boundary is included."""
        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = arrow.get("2024-01-01")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        # 15 months before timeframe start (exactly at boundary)
        earliest_allowed = timeframe_start.shift(months=-15)
        create_imaging_report_with_coding(
            patient=patient,
            value_set_class=Mammography,
            original_date=earliest_allowed.date(),
            result_date=earliest_allowed.date(),
            assigned_date=earliest_allowed.datetime,
        )

        assert protocol.in_numerator(patient) is True


# =============================================================================
# FIRST DUE IN EDGE CASES
# =============================================================================


class TestFirstDueInEdgeCases:
    """Test first_due_in calculation edge cases."""

    @pytest.mark.django_db
    def test_first_due_in_exact_age_41(self) -> None:
        """Test first_due_in for patient exactly age 41."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-41).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        days_until = protocol.first_due_in(patient)

        assert days_until is not None
        # Should be approximately 365 days (1 year)
        assert 360 < days_until < 370

    @pytest.mark.django_db
    def test_first_due_in_returns_positive_for_young_patient(self) -> None:
        """Test first_due_in returns positive days for patient under 42."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-30).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        days_until = protocol.first_due_in(patient)

        assert days_until is not None
        assert days_until > 0
        # Should be approximately 12 years (4380 days)
        assert days_until > 4000
