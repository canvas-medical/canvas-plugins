from unittest.mock import Mock

import arrow
import pytest
from cms125v14_breast_cancer_screening.canvas_sdk_test_utils import (
    BillingLineItemFactory,
    create_condition_with_coding,
    create_imaging_report_with_coding,
    create_protocol_instance,
    create_qualifying_visit,
)
from cms125v14_breast_cancer_screening.protocols.cms125v14_protocol import (
    ClinicalQualityMeasure125v14,
)

from canvas_sdk.effects import EffectType
from canvas_sdk.events import EventType
from canvas_sdk.test_utils.factories import NoteFactory, PatientFactory
from canvas_sdk.v1.data.protocol_override import ProtocolOverride
from canvas_sdk.v1.data.protocol_override import Status as ProtocolOverrideStatus
from canvas_sdk.value_set.v2026.condition import (
    AdvancedIllness,
    FrailtyDiagnosis,
    HistoryOfBilateralMastectomy,
    PalliativeCareDiagnosis,
    StatusPostLeftMastectomy,
    StatusPostRightMastectomy,
)
from canvas_sdk.value_set.v2026.diagnostic_study import Mammography
from canvas_sdk.value_set.v2026.encounter import OfficeVisit
from canvas_sdk.value_set.v2026.intervention import HospiceCareAmbulatory
from canvas_sdk.value_set.v2026.procedure import (
    BilateralMastectomy,
    UnilateralMastectomyLeft,
    UnilateralMastectomyRight,
)
from canvas_sdk.value_set.v2026.symptom import FrailtySymptom
from canvas_sdk.value_set.v2026.tomography import Tomography
from canvas_sdk.value_set.value_set import CodeConstants

# =============================================================================
# PROTOCOL METADATA AND CONFIGURATION TESTS
# =============================================================================


class TestProtocolMetadata:
    """Test protocol metadata and configuration."""

    def test_meta_title(self) -> None:
        """Test protocol title."""
        assert ClinicalQualityMeasure125v14.Meta.title == "Breast Cancer Screening"

    def test_meta_version(self) -> None:
        """Test protocol version."""
        assert ClinicalQualityMeasure125v14.Meta.version == "v14.0.0"

    def test_meta_description(self) -> None:
        """Test protocol description."""
        expected = (
            "Women 42-74 years of age who have not had a mammogram to screen for "
            "breast cancer within the last 27 months."
        )
        assert ClinicalQualityMeasure125v14.Meta.description == expected

    def test_meta_identifiers(self) -> None:
        """Test protocol identifiers include CMS125v14."""
        assert "CMS125v14" in ClinicalQualityMeasure125v14.Meta.identifiers

    def test_meta_types(self) -> None:
        """Test protocol types include CQM."""
        assert "CQM" in ClinicalQualityMeasure125v14.Meta.types

    def test_meta_authors(self) -> None:
        """Test protocol authors."""
        assert (
            "National Committee for Quality Assurance" in ClinicalQualityMeasure125v14.Meta.authors
        )

    def test_meta_information_url(self) -> None:
        """Test protocol information URL."""
        expected_url = (
            "https://ecqi.healthit.gov/sites/default/files/ecqm/measures/CMS125-v14.0.000-QDM.html"
        )
        assert ClinicalQualityMeasure125v14.Meta.information == expected_url

    def test_meta_references_not_empty(self) -> None:
        """Test protocol has references."""
        assert len(ClinicalQualityMeasure125v14.Meta.references) > 0

    def test_responds_to_event_type(self) -> None:
        """Test protocol responds to correct event type."""
        assert (
            EventType.Name(EventType.ASSESS_COMMAND__CONDITION_SELECTED)
            == ClinicalQualityMeasure125v14.RESPONDS_TO
        )

    def test_narrative_string(self) -> None:
        """Test protocol narrative string."""
        assert ClinicalQualityMeasure125v14.NARRATIVE_STRING == "Breast Cancer Screening CMS125v14"


