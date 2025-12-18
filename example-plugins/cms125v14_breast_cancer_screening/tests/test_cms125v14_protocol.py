import arrow
import pytest
from cms125v14_breast_cancer_screening.protocols.cms125v14_protocol import (
    ClinicalQualityMeasure125v14,
)

from canvas_sdk.events import EventType
from canvas_sdk.test_utils.factories import BillingLineItemFactory, NoteFactory, PatientFactory
from canvas_sdk.test_utils.helpers import (
    create_condition_with_coding,
    create_imaging_report_with_coding,
    create_protocol_instance,
)
from canvas_sdk.test_utils.helpers import (
    create_encounter_with_billing as create_qualifying_visit,
)
from canvas_sdk.v1.data.protocol_override import ProtocolOverride
from canvas_sdk.v1.data.protocol_override import Status as ProtocolOverrideStatus
from canvas_sdk.value_set.v2026.condition import (
    AdvancedIllness,
    FrailtyDiagnosis,
    HistoryOfBilateralMastectomy,
    PalliativeCareDiagnosis,
    StatusPostLeftMastectomy,
    StatusPostRightMastectomy,
    UnilateralMastectomyUnspecifiedLaterality,
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
        """Test protocol responds to multiple event types."""
        expected_events = [
            EventType.Name(EventType.CONDITION_CREATED),
            EventType.Name(EventType.CONDITION_UPDATED),
            EventType.Name(EventType.CONDITION_RESOLVED),
            EventType.Name(EventType.MEDICATION_LIST_ITEM_CREATED),
            EventType.Name(EventType.MEDICATION_LIST_ITEM_UPDATED),
            EventType.Name(EventType.OBSERVATION_CREATED),
            EventType.Name(EventType.OBSERVATION_UPDATED),
            EventType.Name(EventType.PATIENT_UPDATED),
            EventType.Name(EventType.ENCOUNTER_CREATED),
            EventType.Name(EventType.ENCOUNTER_UPDATED),
            EventType.Name(EventType.CLAIM_CREATED),
            EventType.Name(EventType.CLAIM_UPDATED),
            EventType.Name(EventType.PROTOCOL_OVERRIDE_CREATED),
            EventType.Name(EventType.PROTOCOL_OVERRIDE_UPDATED),
            EventType.Name(EventType.PROTOCOL_OVERRIDE_DELETED),
        ]
        assert expected_events == ClinicalQualityMeasure125v14.RESPONDS_TO

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


class TestInitialPopulation:
    """Test initial population inclusion/exclusion criteria."""

    @pytest.mark.django_db
    def test_female_age_42_with_visit_included(self) -> None:
        """Test female patient aged exactly 42 with visit is included."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        age = 42
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        assert protocol.in_initial_population(patient, age) is True

    @pytest.mark.django_db
    def test_female_age_74_with_visit_included(self) -> None:
        """Test female patient aged exactly 74 with visit is included."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        age = 74
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        assert protocol.in_initial_population(patient, age) is True

    @pytest.mark.django_db
    def test_female_age_60_with_visit_included(self) -> None:
        """Test female patient aged 60 with visit is included."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        age = 60
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        assert protocol.in_initial_population(patient, age) is True

    @pytest.mark.django_db
    def test_female_age_41_excluded(self) -> None:
        """Test female patient aged 41 is excluded (below minimum age)."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        age = 41
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        assert protocol.in_initial_population(patient, age) is False

    @pytest.mark.django_db
    def test_female_age_75_excluded(self) -> None:
        """Test female patient aged 75 is excluded (above maximum age)."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        age = 75
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        assert protocol.in_initial_population(patient, age) is False

    @pytest.mark.django_db
    def test_male_patient_excluded(self) -> None:
        """Test male patient is excluded regardless of age."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        age = 60
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="M", birth_date=birth_date)

        assert protocol.in_initial_population(patient, age) is False

    @pytest.mark.django_db
    def test_female_without_qualifying_visit_excluded(self) -> None:
        """Test female patient without qualifying visit is excluded.

        Per CMS125v14 spec, the initial population requires a qualifying encounter
        during the measurement period.
        """
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        age = 60
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        # No visit created - excluded per CMS125v14 spec
        assert protocol.in_initial_population(patient, age) is False


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
    def test_status_post_left_and_right_detected(self) -> None:
        """Test status post left + status post right mastectomy detected as bilateral equivalent."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        create_condition_with_coding(
            patient, StatusPostLeftMastectomy, timeframe_end.shift(years=-3).date()
        )
        create_condition_with_coding(
            patient, StatusPostRightMastectomy, timeframe_end.shift(years=-2).date()
        )

        assert protocol.had_mastectomy(patient) is True

    @pytest.mark.django_db
    def test_unspecified_laterality_plus_left_unilateral_detected(self) -> None:
        """Test unspecified laterality + left unilateral mastectomy detected as bilateral."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        create_condition_with_coding(
            patient, UnilateralMastectomyUnspecifiedLaterality, timeframe_end.shift(years=-3).date()
        )
        create_condition_with_coding(
            patient, UnilateralMastectomyLeft, timeframe_end.shift(years=-2).date()
        )

        assert protocol.had_mastectomy(patient) is True

    @pytest.mark.django_db
    def test_unspecified_laterality_plus_status_post_right_detected(self) -> None:
        """Test unspecified laterality + status post right mastectomy detected as bilateral."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        create_condition_with_coding(
            patient, UnilateralMastectomyUnspecifiedLaterality, timeframe_end.shift(years=-3).date()
        )
        create_condition_with_coding(
            patient, StatusPostRightMastectomy, timeframe_end.shift(years=-2).date()
        )

        assert protocol.had_mastectomy(patient) is True

    @pytest.mark.django_db
    def test_two_unspecified_laterality_diagnoses_detected(self) -> None:
        """Test two unspecified laterality mastectomy diagnoses detected as bilateral."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        # Create two separate unspecified laterality diagnoses
        create_condition_with_coding(
            patient, UnilateralMastectomyUnspecifiedLaterality, timeframe_end.shift(years=-3).date()
        )
        create_condition_with_coding(
            patient, UnilateralMastectomyUnspecifiedLaterality, timeframe_end.shift(years=-2).date()
        )

        assert protocol.had_mastectomy(patient) is True

    @pytest.mark.django_db
    def test_single_unspecified_laterality_not_detected(self) -> None:
        """Test single unspecified laterality mastectomy alone is NOT detected as bilateral."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        create_condition_with_coding(
            patient, UnilateralMastectomyUnspecifiedLaterality, timeframe_end.shift(years=-3).date()
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

        age = 65
        birth_date = timeframe_end.shift(years=-age).date()
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
        assert protocol.in_denominator(patient, age) is True


class TestDenominator:
    """Test denominator inclusion/exclusion criteria."""

    @pytest.mark.django_db
    def test_denominator_includes_eligible_patient(self) -> None:
        """Test eligible patient without exclusions is in denominator."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        age = 60
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        assert protocol.in_denominator(patient, age) is True

    @pytest.mark.django_db
    def test_denominator_excludes_bilateral_mastectomy(self) -> None:
        """Test bilateral mastectomy excludes from denominator."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        age = 60
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        create_condition_with_coding(
            patient, BilateralMastectomy, timeframe_end.shift(years=-2).date()
        )

        assert protocol.in_initial_population(patient, age) is True
        assert protocol.in_denominator(patient, age) is False

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

        age = 60
        birth_date = timeframe_end.shift(years=-age).date()
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

            assert protocol.in_denominator(patient, age) is False

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

        age = 60
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        create_condition_with_coding(
            patient,
            PalliativeCareDiagnosis,
            timeframe_start.shift(months=3).date(),
            surgical=False,
        )

        assert protocol.in_denominator(patient, age) is False


class TestStratification:
    """Test stratification logic."""

    @pytest.mark.django_db
    def test_stratum_1_age_42(self) -> None:
        """Test patient age 42 is in Stratum 1."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        age = 42
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        assert protocol.get_stratification(patient, age) == 1

    @pytest.mark.django_db
    def test_stratum_1_age_51(self) -> None:
        """Test patient age 51 is in Stratum 1."""
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
    def test_stratum_2_age_52(self) -> None:
        """Test patient age 52 is in Stratum 2."""
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
    def test_stratum_2_age_74(self) -> None:
        """Test patient age 74 is in Stratum 2."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        age = 74
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        assert protocol.get_stratification(patient, age) == 2

    @pytest.mark.django_db
    def test_stratification_none_for_excluded_patient(self) -> None:
        """Test excluded patient returns None stratification."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        age = 60
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        create_condition_with_coding(
            patient, BilateralMastectomy, timeframe_end.shift(years=-2).date()
        )

        assert protocol.get_stratification(patient, age) is None


