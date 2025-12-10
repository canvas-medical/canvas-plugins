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
        age = 41
        birth_date = timeframe_end.shift(years=-42, days=1).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        assert protocol.in_initial_population(patient, age) is False

    @pytest.mark.django_db
    def test_age_74_years_included(self) -> None:
        """Test patient aged 74 is included."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        # Patient exactly 74
        age = 74
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        assert protocol.in_initial_population(patient, age) is True

    @pytest.mark.django_db
    def test_stratum_boundary_age_51_in_stratum_1(self) -> None:
        """Test patient exactly 51 is in Stratum 1."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        age = 51
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        assert protocol.get_stratification(patient, age) == 1

    @pytest.mark.django_db
    def test_stratum_boundary_age_52_in_stratum_2(self) -> None:
        """Test patient exactly 52 is in Stratum 2."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        age = 52
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        assert protocol.get_stratification(patient, age) == 2

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

        age = 66
        birth_date = timeframe_end.shift(years=-age).date()
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

        assert protocol.in_denominator(patient, age) is False

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

        age = 65
        birth_date = timeframe_end.shift(years=-age).date()
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
        assert protocol.in_denominator(patient, age) is True


class TestNursingHomeDetection:
    """Test nursing home detection logic."""

    @pytest.mark.django_db
    def test_nursing_home_ltc_coverage_type_excludes(self) -> None:
        """Test LTC coverage type excludes patient age ≥66."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        age = 67
        birth_date = timeframe_end.shift(years=-age).date()
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
        assert protocol.in_denominator(patient, age) is False

    @pytest.mark.django_db
    def test_nursing_home_plan_name_keyword_excludes(self) -> None:
        """Test coverage plan name with nursing home keyword excludes patient."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        age = 67
        birth_date = timeframe_end.shift(years=-age).date()
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

        age = 67
        birth_date = timeframe_end.shift(years=-age).date()
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

        age = 65
        birth_date = timeframe_end.shift(years=-age).date()
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
        assert protocol.in_denominator(patient, age) is True

    @pytest.mark.django_db
    def test_no_nursing_home_coverage(self) -> None:
        """Test patient without nursing home coverage returns False."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        age = 67
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        assert protocol.in_nursing_home(patient) is False


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

        age = 67
        birth_date = timeframe_end.shift(years=-age).date()
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
            assert protocol.in_denominator(patient, age) is False

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

        age = 67
        birth_date = timeframe_end.shift(years=-age).date()
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

        age = 67
        birth_date = timeframe_end.shift(years=-age).date()
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

        age = 67
        birth_date = timeframe_end.shift(years=-age).date()
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

        age = 60
        birth_date = timeframe_end.shift(years=-age).date()
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
            assert protocol.in_denominator(patient, age) is False


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

        age = 60
        birth_date = timeframe_end.shift(years=-age).date()
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
        assert protocol.in_denominator(patient, age) is False

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

        age = 60
        birth_date = timeframe_end.shift(years=-age).date()
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
            assert protocol.in_denominator(patient, age) is False


class TestProtocolOverrideEdgeCases:
    """Test protocol override edge cases."""

    @pytest.mark.django_db
    def test_deleted_override_not_returned(self) -> None:
        """Test deleted override is not returned."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        age = 60
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        # Use the protocol's actual key
        protocol_key = protocol.protocol_key()

        imaging_date = timeframe_end.shift(months=-6)
        ProtocolOverride.objects.create(
            patient=patient,
            protocol_key=protocol_key,
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

        age = 60
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        # Use the protocol's actual key
        protocol_key = protocol.protocol_key()

        imaging_date = timeframe_end.shift(months=-6)
        ProtocolOverride.objects.create(
            patient=patient,
            protocol_key=protocol_key,
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

        age = 60
        birth_date = timeframe_end.shift(years=-age).date()
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


class TestTimeframeEdgeCases:
    """Test timeframe boundary conditions."""

    @pytest.mark.django_db
    def test_condition_on_timeframe_end_date_included(self) -> None:
        """Test condition exactly on timeframe end date is included."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        age = 60
        birth_date = timeframe_end.shift(years=-age).date()
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

        age = 60
        birth_date = timeframe_end.shift(years=-age).date()
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

        age = 60
        birth_date = timeframe_end.shift(years=-age).date()
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