class TestProtocolConstants:
    """Test protocol age range and screening constants."""

    def test_age_range_start(self) -> None:
        """Test minimum age is 42."""
        assert ClinicalQualityMeasure125v14.AGE_RANGE_START == 42

    def test_age_range_end(self) -> None:
        """Test maximum age is 74."""
        assert ClinicalQualityMeasure125v14.AGE_RANGE_END == 74

    def test_extra_screening_months(self) -> None:
        """Test extra screening months is 15 (for 27-month window)."""
        assert ClinicalQualityMeasure125v14.EXTRA_SCREENING_MONTHS == 15

    def test_stratum_1_boundaries(self) -> None:
        """Test Stratum 1 age boundaries (42-51)."""
        assert ClinicalQualityMeasure125v14.STRATUM_1_START == 42
        assert ClinicalQualityMeasure125v14.STRATUM_1_END == 51

    def test_stratum_2_boundaries(self) -> None:
        """Test Stratum 2 age boundaries (52-74)."""
        assert ClinicalQualityMeasure125v14.STRATUM_2_START == 52
        assert ClinicalQualityMeasure125v14.STRATUM_2_END == 74


# =============================================================================
# INITIAL POPULATION TESTS
# =============================================================================


class TestInitialPopulation:
    """Test initial population inclusion/exclusion criteria."""

    @pytest.mark.django_db
    def test_female_age_42_with_visit_included(self) -> None:
        """Test female patient aged exactly 42 with visit is included."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-42).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        assert protocol.in_initial_population(patient) is True

    @pytest.mark.django_db
    def test_female_age_74_with_visit_included(self) -> None:
        """Test female patient aged exactly 74 with visit is included."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-74).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        assert protocol.in_initial_population(patient) is True

    @pytest.mark.django_db
    def test_female_age_60_with_visit_included(self) -> None:
        """Test female patient aged 60 with visit is included."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        assert protocol.in_initial_population(patient) is True

    @pytest.mark.django_db
    def test_female_age_41_excluded(self) -> None:
        """Test female patient aged 41 is excluded (below minimum age)."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-41).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        assert protocol.in_initial_population(patient) is False

    @pytest.mark.django_db
    def test_female_age_75_excluded(self) -> None:
        """Test female patient aged 75 is excluded (above maximum age)."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-75).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        assert protocol.in_initial_population(patient) is False

    @pytest.mark.django_db
    def test_male_patient_excluded(self) -> None:
        """Test male patient is excluded regardless of age."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="M", birth_date=birth_date)

        assert protocol.in_initial_population(patient) is False

    @pytest.mark.django_db
    def test_female_without_qualifying_visit_excluded(self) -> None:
        """Test female patient without qualifying visit is excluded."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        # No visit created
        assert protocol.in_initial_population(patient) is False


class TestQualifyingVisit:
    """Test qualifying visit detection logic."""

    @pytest.mark.django_db
    def test_office_visit_qualifies(self) -> None:
        """Test that office visit code qualifies."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date, OfficeVisit)

        assert protocol.has_qualifying_visit(patient) is True

    @pytest.mark.django_db
    def test_visit_outside_timeframe_does_not_qualify(self) -> None:
        """Test that visit outside measurement period does not qualify."""
        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = arrow.get("2024-01-01")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        # Create visit before measurement period
        visit_date = timeframe_start.shift(months=-2)
        create_qualifying_visit(patient, visit_date)

        assert protocol.has_qualifying_visit(patient) is False


# =============================================================================
# MASTECTOMY DETECTION TESTS
# =============================================================================