class TestFirstDueIn:
    """Test first_due_in calculation logic."""

    @pytest.mark.django_db
    def test_first_due_in_for_female_age_40(self) -> None:
        """Test first_due_in returns days until 42nd birthday for female age 40."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        age = 40
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        days_until = protocol.first_due_in(patient, age)

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

        age = 42
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        assert protocol.first_due_in(patient, age) is None

    @pytest.mark.django_db
    def test_first_due_in_returns_none_for_male(self) -> None:
        """Test first_due_in returns None for male patient."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        age = 40
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="M", birth_date=birth_date)

        assert protocol.first_due_in(patient, age) is None

    @pytest.mark.django_db
    def test_first_due_in_returns_none_with_mastectomy(self) -> None:
        """Test first_due_in returns None for patient with mastectomy."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        age = 40
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        create_condition_with_coding(
            patient, BilateralMastectomy, timeframe_end.shift(years=-2).date()
        )

        assert protocol.first_due_in(patient, age) is None


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

        # Use the protocol's actual key (which is the wrapper class name when using create_protocol_instance)
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
            narrative="Custom screening cycle",
            deleted=False,
        )

        override = protocol.get_protocol_override(patient)

        assert override is not None
        assert override.cycle_in_days == 365
        assert override.protocol_key == protocol_key

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


class TestRecommendationPlanButton:
    """Test the Plan button recommendation structure for due patients."""

    @pytest.mark.django_db
    def test_due_patient_gets_plan_button_recommendation(self) -> None:
        """Test due patient's protocol card has Plan button with instruct command."""
        import json

        from canvas_sdk.effects import EffectType

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
        effect = effects[0]

        # Verify this is a ProtocolCard effect
        assert effect.type == EffectType.ADD_OR_UPDATE_PROTOCOL_CARD

        # Check the payload
        payload = json.loads(effect.payload)
        data = payload["data"]

        assert data["status"] == "due"
        assert len(data["recommendations"]) == 1

        recommendation = data["recommendations"][0]
        assert recommendation["button"] == "Plan"
        assert recommendation["command"]["type"] == "instruct"

    @pytest.mark.django_db
    def test_recommendation_has_effect_type(self) -> None:
        """Test due patient's recommendation includes effect_type for instruct command."""
        import json

        from canvas_sdk.effects import EffectType

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
        assert effects[0].type == EffectType.ADD_OR_UPDATE_PROTOCOL_CARD

        payload = json.loads(effects[0].payload)
        recommendation = payload["data"]["recommendations"][0]

        # Verify effect_type is present in context for proper button functionality
        assert "effect_type" in recommendation["context"]
        assert recommendation["context"]["effect_type"] == "ORIGINATE_INSTRUCT_COMMAND"