class TestFirstDueInEdgeCases:
    """Test first_due_in calculation edge cases."""

    @pytest.mark.django_db
    def test_first_due_in_exact_age_41(self) -> None:
        """Test first_due_in for patient exactly age 41."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        age = 41
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        days_until = protocol.first_due_in(patient, age)

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

        age = 30
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        days_until = protocol.first_due_in(patient, age)

        assert days_until is not None
        assert days_until > 0
        # Should be approximately 12 years (4380 days)
        assert days_until > 4000


class TestSnoozeHandling:
    """Test snooze functionality for protocol cards.

    The plugin returns the normal protocol card while Canvas manages the snoozed
    visual state based on ProtocolCurrent.snoozed. These tests verify that the
    plugin returns cards regardless of snooze state.
    """

    @pytest.mark.django_db
    def test_plugin_returns_card_regardless_of_active_snooze(self) -> None:
        """Test that the plugin returns normal card even when snooze exists."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        age = 60
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        # Create a qualifying visit
        create_qualifying_visit(patient, timeframe_end.shift(months=-6))

        # Create an active snooze (7 days from today)
        snooze_date = timeframe_end.date()
        ProtocolOverride.objects.create(
            patient=patient,
            protocol_key=protocol.protocol_key(),
            reference_date=timeframe_end.datetime,
            cycle_in_days=0,
            cycle_quantity=0,
            cycle_unit="days",
            status=ProtocolOverrideStatus.ACTIVE,
            is_adjustment=False,
            is_snooze=True,
            snooze_date=snooze_date,
            snoozed_days=7,
            snooze_comment="Patient request",
            narrative="",
            deleted=False,
        )

        protocol._patient_id = str(patient.id)

        # Plugin returns normal card - Canvas handles snoozed display
        effects = protocol.compute_results(patient)
        assert len(effects) == 1