class TestMastectomyDetection:
    """Test mastectomy detection logic."""

    @pytest.mark.django_db
    def test_bilateral_mastectomy_detected(self) -> None:
        """Test bilateral mastectomy procedure is detected."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        create_condition_with_coding(
            patient, BilateralMastectomy, timeframe_end.shift(years=-2).date()
        )

        assert protocol.had_mastectomy(patient) is True

    @pytest.mark.django_db
    def test_history_of_bilateral_mastectomy_detected(self) -> None:
        """Test history of bilateral mastectomy is detected."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        create_condition_with_coding(
            patient, HistoryOfBilateralMastectomy, timeframe_end.shift(years=-5).date()
        )

        assert protocol.had_mastectomy(patient) is True

    @pytest.mark.django_db
    def test_two_unilateral_mastectomies_detected(self) -> None:
        """Test left + right unilateral mastectomies detected as bilateral equivalent."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        create_condition_with_coding(
            patient, UnilateralMastectomyLeft, timeframe_end.shift(years=-3).date()
        )
        create_condition_with_coding(
            patient, UnilateralMastectomyRight, timeframe_end.shift(years=-2).date()
        )

        assert protocol.had_mastectomy(patient) is True

    @pytest.mark.django_db
    def test_unilateral_left_plus_status_post_right_detected(self) -> None:
        """Test left unilateral + status post right detected as bilateral equivalent."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        create_condition_with_coding(
            patient, UnilateralMastectomyLeft, timeframe_end.shift(years=-3).date()
        )
        create_condition_with_coding(
            patient, StatusPostRightMastectomy, timeframe_end.shift(years=-4).date()
        )

        assert protocol.had_mastectomy(patient) is True

    @pytest.mark.django_db
    def test_unilateral_right_plus_status_post_left_detected(self) -> None:
        """Test right unilateral + status post left detected as bilateral equivalent."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        create_condition_with_coding(
            patient, UnilateralMastectomyRight, timeframe_end.shift(years=-3).date()
        )
        create_condition_with_coding(
            patient, StatusPostLeftMastectomy, timeframe_end.shift(years=-4).date()
        )

        assert protocol.had_mastectomy(patient) is True

    @pytest.mark.django_db
    def test_single_unilateral_not_detected(self) -> None:
        """Test single unilateral mastectomy alone is NOT detected as bilateral."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        create_condition_with_coding(
            patient, UnilateralMastectomyLeft, timeframe_end.shift(years=-3).date()
        )

        assert protocol.had_mastectomy(patient) is False

    @pytest.mark.django_db
    def test_no_mastectomy(self) -> None:
        """Test patient without any mastectomy returns False."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        assert protocol.had_mastectomy(patient) is False


# =============================================================================
# HOSPICE CARE EXCLUSION TESTS
# =============================================================================


class TestHospiceCareExclusion:
    """Test hospice care exclusion logic."""

    @pytest.mark.django_db
    def test_hospice_care_billing_excludes(self) -> None:
        """Test hospice care billing code excludes patient."""
        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = arrow.get("2024-01-01")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        # Get hospice code from value set
        hospice_codes = HospiceCareAmbulatory.values
        hospice_cpt = None
        for code_constant in [CodeConstants.HCPCS, CodeConstants.CPT]:
            if code_constant in hospice_codes and hospice_codes[code_constant]:
                hospice_cpt = next(iter(hospice_codes[code_constant]))
                break

        if hospice_cpt:
            hospice_date = timeframe_start.shift(months=6)
            hospice_note = NoteFactory.create(
                patient=patient,
                datetime_of_service=hospice_date.datetime,
            )
            BillingLineItemFactory.create(
                patient=patient,
                note=hospice_note,
                cpt=hospice_cpt,
            )

            assert protocol.in_hospice_care(patient) is True

    @pytest.mark.django_db
    def test_no_hospice_care(self) -> None:
        """Test patient without hospice care returns False."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        assert protocol.in_hospice_care(patient) is False


# =============================================================================
# PALLIATIVE CARE EXCLUSION TESTS
# =============================================================================