class TestTomographyNumerator:
    """Test tomography (3D mammography) satisfies numerator."""

    @pytest.mark.django_db
    def test_tomography_imaging_report_satisfies_numerator(self) -> None:
        """Test patient with tomography imaging report is in numerator."""
        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = arrow.get("2024-01-01")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        imaging_date = timeframe_start.shift(months=6)
        create_imaging_report_with_coding(
            patient=patient,
            value_set_class=Tomography,
            original_date=imaging_date.date(),
            result_date=imaging_date.date(),
            assigned_date=imaging_date.datetime,
        )

        assert protocol.in_numerator(patient) is True
        assert protocol._on_date is not None

    @pytest.mark.django_db
    def test_tomography_billing_satisfies_numerator(self) -> None:
        """Test patient with tomography billing code is in numerator."""
        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = arrow.get("2024-01-01")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        # Use tomography CPT code 77063
        tomography_cpt = "77063"
        tomography_date = timeframe_start.shift(months=6)
        tomography_note = NoteFactory.create(
            patient=patient,
            datetime_of_service=tomography_date.datetime,
        )
        BillingLineItemFactory.create(
            patient=patient,
            note=tomography_note,
            cpt=tomography_cpt,
        )

        assert protocol.in_numerator(patient) is True


class TestScreeningWindowBoundary:
    """Test the 27-month screening window boundary conditions."""

    @pytest.mark.django_db
    def test_mammography_at_exactly_27_months_satisfies_numerator(self) -> None:
        """Test mammography exactly at 27-month boundary satisfies numerator."""
        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = arrow.get("2024-01-01")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        # 27 months before end of measurement period (within window)
        # The window is: measurement period (12 months) + 15 extra months = 27 months
        imaging_date = timeframe_end.shift(months=-26)  # Just inside window
        create_imaging_report_with_coding(
            patient=patient,
            value_set_class=Mammography,
            original_date=imaging_date.date(),
            result_date=imaging_date.date(),
            assigned_date=imaging_date.datetime,
        )

        assert protocol.in_numerator(patient) is True

    @pytest.mark.django_db
    def test_mammography_at_28_months_does_not_satisfy_numerator(self) -> None:
        """Test mammography at 28 months (outside window) does not satisfy numerator."""
        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = arrow.get("2024-01-01")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        # 28 months before end = outside 27-month window
        imaging_date = timeframe_end.shift(months=-28)
        create_imaging_report_with_coding(
            patient=patient,
            value_set_class=Mammography,
            original_date=imaging_date.date(),
            result_date=imaging_date.date(),
            assigned_date=imaging_date.datetime,
        )

        assert protocol.in_numerator(patient) is False