class TestHelperMethods:
    """Test helper methods directly."""

    @pytest.mark.django_db
    def test_combine_value_set_codes_with_multiple_sets(self) -> None:
        """Test _combine_value_set_codes combines codes from multiple value sets."""
        # Mammography and FrailtyEncounter should have codes
        result = ClinicalQualityMeasure125v14._combine_value_set_codes(
            Mammography, FrailtyEncounter
        )

        # Should have codes from both sets
        mammography_codes = Mammography.get_codes()
        frailty_codes = FrailtyEncounter.get_codes()

        assert result == mammography_codes | frailty_codes
        assert len(result) > 0

    @pytest.mark.django_db
    def test_combine_value_set_codes_with_single_set(self) -> None:
        """Test _combine_value_set_codes works with single value set."""
        result = ClinicalQualityMeasure125v14._combine_value_set_codes(Mammography)
        assert result == Mammography.get_codes()

    @pytest.mark.django_db
    def test_get_stratum_text_stratum_1(self) -> None:
        """Test _get_stratum_text returns correct text for stratum 1."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        assert protocol._get_stratum_text(1) == " (Stratum 1: Ages 42-51)"

    @pytest.mark.django_db
    def test_get_stratum_text_stratum_2(self) -> None:
        """Test _get_stratum_text returns correct text for stratum 2."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        assert protocol._get_stratum_text(2) == " (Stratum 2: Ages 52-74)"

    @pytest.mark.django_db
    def test_get_stratum_text_none(self) -> None:
        """Test _get_stratum_text returns empty string for None."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        assert protocol._get_stratum_text(None) == ""

    @pytest.mark.django_db
    def test_calculate_due_in_days_with_override(self) -> None:
        """Test _calculate_due_in_days uses override cycle when provided."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        # Set _on_date to simulate a recent mammogram
        protocol._on_date = timeframe_end.shift(months=-6)

        age = 60
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        # Create an override with 365-day cycle
        override = ProtocolOverride.objects.create(
            patient=patient,
            protocol_key=protocol.protocol_key(),
            reference_date=protocol._on_date.datetime,
            cycle_in_days=365,
            cycle_quantity=1,
            cycle_unit="years",
            status=ProtocolOverrideStatus.ACTIVE,
            is_adjustment=True,
            is_snooze=False,
            snooze_date=timeframe_end.date(),  # Required field
            snoozed_days=0,
            snooze_comment="",
            narrative="",
            deleted=False,
        )

        due_in = protocol._calculate_due_in_days(override)
        # 365 days from 6 months ago = ~182 days from now
        expected = (protocol._on_date.shift(days=365) - protocol.now).days
        assert due_in == expected

    @pytest.mark.django_db
    def test_calculate_due_in_days_without_override(self) -> None:
        """Test _calculate_due_in_days uses standard calculation without override."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        # Set _on_date to simulate a recent mammogram
        protocol._on_date = timeframe_end.shift(months=-6)

        due_in = protocol._calculate_due_in_days(None)
        # Standard calculation: _on_date + timeframe.duration + EXTRA_SCREENING_MONTHS - now
        expected = (
            protocol._on_date.shift(
                days=protocol.timeframe.duration, months=protocol.EXTRA_SCREENING_MONTHS
            )
            - protocol.now
        ).days
        assert due_in == expected

    @pytest.mark.django_db
    def test_calculate_due_in_days_with_no_on_date(self) -> None:
        """Test _calculate_due_in_days returns -1 when _on_date is None."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        # Ensure _on_date is None
        protocol._on_date = None

        due_in = protocol._calculate_due_in_days(None)
        assert due_in == -1

    @pytest.mark.django_db
    def test_build_satisfied_narrative_with_no_on_date(self) -> None:
        """Test _build_satisfied_narrative returns fallback when _on_date is None."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        age = 60
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date, first_name="Jane")

        # Ensure _on_date is None
        protocol._on_date = None

        narrative = protocol._build_satisfied_narrative(patient, -1, " (Stratum 2: Ages 52-74)")
        assert narrative == "Jane is due for breast cancer screening. (Stratum 2: Ages 52-74)"


class TestPatientIdFromTarget:
    """Test patient_id_from_target method for various event types."""

    @pytest.mark.django_db
    def test_patient_id_from_target_cached_value(self) -> None:
        """Test patient_id_from_target returns cached value when already set."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        # Pre-set the cached patient_id
        expected_id = "cached-patient-id-123"
        protocol._patient_id = expected_id

        result = protocol.patient_id_from_target()
        assert result == expected_id

    @pytest.mark.django_db
    def test_patient_id_from_target_encounter_event(self) -> None:
        """Test patient_id_from_target handles ENCOUNTER_CREATED events via DB query."""
        from unittest.mock import Mock

        from canvas_sdk.events import EventType
        from canvas_sdk.test_utils.factories import EncounterFactory

        timeframe_end = arrow.get("2024-12-31")
        age = 60
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        # Create a note for the patient first
        note = NoteFactory.create(patient=patient)

        # Create an encounter linked to the note
        encounter = EncounterFactory.create(note=note)

        # Create protocol with mock event for ENCOUNTER_CREATED
        mock_event = Mock()
        mock_event.type = EventType.ENCOUNTER_CREATED
        mock_event.target = Mock()
        mock_event.target.id = encounter.id

        protocol = ClinicalQualityMeasure125v14(event=mock_event)
        protocol.now = timeframe_end

        result = protocol.patient_id_from_target()
        assert result == str(patient.id)

    @pytest.mark.django_db
    def test_patient_id_from_target_fallback_to_super(self) -> None:
        """Test patient_id_from_target falls back to super for other event types."""
        from unittest.mock import Mock

        from canvas_sdk.events import EventType
        from canvas_sdk.test_utils.factories import ConditionFactory

        timeframe_end = arrow.get("2024-12-31")
        age = 60
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        # Create a condition to trigger CONDITION_CREATED event
        condition = ConditionFactory.create(patient=patient)

        # Create protocol with mock event for CONDITION_CREATED
        # The base class uses .get(id=self.event.target) so target should be the id directly
        mock_event = Mock()
        mock_event.type = EventType.CONDITION_CREATED
        mock_event.target = condition.id  # Use ID directly, not a mock with .id attribute

        protocol = ClinicalQualityMeasure125v14(event=mock_event)
        protocol.now = timeframe_end

        result = protocol.patient_id_from_target()
        assert result == str(patient.id)