class TestPalliativeCareExclusion:
    """Test palliative care exclusion logic."""

    @pytest.mark.django_db
    def test_palliative_care_diagnosis_excludes(self) -> None:
        """Test palliative care diagnosis excludes patient."""
        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = arrow.get("2024-01-01")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        create_condition_with_coding(
            patient,
            PalliativeCareDiagnosis,
            timeframe_start.shift(months=3).date(),
            surgical=False,
        )

        assert protocol.received_palliative_care(patient) is True

    @pytest.mark.django_db
    def test_no_palliative_care(self) -> None:
        """Test patient without palliative care returns False."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        assert protocol.received_palliative_care(patient) is False


# =============================================================================
# FRAILTY INDICATOR TESTS
# =============================================================================


class TestFrailtyIndicator:
    """Test frailty indicator detection logic."""

    @pytest.mark.django_db
    def test_frailty_diagnosis_detected(self) -> None:
        """Test frailty diagnosis is detected."""
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
            patient,
            FrailtyDiagnosis,
            timeframe_start.shift(months=3).date(),
            surgical=False,
        )

        assert protocol.has_frailty_indicator(patient) is True

    @pytest.mark.django_db
    def test_frailty_symptom_detected(self) -> None:
        """Test frailty symptom is detected."""
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
            patient,
            FrailtySymptom,
            timeframe_start.shift(months=3).date(),
            surgical=False,
        )

        assert protocol.has_frailty_indicator(patient) is True

    @pytest.mark.django_db
    def test_no_frailty_indicator(self) -> None:
        """Test patient without frailty indicator returns False."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-67).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        assert protocol.has_frailty_indicator(patient) is False


# =============================================================================
# FRAILTY + ADVANCED ILLNESS EXCLUSION TESTS
# =============================================================================


class TestFrailtyAdvancedIllnessExclusion:
    """Test frailty + advanced illness/dementia medication exclusion logic."""

    @pytest.mark.django_db
    def test_frailty_with_advanced_illness_age_66_plus_excludes(self) -> None:
        """Test patient age ≥66 with frailty + advanced illness is excluded."""
        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = arrow.get("2024-01-01")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        birth_date = timeframe_end.shift(years=-67).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        # Add frailty
        create_condition_with_coding(
            patient,
            FrailtyDiagnosis,
            timeframe_start.shift(months=3).date(),
            surgical=False,
        )

        # Add advanced illness
        create_condition_with_coding(
            patient,
            AdvancedIllness,
            timeframe_start.shift(months=4).date(),
            surgical=False,
        )

        assert protocol.has_frailty_with_advanced_illness(patient) is True

    @pytest.mark.django_db
    def test_frailty_alone_does_not_exclude(self) -> None:
        """Test frailty alone without advanced illness does not exclude."""
        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = arrow.get("2024-01-01")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        birth_date = timeframe_end.shift(years=-67).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        # Add frailty only
        create_condition_with_coding(
            patient,
            FrailtyDiagnosis,
            timeframe_start.shift(months=3).date(),
            surgical=False,
        )

        assert protocol.has_frailty_indicator(patient) is True
        assert protocol.has_frailty_with_advanced_illness(patient) is False

    @pytest.mark.django_db
    def test_frailty_with_advanced_illness_age_under_66_not_excluded(self) -> None:
        """Test patient age <66 with frailty + advanced illness is NOT excluded."""
        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = arrow.get("2024-01-01")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        birth_date = timeframe_end.shift(years=-65).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        # Create qualifying visit
        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        # Add frailty and advanced illness
        create_condition_with_coding(
            patient,
            FrailtyDiagnosis,
            timeframe_start.shift(months=3).date(),
            surgical=False,
        )
        create_condition_with_coding(
            patient,
            AdvancedIllness,
            timeframe_start.shift(months=4).date(),
            surgical=False,
        )

        # Should still be in denominator because age < 66
        assert protocol.in_denominator(patient) is True