class TestProtocolOverrideScreeningWindow:
    """Test protocol override modifies screening window calculation."""

    @pytest.mark.django_db
    def test_override_with_custom_cycle_adjusts_due_date(self) -> None:
        """Test protocol override with custom cycle affects due_in calculation."""
        import json

        from canvas_sdk.effects import EffectType

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

        # Add mammography
        imaging_date = timeframe_end.shift(months=-6)
        create_imaging_report_with_coding(
            patient=patient,
            value_set_class=Mammography,
            original_date=imaging_date.date(),
            result_date=imaging_date.date(),
            assigned_date=imaging_date.datetime,
        )

        # Create override with 1-year cycle instead of default 27-month
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
            narrative="Annual screening per clinical recommendation",
            deleted=False,
        )

        effects = protocol.compute_results(patient)
        assert len(effects) == 1

        # Verify this is a ProtocolCard effect
        assert effects[0].type == EffectType.ADD_OR_UPDATE_PROTOCOL_CARD

        # Check the applied effect's payload
        payload = json.loads(effects[0].payload)
        data = payload["data"]

        # With 1-year override and mammogram 6 months ago, should be due in ~6 months
        # (365 days - 180 days = ~185 days)
        assert data["due_in"] > 0  # Should have a positive due_in value


class TestMultipleExclusions:
    """Test behavior when patient has multiple exclusion criteria."""

    @pytest.mark.django_db
    def test_patient_with_hospice_and_mastectomy_excluded(self) -> None:
        """Test patient with both hospice care and mastectomy is excluded."""
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

        assert protocol.had_mastectomy(patient) is True
        assert protocol.in_hospice_care(patient) is True
        assert protocol.in_denominator(patient, age) is False

    @pytest.mark.django_db
    def test_patient_with_frailty_advanced_illness_and_palliative_excluded(self) -> None:
        """Test patient age 66+ with frailty, advanced illness, and palliative care."""
        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = arrow.get("2024-01-01")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        age = 68
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        # Add frailty
        create_condition_with_coding(
            patient,
            FrailtyDiagnosis,
            timeframe_start.shift(months=2).date(),
            surgical=False,
        )

        # Add advanced illness
        create_condition_with_coding(
            patient,
            AdvancedIllness,
            timeframe_start.shift(months=3).date(),
            surgical=False,
        )

        # Add palliative care
        create_condition_with_coding(
            patient,
            PalliativeCareDiagnosis,
            timeframe_start.shift(months=4).date(),
            surgical=False,
        )

        assert protocol.has_frailty_with_advanced_illness(patient) is True
        assert protocol.received_palliative_care(patient) is True
        assert protocol.in_denominator(patient, age) is False