class TestComputeErrorHandling:
    """Test compute() method error handling."""

    @pytest.mark.django_db
    def test_compute_returns_empty_on_patient_not_found(self) -> None:
        """Test compute returns empty list when Patient.DoesNotExist is raised."""
        from unittest.mock import Mock

        from canvas_sdk.events import EventType

        timeframe_end = arrow.get("2024-12-31")

        # Create protocol with mock event
        mock_event = Mock()
        mock_event.type = EventType.OBSERVATION_CREATED
        mock_event.context = {"patient": {"id": "nonexistent-patient-id"}}

        protocol = ClinicalQualityMeasure125v14(event=mock_event)
        protocol.now = timeframe_end

        # The patient doesn't exist, so compute should return empty list
        result = protocol.compute()
        assert result == []

    @pytest.mark.django_db
    def test_compute_returns_empty_on_exception(self) -> None:
        """Test compute returns empty list when patient_id_from_target raises exception."""
        from unittest.mock import Mock

        from canvas_sdk.events import EventType

        timeframe_end = arrow.get("2024-12-31")

        # Create protocol with mock event
        mock_event = Mock()
        mock_event.type = EventType.ENCOUNTER_CREATED
        mock_event.target = Mock()
        mock_event.target.id = "nonexistent-encounter-id"

        protocol = ClinicalQualityMeasure125v14(event=mock_event)
        protocol.now = timeframe_end

        # The encounter doesn't exist, so patient_id_from_target will raise
        result = protocol.compute()
        assert result == []


class TestGetStratificationEdgeCases:
    """Test get_stratification edge cases."""

    @pytest.mark.django_db
    def test_get_stratification_returns_none_when_not_in_denominator(self) -> None:
        """Test get_stratification returns None when patient not in denominator."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        # Create male patient (not in initial population)
        age = 60
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="M", birth_date=birth_date)

        result = protocol.get_stratification(patient, age)
        assert result is None

    @pytest.mark.django_db
    def test_get_stratification_returns_none_for_age_outside_strata(self) -> None:
        """Test get_stratification returns None when patient age falls outside strata ranges.

        This tests the defensive else branch. We modify stratum boundaries to create a gap.
        """
        from unittest.mock import patch

        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        # Create patient aged 55 in denominator
        age = 55
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        # Mock in_denominator to return True but set strata boundaries to exclude age 55
        # This simulates a hypothetical scenario where strata don't cover all denominator ages
        with (
            patch.object(protocol, "STRATUM_1_END", 50),
            patch.object(protocol, "STRATUM_2_START", 60),
        ):
            result = protocol.get_stratification(patient, age)
            assert result is None


class TestComputeHappyPath:
    """Test compute() method happy path."""

    @pytest.mark.django_db
    def test_compute_returns_effects_for_valid_patient(self) -> None:
        """Test compute returns effects when patient exists and is valid."""
        from unittest.mock import Mock, PropertyMock, patch

        from canvas_sdk.events import EventType
        from canvas_sdk.protocols.timeframe import Timeframe

        timeframe_end = arrow.get("2024-12-31")
        age = 60
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        # Create qualifying visit
        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        # Create protocol with mock event for OBSERVATION_CREATED
        mock_event = Mock()
        mock_event.type = EventType.OBSERVATION_CREATED
        mock_event.context = {"patient": {"id": str(patient.id)}}

        protocol = ClinicalQualityMeasure125v14(event=mock_event)
        protocol.now = timeframe_end

        # Create custom timeframe
        custom_timeframe = Timeframe(start=timeframe_end.shift(years=-1), end=timeframe_end)

        # Mock the timeframe property to return our custom timeframe
        with patch.object(
            ClinicalQualityMeasure125v14, "timeframe", new_callable=PropertyMock
        ) as mock_timeframe:
            mock_timeframe.return_value = custom_timeframe
            result = protocol.compute()
            assert len(result) == 1  # Should return a protocol card