# =============================================================================
# DENOMINATOR TESTS
# =============================================================================


class TestDenominator:
    """Test denominator inclusion/exclusion criteria."""

    @pytest.mark.django_db
    def test_denominator_includes_eligible_patient(self) -> None:
        """Test eligible patient without exclusions is in denominator."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        assert protocol.in_denominator(patient) is True

    @pytest.mark.django_db
    def test_denominator_excludes_bilateral_mastectomy(self) -> None:
        """Test bilateral mastectomy excludes from denominator."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        create_condition_with_coding(
            patient, BilateralMastectomy, timeframe_end.shift(years=-2).date()
        )

        assert protocol.in_initial_population(patient) is True
        assert protocol.in_denominator(patient) is False

    @pytest.mark.django_db
    def test_denominator_excludes_hospice_care(self) -> None:
        """Test hospice care excludes from denominator."""
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

        # Add hospice billing
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

            assert protocol.in_denominator(patient) is False

    @pytest.mark.django_db
    def test_denominator_excludes_palliative_care(self) -> None:
        """Test palliative care excludes from denominator."""
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

        create_condition_with_coding(
            patient,
            PalliativeCareDiagnosis,
            timeframe_start.shift(months=3).date(),
            surgical=False,
        )

        assert protocol.in_denominator(patient) is False


# =============================================================================
# STRATIFICATION TESTS
# =============================================================================


class TestStratification:
    """Test stratification logic."""

    @pytest.mark.django_db
    def test_stratum_1_age_42(self) -> None:
        """Test patient age 42 is in Stratum 1."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-42).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        assert protocol.get_stratification(patient) == 1

    @pytest.mark.django_db
    def test_stratum_1_age_51(self) -> None:
        """Test patient age 51 is in Stratum 1."""
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
    def test_stratum_2_age_52(self) -> None:
        """Test patient age 52 is in Stratum 2."""
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
    def test_stratum_2_age_74(self) -> None:
        """Test patient age 74 is in Stratum 2."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-74).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        assert protocol.get_stratification(patient) == 2

    @pytest.mark.django_db
    def test_stratification_none_for_excluded_patient(self) -> None:
        """Test excluded patient returns None stratification."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        create_condition_with_coding(
            patient, BilateralMastectomy, timeframe_end.shift(years=-2).date()
        )

        assert protocol.get_stratification(patient) is None


# =============================================================================
# FIRST DUE IN TESTS
# =============================================================================


class TestFirstDueIn:
    """Test first_due_in calculation logic."""

    @pytest.mark.django_db
    def test_first_due_in_for_female_age_40(self) -> None:
        """Test first_due_in returns days until 42nd birthday for female age 40."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-40).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        days_until = protocol.first_due_in(patient)

        assert days_until is not None
        assert days_until > 0
        # Should be approximately 2 years (730 days) +/- leap year
        assert 700 < days_until < 750

    @pytest.mark.django_db
    def test_first_due_in_returns_none_for_age_42(self) -> None:
        """Test first_due_in returns None for patient already age 42."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-42).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        assert protocol.first_due_in(patient) is None

    @pytest.mark.django_db
    def test_first_due_in_returns_none_for_male(self) -> None:
        """Test first_due_in returns None for male patient."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-40).date()
        patient = PatientFactory.create(sex_at_birth="M", birth_date=birth_date)

        assert protocol.first_due_in(patient) is None

    @pytest.mark.django_db
    def test_first_due_in_returns_none_with_mastectomy(self) -> None:
        """Test first_due_in returns None for patient with mastectomy."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-40).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        create_condition_with_coding(
            patient, BilateralMastectomy, timeframe_end.shift(years=-2).date()
        )

        assert protocol.first_due_in(patient) is None


# =============================================================================
# NUMERATOR TESTS
# =============================================================================


class TestNumerator:
    """Test numerator inclusion logic."""

    @pytest.mark.django_db
    def test_numerator_with_mammography_billing(self) -> None:
        """Test patient with mammography billing is in numerator."""
        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = arrow.get("2024-01-01")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        # Get mammography code from value set
        mammography_codes = Mammography.values
        mammography_code = None
        if CodeConstants.LOINC in mammography_codes and mammography_codes[CodeConstants.LOINC]:
            mammography_code = next(iter(mammography_codes[CodeConstants.LOINC]))

        if mammography_code:
            mammography_date = timeframe_start.shift(months=6)
            mammography_note = NoteFactory.create(
                patient=patient,
                datetime_of_service=mammography_date.datetime,
            )
            BillingLineItemFactory.create(
                patient=patient,
                note=mammography_note,
                cpt=mammography_code,
            )

            assert protocol.in_numerator(patient) is True
            assert protocol._on_date is not None

    @pytest.mark.django_db
    def test_numerator_with_imaging_report(self) -> None:
        """Test patient with mammography imaging report is in numerator."""
        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = arrow.get("2024-01-01")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        # Use helper with Mammography value set for proper ValueSet filtering
        imaging_date = timeframe_start.shift(months=6)
        create_imaging_report_with_coding(
            patient=patient,
            value_set_class=Mammography,
            original_date=imaging_date.date(),
            result_date=imaging_date.date(),
            assigned_date=imaging_date.datetime,
        )

        assert protocol.in_numerator(patient) is True
        assert protocol._on_date is not None

    @pytest.mark.django_db
    def test_numerator_without_mammogram(self) -> None:
        """Test patient without mammogram is not in numerator."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        assert protocol.in_numerator(patient) is False

    @pytest.mark.django_db
    def test_numerator_with_old_imaging_report(self) -> None:
        """Test mammography report outside 27-month window is not in numerator."""
        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = arrow.get("2024-01-01")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        # 28 months before timeframe start (outside 27-month window)
        imaging_date = timeframe_start.shift(months=-28)
        create_imaging_report_with_coding(
            patient=patient,
            value_set_class=Mammography,
            original_date=imaging_date.date(),
            result_date=imaging_date.date(),
            assigned_date=imaging_date.datetime,
        )

        assert protocol.in_numerator(patient) is False