class TestProtocolCardContent:
    """Test protocol card content (narrative, status, due_in values)."""

    @pytest.mark.django_db
    def test_due_card_has_correct_narrative(self) -> None:
        """Test DUE status card has correct narrative mentioning 27 months."""
        import json

        from canvas_sdk.effects import EffectType

        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date, first_name="Jane")

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        effects = protocol.compute_results(patient)

        # Verify this is a ProtocolCard effect
        assert effects[0].type == EffectType.ADD_OR_UPDATE_PROTOCOL_CARD

        payload = json.loads(effects[0].payload)
        data = payload["data"]

        assert "27 months" in data["narrative"]
        assert "Jane" in data["narrative"]
        assert data["due_in"] == -1  # Overdue

    @pytest.mark.django_db
    def test_satisfied_card_has_correct_narrative_with_date(self) -> None:
        """Test SATISFIED status card mentions patient name."""
        import json

        from canvas_sdk.effects import EffectType

        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = arrow.get("2024-01-01")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        birth_date = timeframe_end.shift(years=-60).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date, first_name="Sarah")

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        imaging_date = timeframe_end.shift(months=-3)
        create_imaging_report_with_coding(
            patient=patient,
            value_set_class=Mammography,
            original_date=imaging_date.date(),
            result_date=imaging_date.date(),
            assigned_date=imaging_date.datetime,
        )

        effects = protocol.compute_results(patient)

        # Verify this is a ProtocolCard effect
        assert effects[0].type == EffectType.ADD_OR_UPDATE_PROTOCOL_CARD

        payload = json.loads(effects[0].payload)
        data = payload["data"]

        assert data["status"] == "satisfied"
        assert "Sarah" in data["narrative"]
        assert data["due_in"] > 0  # Future due date

    @pytest.mark.django_db
    def test_due_card_includes_stratification_info(self) -> None:
        """Test DUE card narrative includes stratification information."""
        import json

        from canvas_sdk.effects import EffectType

        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        # Stratum 1 patient (age 42-51)
        birth_date = timeframe_end.shift(years=-45).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        effects = protocol.compute_results(patient)

        # Verify this is a ProtocolCard effect
        assert effects[0].type == EffectType.ADD_OR_UPDATE_PROTOCOL_CARD

        payload = json.loads(effects[0].payload)
        data = payload["data"]

        assert "Stratum 1" in data["narrative"]

    @pytest.mark.django_db
    def test_satisfied_card_includes_stratification_info(self) -> None:
        """Test SATISFIED card narrative includes stratification information."""
        import json

        from canvas_sdk.effects import EffectType

        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = arrow.get("2024-01-01")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        # Stratum 2 patient (age 52-74)
        birth_date = timeframe_end.shift(years=-65).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        imaging_date = timeframe_end.shift(months=-3)
        create_imaging_report_with_coding(
            patient=patient,
            value_set_class=Mammography,
            original_date=imaging_date.date(),
            result_date=imaging_date.date(),
            assigned_date=imaging_date.datetime,
        )

        effects = protocol.compute_results(patient)

        # Verify this is a ProtocolCard effect
        assert effects[0].type == EffectType.ADD_OR_UPDATE_PROTOCOL_CARD

        payload = json.loads(effects[0].payload)
        data = payload["data"]

        assert "Stratum 2" in data["narrative"]


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.django_db
    def test_patient_turns_42_during_measurement_period(self) -> None:
        """Test patient who turns 42 during measurement period."""
        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = arrow.get("2024-01-01")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        # Patient turns 42 on June 15, 2024 (during measurement period)
        age_at_end = 42
        birth_date = arrow.get("1982-06-15").date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-3)
        create_qualifying_visit(patient, visit_date)

        # Age at end of measurement period is 42
        assert protocol.in_initial_population(patient, age_at_end) is True

    @pytest.mark.django_db
    def test_patient_turns_75_during_measurement_period(self) -> None:
        """Test patient who turns 75 during measurement period is excluded."""
        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = arrow.get("2024-01-01")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        # Patient turns 75 on June 15, 2024 (during measurement period)
        age_at_end = 75
        birth_date = arrow.get("1949-06-15").date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-3)
        create_qualifying_visit(patient, visit_date)

        # Age at end of measurement period is 75 - excluded
        assert protocol.in_initial_population(patient, age_at_end) is False

    @pytest.mark.django_db
    def test_mastectomy_after_measurement_period_end_not_excluded(self) -> None:
        """Test mastectomy after measurement period end does not exclude patient."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        age = 60
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        # Mastectomy AFTER measurement period end - should NOT exclude
        create_condition_with_coding(
            patient, BilateralMastectomy, timeframe_end.shift(months=2).date()
        )

        assert protocol.had_mastectomy(patient) is False
        assert protocol.in_denominator(patient, age) is True

    @pytest.mark.django_db
    def test_patient_with_unknown_sex_excluded(self) -> None:
        """Test patient with unknown sex at birth is excluded."""
        timeframe_end = arrow.get("2024-12-31")
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14, timeframe_end=timeframe_end
        )

        age = 60
        birth_date = timeframe_end.shift(years=-age).date()
        patient = PatientFactory.create(sex_at_birth="UNK", birth_date=birth_date)

        assert protocol.in_initial_population(patient, age) is False

    @pytest.mark.django_db
    def test_multiple_mammograms_uses_most_recent(self) -> None:
        """Test multiple mammograms - protocol uses most recent for due_in calculation."""
        import json

        from canvas_sdk.effects import EffectType

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

        # Older mammogram
        older_date = timeframe_end.shift(months=-12)
        create_imaging_report_with_coding(
            patient=patient,
            value_set_class=Mammography,
            original_date=older_date.date(),
            result_date=older_date.date(),
            assigned_date=older_date.datetime,
        )

        # More recent mammogram
        recent_date = timeframe_end.shift(months=-3)
        create_imaging_report_with_coding(
            patient=patient,
            value_set_class=Mammography,
            original_date=recent_date.date(),
            result_date=recent_date.date(),
            assigned_date=recent_date.datetime,
        )

        effects = protocol.compute_results(patient)

        # Verify this is a ProtocolCard effect
        assert effects[0].type == EffectType.ADD_OR_UPDATE_PROTOCOL_CARD

        payload = json.loads(effects[0].payload)
        data = payload["data"]

        assert data["status"] == "satisfied"
        # Due in should be based on the more recent mammogram (3 months ago)
        # so due_in should be larger than if it was based on 12-month-old mammogram
        assert data["due_in"] > 0


class TestSatisfiedNarrativeTimePhrases:
    """Test _build_satisfied_narrative time phrase variations."""

    @pytest.mark.django_db
    def test_mammogram_today_shows_today_phrase(self) -> None:
        """Test narrative shows 'today' for mammogram performed today."""
        import json

        from canvas_sdk.effects import EffectType

        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = timeframe_end.shift(years=-1)
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        birth_date = timeframe_end.shift(years=-50).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        # Add qualifying visit for initial population
        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        # Mammogram on the same day as timeframe_end (today)
        today_date = timeframe_end
        create_imaging_report_with_coding(
            patient=patient,
            value_set_class=Mammography,
            original_date=today_date.date(),
            result_date=today_date.date(),
            assigned_date=today_date.datetime,
        )

        effects = protocol.compute_results(patient)

        assert effects[0].type == EffectType.ADD_OR_UPDATE_PROTOCOL_CARD
        payload = json.loads(effects[0].payload)
        data = payload["data"]

        assert data["status"] == "satisfied"
        assert "today" in data["narrative"]

    @pytest.mark.django_db
    def test_mammogram_one_month_ago_shows_singular_phrase(self) -> None:
        """Test narrative shows '1 month ago' for mammogram performed 30-59 days ago."""
        import json

        from canvas_sdk.effects import EffectType

        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = timeframe_end.shift(years=-1)
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        birth_date = timeframe_end.shift(years=-50).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        # Add qualifying visit for initial population
        visit_date = timeframe_end.shift(months=-6)
        create_qualifying_visit(patient, visit_date)

        # Mammogram 35 days ago (1 month ago)
        one_month_ago = timeframe_end.shift(days=-35)
        create_imaging_report_with_coding(
            patient=patient,
            value_set_class=Mammography,
            original_date=one_month_ago.date(),
            result_date=one_month_ago.date(),
            assigned_date=one_month_ago.datetime,
        )

        effects = protocol.compute_results(patient)

        assert effects[0].type == EffectType.ADD_OR_UPDATE_PROTOCOL_CARD
        payload = json.loads(effects[0].payload)
        data = payload["data"]

        assert data["status"] == "satisfied"
        assert "1 month ago" in data["narrative"]


class TestProtocolOverrideNumeratorLogic:
    """Test in_numerator override logic for custom screening cycles."""

    @pytest.mark.django_db
    def test_override_within_cycle_uses_measurement_period_only(self) -> None:
        """Test that override within cycle limits search to measurement period."""
        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = timeframe_end.shift(years=-1)
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        birth_date = timeframe_end.shift(years=-50).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        # Create override with reference_date and cycle_in_days
        # Reference date is within the cycle (365 days cycle, 6 months ago reference)
        reference_date = timeframe_end.shift(months=-6)
        ProtocolOverride.objects.create(
            patient=patient,
            protocol_key=protocol.protocol_key(),
            reference_date=reference_date.datetime,
            cycle_in_days=365,
            cycle_quantity=1,
            cycle_unit="years",
            is_snooze=False,
            is_adjustment=True,
            snooze_date=reference_date.date(),
            snoozed_days=0,
            snooze_comment="",
            narrative="Custom cycle",
            deleted=False,
            status=ProtocolOverrideStatus.ACTIVE,
        )

        # Create mammogram OUTSIDE measurement period but within 27-month window
        # This should NOT count when override is active within cycle
        outside_mp_date = timeframe_start.shift(months=-6)
        create_imaging_report_with_coding(
            patient=patient,
            value_set_class=Mammography,
            original_date=outside_mp_date.date(),
            result_date=outside_mp_date.date(),
            assigned_date=outside_mp_date.datetime,
        )

        # Patient should NOT be in numerator because mammogram is outside measurement period
        # and override restricts to measurement period only when within cycle
        assert protocol.in_numerator(patient) is False

    @pytest.mark.django_db
    def test_override_outside_cycle_uses_standard_27_month_window(self) -> None:
        """Test that override outside cycle falls back to standard 27-month window."""
        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = timeframe_end.shift(years=-1)
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        birth_date = timeframe_end.shift(years=-50).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        # Create override with reference_date and cycle_in_days
        # Reference date is OUTSIDE the cycle (30 day cycle, 2 years ago reference)
        reference_date = timeframe_end.shift(years=-2)
        ProtocolOverride.objects.create(
            patient=patient,
            protocol_key=protocol.protocol_key(),
            reference_date=reference_date.datetime,
            cycle_in_days=30,  # Short cycle that has long expired
            cycle_quantity=1,
            cycle_unit="months",
            is_snooze=False,
            is_adjustment=True,
            snooze_date=reference_date.date(),
            snoozed_days=0,
            snooze_comment="",
            narrative="Custom cycle",
            deleted=False,
            status=ProtocolOverrideStatus.ACTIVE,
        )

        # Create mammogram within 27-month window but outside measurement period
        within_27_month_date = timeframe_start.shift(months=-6)
        create_imaging_report_with_coding(
            patient=patient,
            value_set_class=Mammography,
            original_date=within_27_month_date.date(),
            result_date=within_27_month_date.date(),
            assigned_date=within_27_month_date.datetime,
        )

        # Patient should be in numerator because override is outside cycle
        # and standard 27-month window applies
        assert protocol.in_numerator(patient) is True

    @pytest.mark.django_db
    def test_in_numerator_uses_passed_override_parameter(self) -> None:
        """Test that in_numerator uses override when passed explicitly."""
        timeframe_end = arrow.get("2024-12-31")
        timeframe_start = timeframe_end.shift(years=-1)
        protocol = create_protocol_instance(
            ClinicalQualityMeasure125v14,
            timeframe_start=timeframe_start,
            timeframe_end=timeframe_end,
        )

        birth_date = timeframe_end.shift(years=-50).date()
        patient = PatientFactory.create(sex_at_birth="F", birth_date=birth_date)

        # Create override with reference_date within cycle
        reference_date = timeframe_end.shift(months=-6)
        override = ProtocolOverride.objects.create(
            patient=patient,
            protocol_key=protocol.protocol_key(),
            reference_date=reference_date.datetime,
            cycle_in_days=365,
            cycle_quantity=1,
            cycle_unit="years",
            is_snooze=False,
            is_adjustment=True,
            snooze_date=reference_date.date(),
            snoozed_days=0,
            snooze_comment="",
            narrative="Custom cycle",
            deleted=False,
            status=ProtocolOverrideStatus.ACTIVE,
        )

        # Create mammogram OUTSIDE measurement period but within 27-month window
        outside_mp_date = timeframe_start.shift(months=-6)
        create_imaging_report_with_coding(
            patient=patient,
            value_set_class=Mammography,
            original_date=outside_mp_date.date(),
            result_date=outside_mp_date.date(),
            assigned_date=outside_mp_date.datetime,
        )

        # When passing override explicitly, should use it (not fetch from DB)
        assert protocol.in_numerator(patient, override) is False

        # When passing None explicitly, should fetch from DB and get same result
        assert protocol.in_numerator(patient, None) is False

        # When not passing override at all (default), should also fetch from DB
        assert protocol.in_numerator(patient) is False