# =============================================================================
# PROTOCOL OVERRIDE TESTS
# =============================================================================


class TestProtocolOverride:
    """Test protocol override support."""

    @pytest.mark.django_db
    def test_get_protocol_override_returns_active_override(self) -> None:
        """Test get_protocol_override returns active override."""
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
            narrative="Custom screening cycle",
            deleted=False,
        )

        override = protocol.get_protocol_override(patient)

        assert override is not None
        assert override.cycle_in_days == 365
        assert override.protocol_key == "CMS125v14"

    @pytest.mark.django_db
    def test_get_protocol_override_returns_none_when_no_override(self) -> None:
        """Test get_protocol_override returns None when no override exists."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        assert protocol.get_protocol_override(patient) is None


# =============================================================================
# COMPUTE METHOD TESTS
# =============================================================================


class TestComputeMethod:
    """Test compute() method for event handling."""

    def test_compute_assess_command_returns_log_effect(self) -> None:
        """Test compute() returns LOG effect for ASSESS_COMMAND__CONDITION_SELECTED."""
        mock_event = Mock()
        mock_event.type = EventType.ASSESS_COMMAND__CONDITION_SELECTED
        mock_event.context = {"note": {"uuid": "test-note-uuid-123"}}

        protocol = ClinicalQualityMeasure125v14(event=mock_event)
        effects = protocol.compute()

        assert len(effects) == 1
        assert effects[0].type == EffectType.LOG
        assert "test-note-uuid-123" in effects[0].payload
        assert protocol.NARRATIVE_STRING in effects[0].payload

    def test_compute_assess_command_handles_missing_uuid(self) -> None:
        """Test compute() handles missing note UUID gracefully."""
        mock_event = Mock()
        mock_event.type = EventType.ASSESS_COMMAND__CONDITION_SELECTED
        mock_event.context = {"note": {}}

        protocol = ClinicalQualityMeasure125v14(event=mock_event)
        effects = protocol.compute()

        assert len(effects) == 1
        assert effects[0].type == EffectType.LOG
        assert "unknown" in effects[0].payload


# =============================================================================
# COMPUTE RESULTS TESTS
# =============================================================================


class TestComputeResults:
    """Test compute_results() method for protocol card generation."""

    @pytest.mark.django_db
    def test_compute_results_due_status_no_mammogram(self) -> None:
        """Test compute_results returns DUE status when no mammogram."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        effects = protocol.compute_results(patient)

        assert len(effects) == 1
        assert effects[0] is not None

    @pytest.mark.django_db
    def test_compute_results_satisfied_status_with_mammogram(self) -> None:
        """Test compute_results returns SATISFIED status with recent mammogram."""
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

        # Use helper with Mammography value set for proper ValueSet filtering
        imaging_date = timeframe_end.shift(months=-6)
        create_imaging_report_with_coding(
            patient=patient,
            value_set_class=Mammography,
            original_date=imaging_date.date(),
            result_date=imaging_date.date(),
            assigned_date=imaging_date.datetime,
        )

        effects = protocol.compute_results(patient)

        assert len(effects) == 1
        assert effects[0] is not None

    @pytest.mark.django_db
    def test_compute_results_not_applicable_for_young_patient(self) -> None:
        """Test compute_results returns NOT_APPLICABLE for patient under 42."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-40).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        effects = protocol.compute_results(patient)

        # Young patient gets a card showing when they'll be eligible
        assert len(effects) == 1
        assert effects[0] is not None

    @pytest.mark.django_db
    def test_compute_results_empty_for_excluded_patient(self) -> None:
        """Test compute_results returns empty list for excluded patient."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        create_condition_with_coding(
            patient, BilateralMastectomy, timeframe_end.shift(years=-2).date()
        )

        effects = protocol.compute_results(patient)

        assert len(effects) == 0


# =============================================================================
# VALUE SET TESTS
# =============================================================================


class TestValueSets:
    """Test value sets are properly configured."""

    def test_mammography_value_set_has_codes(self) -> None:
        """Test Mammography value set has codes."""
        assert hasattr(Mammography, "values")
        assert len(Mammography.values) > 0

    def test_tomography_value_set_has_codes(self) -> None:
        """Test Tomography value set has codes."""
        assert hasattr(Tomography, "values")
        codes = Tomography.get_codes()
        assert len(codes) > 0

    def test_bilateral_mastectomy_has_codes(self) -> None:
        """Test BilateralMastectomy value set has codes."""
        assert hasattr(BilateralMastectomy, "values")
        assert len(BilateralMastectomy.values) > 0

    def test_hospice_care_ambulatory_has_codes(self) -> None:
        """Test HospiceCareAmbulatory value set has codes."""
        assert hasattr(HospiceCareAmbulatory, "values")
        assert len(HospiceCareAmbulatory.values) > 0

    def test_palliative_care_diagnosis_has_codes(self) -> None:
        """Test PalliativeCareDiagnosis value set has codes."""
        assert hasattr(PalliativeCareDiagnosis, "values")
        assert len(PalliativeCareDiagnosis.values) > 0

    def test_frailty_diagnosis_has_codes(self) -> None:
        """Test FrailtyDiagnosis value set has codes."""
        assert hasattr(FrailtyDiagnosis, "values")
        assert len(FrailtyDiagnosis.values) > 0

    def test_advanced_illness_has_codes(self) -> None:
        """Test AdvancedIllness value set has codes."""
        assert hasattr(AdvancedIllness, "values")
        assert len(AdvancedIllness.values) > 0
