import arrow
from django.db.models import Q

from canvas_sdk.commands import InstructCommand
from canvas_sdk.commands.constants import CodeSystems, Coding
from canvas_sdk.effects import Effect
from canvas_sdk.effects.protocol_card import ProtocolCard, Recommendation
from canvas_sdk.events import EventType
from canvas_sdk.protocols import ClinicalQualityMeasure
from canvas_sdk.protocols.timeframe import Timeframe
from canvas_sdk.v1.data.billing import BillingLineItem
from canvas_sdk.v1.data.condition import Condition
from canvas_sdk.v1.data.coverage import Coverage, TransactorCoverageType
from canvas_sdk.v1.data.encounter import Encounter
from canvas_sdk.v1.data.imaging import ImagingReport
from canvas_sdk.v1.data.medication import Medication
from canvas_sdk.v1.data.observation import Observation
from canvas_sdk.v1.data.patient import Patient
from canvas_sdk.v1.data.protocol_override import ProtocolOverride
from canvas_sdk.value_set.v2026.condition import (
    AdvancedIllness,
    FrailtyDiagnosis,
    HistoryOfBilateralMastectomy,
    HospiceDiagnosis,
    PalliativeCareDiagnosis,
    StatusPostLeftMastectomy,
    StatusPostRightMastectomy,
    UnilateralMastectomyUnspecifiedLaterality,
)
from canvas_sdk.value_set.v2026.diagnostic_study import Mammography
from canvas_sdk.value_set.v2026.encounter import (
    AnnualWellnessVisit,
    FrailtyEncounter,
    HomeHealthcareServices,
    HospiceEncounter,
    OfficeVisit,
    PalliativeCareEncounter,
    PreventiveCareServicesEstablishedOfficeVisit18AndUp,
    PreventiveCareServicesInitialOfficeVisit18AndUp,
    TelephoneVisits,
    VirtualEncounter,
)
from canvas_sdk.value_set.v2026.intervention import (
    HospiceCareAmbulatory,
    PalliativeCareIntervention,
)
from canvas_sdk.value_set.v2026.medication import DementiaMedications
from canvas_sdk.value_set.v2026.procedure import (
    BilateralMastectomy,
    UnilateralMastectomyLeft,
    UnilateralMastectomyRight,
)
from canvas_sdk.value_set.v2026.symptom import FrailtySymptom
from canvas_sdk.value_set.v2026.tomography import Tomography
from canvas_sdk.value_set.value_set import ValueSetType
from logger import log


class ClinicalQualityMeasure125v14(ClinicalQualityMeasure):
    """
    Breast Cancer Screening.

    Description: Percentage of women 42-74 years of age who had a mammogram to screen
    for breast cancer in the 27 months prior to the end of the Measurement Period

    Definition: None

    Rationale: Breast cancer is one of the most common types of cancers, accounting for 15 percent
    of all new cancer diagnoses in the U.S. (Noone et al., 2018). In 2015, over 3 million women
    were estimated to be living with breast cancer in the U.S. and it is estimated that 12 percent
    of women will be diagnosed with breast cancer at some point during their lifetime (Noone et al., 2018).

    While there are other factors that affect a woman's risk of developing breast cancer,
    advancing age is a primary risk factor. Breast cancer is most frequently diagnosed among
    women ages 55-64; the median age at diagnosis is 62 years (Noone et al., 2018).

    The chance of a woman being diagnosed with breast cancer in a given year increases with age.
    By age 40, the chances are 1 in 68; by age 50 it becomes 1 in 43; by age 60, it is 1 in 29 (American Cancer Society, 2017).

    Guidance: This measure evaluates primary screening. Do not count biopsies,
    breast ultrasounds, or MRIs because they are not appropriate methods for primary breast cancer screening.
    Please note the measure may include screenings performed outside the age range of patients
    referenced in the initial population. Screenings that occur prior to the measurement period are valid to meet measure criteria.

    This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.6. Please refer to the eCQI resource center (https://ecqi.healthit.gov/qdm) for more information on the QDM.
    More information: https://ecqi.healthit.gov/sites/default/files/ecqm/measures/CMS125-v14.0.000-QDM.html
    """

    _patient_id: str | None  # needed for type inference in patient_id_from_target override

    class Meta:
        """Meta class for CMS125v14."""

        title = "Breast Cancer Screening"
        version = "v14.0.0"
        description = (
            "Women 42-74 years of age who have not had a mammogram to screen for "
            "breast cancer within the last 27 months."
        )
        information = (
            "https://ecqi.healthit.gov/sites/default/files/ecqm/measures/CMS125-v14.0.000-QDM.html"
        )
        identifiers = ["CMS125v14"]
        types = ["CQM"]
        authors = ["National Committee for Quality Assurance"]
        references = [
            "American Cancer Society. (2017). Breast Cancer Facts & Figures 2017-2018. Retrieved February 8, 2019, from https://www.cancer.org/content/dam/cancer-org/research/cancer-facts-and-statistics/breast-cancer-facts-and-figures/breast-cancer-facts-and-figures-2017-2018.pdf",
            "American College of Radiology (ACR). (2017). ACR Appropriateness Criteria: Breast Cancer Screening. Retrieved from https://acsearch.acr.org/docs/70910/Narrative/",
            "National Comprehensive Cancer Network (NCCN). (2021). Breast Cancer Screening and Diagnosis. Retrieved from https://www.nccn.org/professionals/physician_gls/pdf/breast-screening.pdf",
            "Noone, A.M., Howlader, N., Krapcho, M., Miller, D., Brest, A., Yu, M., Ruhl, J., Tatalovich, Z., Mariotto, A., Lewis, D.R., Chen, H.S., Feuer, E.J., Cronin, K.A. (eds). (2018). SEER Cancer Statistics Review, 1975-2015. National Cancer Institute. Bethesda, MD. Retrieved February 8, 2019, from https://seer.cancer.gov/csr/1975_2015/",
            "U.S. Preventive Services Task Force (2024). Screening for Breast Cancer: U.S. Preventive Services Task Force Recommendation Statement. JAMA, 2024;331(22):1918-1930. doi:10.1001/jama.2024.5534.",
        ]

    RESPONDS_TO = [
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
    NARRATIVE_STRING = "Breast Cancer Screening CMS125v14"

    _on_date: "arrow.Arrow | None" = None
    AGE_RANGE_START = 42
    AGE_RANGE_END = 74
    EXTRA_SCREENING_MONTHS = 15

    # Stratification age boundaries
    STRATUM_1_START = 42
    STRATUM_1_END = 51
    STRATUM_2_START = 52
    STRATUM_2_END = 74

    # Keywords for nursing home detection in coverage plan names
    NURSING_HOME_KEYWORDS = (
        "long term care",
        "long-term care",
        "nursing home",
        "nursing facility",
        "skilled nursing",
    )

    # SNOMED codes for observation-based exclusion checks (source-agnostic)
    HOSPICE_CARE_SNOMED_CODES = frozenset(
        {
            "428361000124107",  # Discharge to home for hospice care
            "428371000124100",  # Discharge to healthcare facility for hospice care
            "373066001",  # Yes (qualifier value) - response to Hospice care [MDS] assessment
        }
    )

    FRAILTY_DEVICE_SNOMED_CODES = frozenset(
        {
            "58938008",  # Wheelchair
            "266731002",  # Walking frame
            "87405001",  # Walking stick/cane
            "360008003",  # Commode
            "23366006",  # Motorized wheelchair
            "336608004",  # Oxygen cylinder
            "702172008",  # Home CPAP unit
            "66435007",  # Hospital bed
        }
    )

    PALLIATIVE_CARE_SNOMED_CODE = "305284002"  # Receiving palliative care

    NURSING_HOME_SNOMED_CODE = "160734000"  # Lives in nursing home (finding)

    MAMMOGRAPHY_PROCEDURE_SNOMED_CODE = "71651007"

    def _has_observation_with_value_codes(
        self, patient: Patient, snomed_codes: frozenset[str] | set[str]
    ) -> bool:
        """Check if patient has observations with value codings matching any of the given SNOMED codes.

        Queries observations for the patient and checks if any value coding
        matches the provided SNOMED codes. This is source-agnostic - it captures
        observations created from questionnaires, plugins, or any other source.

        Args:
            patient: The patient to check
            snomed_codes: Set of SNOMED codes to look for in observation value codings

        Returns:
            True if any observation value coding matches the provided codes
        """
        return Observation.objects.filter(
            patient=patient,
            value_codings__code__in=snomed_codes,
        ).exists()

    def _has_billing_with_codes(self, patient: Patient, *value_sets: ValueSetType) -> bool:
        """Check if patient has billing codes from any of the provided value sets.

        Args:
            patient: The patient to check
            *value_sets: Value set classes to check codes against

        Returns:
            True if any billing code matches any value set
        """
        billing = BillingLineItem.objects.filter(patient=patient).within(self.timeframe)
        all_codes = self._combine_value_set_codes(*value_sets)
        return bool(all_codes and billing.filter(cpt__in=all_codes).exists())

    @staticmethod
    def _combine_value_set_codes(*value_sets: ValueSetType) -> set[str]:
        """Combine codes from multiple value sets into a single set.

        Args:
            *value_sets: Value set classes with get_codes() method

        Returns:
            Combined set of all codes from all value sets
        """
        return set().union(*(vs.get_codes() for vs in value_sets))

    def patient_id_from_target(self) -> str:
        """Override to support OBSERVATION, ENCOUNTER, and CLAIM events."""
        if self._patient_id is not None:
            return self._patient_id

        events_with_patient_in_context = (
            EventType.OBSERVATION_CREATED,
            EventType.OBSERVATION_UPDATED,
            EventType.CLAIM_CREATED,
            EventType.CLAIM_UPDATED,
        )

        if self.event.type in events_with_patient_in_context:
            patient_ctx = self.event.context.get("patient", {})
            self._patient_id = patient_ctx.get("id")
            if not self._patient_id:
                raise ValueError(
                    f"Patient ID not found in event context for event type {self.event.type}"
                )
            return self._patient_id

        if self.event.type in (EventType.ENCOUNTER_CREATED, EventType.ENCOUNTER_UPDATED):
            self._patient_id = str(
                Encounter.objects.values_list("note__patient__id", flat=True).get(
                    id=self.event.target.id
                )
            )
            return self._patient_id

        return super().patient_id_from_target()

    def compute(self) -> list[Effect]:
        """Compute the protocol result and return effects."""
        try:
            patient_id = self.patient_id_from_target()
        except Exception as e:
            log.error(f"CMS125v14: Failed to get patient_id from target: {e}")
            return []

        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            log.error(f"CMS125v14: Patient not found with id: {patient_id}")
            return []

        return self.compute_results(patient)

    def had_mastectomy(self, patient: Patient) -> bool:
        """Check if patient had a bilateral mastectomy or equivalent.

        Checks for:
        1. Bilateral mastectomy (procedure or history diagnosis)
        2. Two unilateral mastectomies (left + right procedures)
        3. Unilateral mastectomy procedure + status post diagnosis on the other side
        4. Two unilateral mastectomy diagnoses with unspecified laterality
           (Note: CQL checks anatomicalLocationSite for left/right, but Canvas
           Condition model doesn't have this field, so we check for two separate
           unspecified laterality diagnoses as a proxy for bilateral)
        5. Status post left + status post right mastectomy diagnoses
        """
        conditions = Condition.objects.filter(
            patient=patient,
            onset_date__lte=self.timeframe.end.date(),
        )

        bilateral = conditions.find(BilateralMastectomy)
        if not bilateral.exists():
            bilateral = conditions.find(HistoryOfBilateralMastectomy)

        if bilateral.exists():
            return True

        left_unilateral = conditions.find(UnilateralMastectomyLeft)
        right_unilateral = conditions.find(UnilateralMastectomyRight)

        if left_unilateral.exists() and right_unilateral.exists():
            return True

        if left_unilateral.exists():
            status_post_right = conditions.find(StatusPostRightMastectomy)
            if status_post_right.exists():
                return True

        if right_unilateral.exists():
            status_post_left = conditions.find(StatusPostLeftMastectomy)
            if status_post_left.exists():
                return True

        status_post_left = conditions.find(StatusPostLeftMastectomy)
        status_post_right = conditions.find(StatusPostRightMastectomy)
        if status_post_left.exists() and status_post_right.exists():
            return True

        unspecified = conditions.find(UnilateralMastectomyUnspecifiedLaterality)
        if unspecified.exists():
            if (
                left_unilateral.exists()
                or status_post_left.exists()
                or conditions.find(StatusPostLeftMastectomy).exists()
            ):
                return True
            if (
                right_unilateral.exists()
                or status_post_right.exists()
                or conditions.find(StatusPostRightMastectomy).exists()
            ):
                return True
            if unspecified.count() >= 2:
                return True

        return False

    def first_due_in(self, patient: Patient, age: int) -> int | None:
        """Calculate days until screening first due (when patient turns 42).

        Args:
            patient: The patient to check
            age: Patient's age at end of measurement period
        """
        if (
            patient.sex_at_birth == "F"
            and age < self.AGE_RANGE_START
            and not self.had_mastectomy(patient)
        ):
            birth_date_arrow = arrow.get(patient.birth_date)
            birthday_42 = birth_date_arrow.shift(years=self.AGE_RANGE_START)
            days_until = (birthday_42 - self.timeframe.end).days
            return days_until
        return None

    def has_qualifying_visit(self, patient: Patient) -> bool:
        """
        Check if patient had a qualifying visit during the measurement period.

        Per CMS125v14 spec, qualifying visits include:
        - Office Visit
        - Preventive Care Services (Established/Initial, 18+)
        - Annual Wellness Visit
        - Home Healthcare Services
        - Virtual Encounter
        - Telephone Visits
        """
        return self._has_billing_with_codes(
            patient,
            OfficeVisit,
            AnnualWellnessVisit,
            PreventiveCareServicesInitialOfficeVisit18AndUp,
            PreventiveCareServicesEstablishedOfficeVisit18AndUp,
            HomeHealthcareServices,
            VirtualEncounter,
            TelephoneVisits,
        )

    def in_initial_population(self, patient: Patient, age: int) -> bool:
        """
        Initial population: Women 42-74 years of age with a visit during the measurement period.

        Per CMS125v14 spec, the initial population requires a qualifying encounter.

        Args:
            patient: The patient to check
            age: Patient's age at end of measurement period
        """
        if not (self.AGE_RANGE_START <= age <= self.AGE_RANGE_END):
            return False

        if patient.sex_at_birth != "F":
            return False

        return self.has_qualifying_visit(patient)

    def in_hospice_care(self, patient: Patient) -> bool:
        """
        Check if patient was in hospice care during the measurement period.

        Checks:
        1. Billing line items with hospice codes (HospiceCareAmbulatory, HospiceEncounter)
        2. Conditions with HospiceDiagnosis codes
        3. Observations with SNOMED codes indicating hospice care (source-agnostic:
           captures data from questionnaires, plugins, or any other source)
        """
        if self._has_billing_with_codes(patient, HospiceCareAmbulatory, HospiceEncounter):
            return True

        hospice_conditions = (
            Condition.objects.filter(
                patient=patient,
                onset_date__lte=self.timeframe.end.date(),
            )
            .filter(
                Q(resolution_date__isnull=True)
                | Q(resolution_date__gte=self.timeframe.start.date())
            )
            .find(HospiceDiagnosis)
        )

        if hospice_conditions.exists():
            return True

        return self._has_observation_with_value_codes(patient, self.HOSPICE_CARE_SNOMED_CODES)

    def received_palliative_care(self, patient: Patient) -> bool:
        """
        Check if patient received palliative care during the measurement period.

        Per CMS125v14 CQL (PalliativeCareQDM library):
        - Palliative care diagnosis with prevalencePeriod overlapping measurement period
        - Palliative care encounter during measurement period
        - Palliative care intervention during measurement period
        - Observations with SNOMED codes indicating palliative care (source-agnostic)

        Note: Using conditions within timeframe (not "up to end") to match CQL's
        requirement that palliative care must be during the measurement period.
        """
        if (
            Condition.objects.filter(
                patient=patient,
                onset_date__lte=self.timeframe.end.date(),
            )
            .filter(
                Q(resolution_date__isnull=True)
                | Q(resolution_date__gte=self.timeframe.start.date())
            )
            .find(PalliativeCareDiagnosis)
            .exists()
        ):
            return True

        if self._has_billing_with_codes(
            patient, PalliativeCareEncounter, PalliativeCareIntervention
        ):
            return True

        return self._has_observation_with_value_codes(
            patient, frozenset({self.PALLIATIVE_CARE_SNOMED_CODE})
        )

    def has_frailty_indicator(self, patient: Patient) -> bool:
        """
        Check if patient has any frailty indicator during the measurement period.

        Frailty indicators include:
        1. Frailty diagnosis (conditions)
        2. Frailty symptom (conditions)
        3. Frailty encounter (billing)
        4. Frailty device (via observations with SNOMED codes, source-agnostic)

        Returns True if any frailty indicator is found.
        """
        frailty_conditions = Condition.objects.filter(
            patient=patient,
            onset_date__lte=self.timeframe.end.date(),
        ).filter(
            Q(resolution_date__isnull=True) | Q(resolution_date__gte=self.timeframe.start.date())
        )

        if frailty_conditions.find(FrailtyDiagnosis).exists():
            return True

        if frailty_conditions.find(FrailtySymptom).exists():
            return True

        if self._has_billing_with_codes(patient, FrailtyEncounter):
            return True

        return self._has_observation_with_value_codes(patient, self.FRAILTY_DEVICE_SNOMED_CODES)

    def has_advanced_illness_or_dementia_meds(self, patient: Patient) -> bool:
        """
        Check if patient has advanced illness diagnosis OR is taking dementia medications
        during the measurement period or the year prior.

        Returns True if either condition is met.
        """
        prior_year_start = self.timeframe.start.shift(years=-1)

        advanced_illness_conditions = Condition.objects.filter(
            patient=patient,
            onset_date__lte=self.timeframe.end.date(),
        ).filter(Q(resolution_date__isnull=True) | Q(resolution_date__gte=prior_year_start.date()))

        if advanced_illness_conditions.find(AdvancedIllness).exists():
            return True

        dementia_meds = Medication.objects.filter(
            patient=patient,
            start_date__lte=self.timeframe.end.datetime,
        ).filter(Q(end_date__isnull=True) | Q(end_date__gte=prior_year_start.datetime))

        return dementia_meds.find(DementiaMedications).exists()

    def has_frailty_with_advanced_illness(self, patient: Patient) -> bool:
        """
        Check if patient age ≥66 has frailty AND (advanced illness OR dementia medications).

        Per CMS125v14 flow:
        - Must have frailty indicator during measurement period
        - AND either:
        - Advanced illness diagnosis during MP or prior year, OR
        - Dementia medications during MP or prior year

        This exclusion only applies to patients age ≥66.
        """
        if not self.has_frailty_indicator(patient):
            return False

        return self.has_advanced_illness_or_dementia_meds(patient)

    def in_nursing_home(self, patient: Patient) -> bool:
        """
        Check if patient is living long-term in a nursing home any time on or before
        the end of the measurement period.

        This is typically determined by:
        1. Coverage/insurance type indicating long-term care facility
        2. Patient address indicating institutional care facility
        3. Observations with SNOMED codes indicating nursing home residence (source-agnostic)
        4. Frequent SNF/nursing facility encounters

        Note: Canvas may track this differently depending on implementation.
        This method checks Coverage records for long-term care payer types
        and observations for housing status.

        This exclusion only applies to patients age ≥66.
        """
        coverages = Coverage.objects.filter(
            patient=patient,
            coverage_start_date__lte=self.timeframe.end.date(),
        )

        for coverage in coverages:
            if coverage.coverage_type == TransactorCoverageType.LTC:
                return True

            if coverage.plan:
                plan_name_lower = str(coverage.plan).lower()
                if any(keyword in plan_name_lower for keyword in self.NURSING_HOME_KEYWORDS):
                    return True

        return self._has_observation_with_value_codes(
            patient, frozenset({self.NURSING_HOME_SNOMED_CODE})
        )

    def get_stratification(self, patient: Patient, age: int) -> int | None:
        """
        Determine which stratification group the patient belongs to.

        Per CMS125v14:
        - Stratum 1: Ages 42-51 at end of measurement period
        - Stratum 2: Ages 52-74 at end of measurement period

        Args:
            patient: The patient to check
            age: Patient's age at end of measurement period

        Returns:
            1 for Stratum 1 (ages 42-51)
            2 for Stratum 2 (ages 52-74)
            None if patient not in denominator or outside age ranges
        """
        if not self.in_denominator(patient, age):
            return None

        if self.STRATUM_1_START <= age <= self.STRATUM_1_END:
            return 1
        elif self.STRATUM_2_START <= age <= self.STRATUM_2_END:
            return 2
        else:
            return None

    def in_denominator(self, patient: Patient, age: int) -> bool:
        """
        Denominator: Equals Initial Population.

        Exclusions:
        1. Women who had a bilateral mastectomy or who have a history of a bilateral
           mastectomy or for whom there is evidence of a right and a left unilateral mastectomy.
        2. Patients who were in hospice care during the measurement year.
        3. Patients who received palliative care during the measurement period.
        4. Patients age ≥66 with frailty + advanced illness (see has_frailty_with_advanced_illness).
        5. Patients age ≥66 living long-term in nursing home (see in_nursing_home).

        Args:
            patient: The patient to check
            age: Patient's age at end of measurement period

        Exceptions: None
        """
        if not self.in_initial_population(patient, age):
            return False

        if self.in_hospice_care(patient):
            return False

        if self.received_palliative_care(patient):
            return False

        if self.had_mastectomy(patient):
            return False

        if age >= 66:
            if self.has_frailty_with_advanced_illness(patient):
                return False

            if self.in_nursing_home(patient):
                return False

        return True

    def get_protocol_override(self, patient: Patient) -> ProtocolOverride | None:
        """Get active protocol override (adjustment) for this patient and protocol."""
        return ProtocolOverride.objects.get_active_adjustment(patient, self.protocol_key())

    def in_numerator(self, patient: Patient, override: ProtocolOverride | None = None) -> bool:
        """
        Numerator: Women with one or more mammograms between October 1 of two years prior
        to the measurement period and the end of the measurement period (27-month window).

        Args:
            patient: The patient to check
            override: Protocol override, if already fetched. If None, will be fetched.

        Exclusions: Not Applicable
        """
        if override is None:
            override = self.get_protocol_override(patient)

        if override:
            reference_date = arrow.get(override.reference_date)
            cycle_days = override.cycle_in_days

            days_since_reference = (self.now - reference_date).days

            if days_since_reference <= cycle_days:
                period_start = self.timeframe.start
            else:
                period_start = self.timeframe.start.shift(months=-1 * self.EXTRA_SCREENING_MONTHS)
        else:
            period_start = self.timeframe.start.shift(months=-1 * self.EXTRA_SCREENING_MONTHS)

        period_end = self.timeframe.end

        extended_timeframe = Timeframe(start=period_start, end=period_end)

        mammography_billing = BillingLineItem.objects.filter(patient=patient).within(
            extended_timeframe
        )

        all_screening_codes = self._combine_value_set_codes(Mammography, Tomography)

        if all_screening_codes:
            mammography_billing = mammography_billing.filter(cpt__in=all_screening_codes).order_by(
                "-note__datetime_of_service"
            )

            if mammography_billing.exists():
                last_billing = mammography_billing.first()
                if (
                    last_billing is not None
                    and last_billing.note is not None
                    and last_billing.note.datetime_of_service
                ):
                    self._on_date = arrow.get(last_billing.note.datetime_of_service)
                    return True

        imaging_reports = (
            ImagingReport.objects.filter(patient=patient)
            .find(Mammography | Tomography)
            .filter(
                original_date__gte=period_start.date(),
                original_date__lte=period_end.date(),
            )
            .order_by("-original_date")
        )

        if imaging_reports.exists():
            last_report = imaging_reports.first()
            if last_report is not None and last_report.original_date is not None:
                self._on_date = arrow.get(last_report.original_date)
                return True

        return False

    def compute_results(self, patient: Patient) -> list[Effect]:
        """
        Compute the results for the protocol and return effects.

        Clinical recommendation: The U.S. Preventive Services Task Force (USPSTF) recommends
        biennial screening mammography for women aged 50-74 years (B recommendation).

        Args:
            patient: The patient to compute results for

        Returns:
            list[Effect]: Protocol cards to display in Canvas UI
        """
        protocol_key = self.protocol_key()

        age = int(patient.age_at(self.timeframe.end))

        if not self.in_denominator(patient, age):
            first_due = self.first_due_in(patient, age)
            if first_due and first_due > 0:
                narrative = (
                    f"{patient.first_name} will be eligible for breast cancer screening "
                    f"in {first_due} days."
                )
                card = ProtocolCard(
                    patient_id=patient.id,
                    key=protocol_key,
                    title="Breast Cancer Screening",
                    narrative=narrative,
                    status=ProtocolCard.Status.NOT_APPLICABLE,
                    due_in=first_due,
                    can_be_snoozed=True,
                )
                return [card.apply()]

            return []

        override = self.get_protocol_override(patient)

        stratum = self.get_stratification(patient, age)
        stratum_text = self._get_stratum_text(stratum)

        if self.in_numerator(patient, override) and self._on_date:
            due_in_days = self._calculate_due_in_days(override)
            narrative = self._build_satisfied_narrative(patient, due_in_days, stratum_text)

            card = ProtocolCard(
                patient_id=patient.id,
                key=protocol_key,
                title="Breast Cancer Screening",
                narrative=narrative,
                status=ProtocolCard.Status.SATISFIED,
                due_in=due_in_days,
                can_be_snoozed=True,
            )
            return [card.apply()]

        narrative = (
            f"No mammography found in the last 27 months. "
            f"{patient.first_name} is due for breast cancer screening.{stratum_text}"
        )

        recommendation = self._build_screening_recommendation()

        card = ProtocolCard(
            patient_id=patient.id,
            key=protocol_key,
            title="Breast Cancer Screening",
            narrative=narrative,
            status=ProtocolCard.Status.DUE,
            due_in=-1,  # Already overdue
            recommendations=[recommendation],
            can_be_snoozed=True,
        )
        return [card.apply()]

    def _get_stratum_text(self, stratum: int | None) -> str:
        """Get stratum text for narrative display."""
        if stratum == 1:
            return " (Stratum 1: Ages 42-51)"
        elif stratum == 2:
            return " (Stratum 2: Ages 52-74)"
        return ""

    def _calculate_due_in_days(self, override: ProtocolOverride | None) -> int:
        """Calculate days until next screening is due."""
        if self._on_date is None:
            return -1  # Fallback: indicate overdue if somehow called without a date
        if override:
            return (self._on_date.shift(days=override.cycle_in_days) - self.now).days

        return (
            self._on_date.shift(days=self.timeframe.duration, months=self.EXTRA_SCREENING_MONTHS)
            - self.now
        ).days

    def _build_satisfied_narrative(
        self, patient: Patient, due_in_days: int, stratum_text: str
    ) -> str:
        """Build narrative for satisfied protocol status."""
        if self._on_date is None:
            return f"{patient.first_name} is due for breast cancer screening.{stratum_text}"
        months_ago = (self.now - self._on_date).days // 30
        if months_ago == 0:
            time_phrase = "today"
        elif months_ago == 1:
            time_phrase = "1 month ago"
        else:
            time_phrase = f"{months_ago} months ago"

        return (
            f"{patient.first_name} had a mammography {time_phrase} on "
            f"{self._on_date.format('M/D/YY')}. "
            f"Next screening due in {due_in_days} days.{stratum_text}"
        )

    def _build_screening_recommendation(self) -> Recommendation:
        """Build the screening recommendation for mammography.

        Note: InstructCommand.coding only accepts SNOMED or UNSTRUCTURED code systems,
        but mammography codes are in LOINC/CPT. Therefore, we use a descriptive title
        and comment to guide clinicians rather than a coding filter.
        """
        instruct_command = InstructCommand(
            coding=Coding(system=CodeSystems.SNOMED, code=self.MAMMOGRAPHY_PROCEDURE_SNOMED_CODE),
            comment="Order screening mammography per CMS125v14 breast cancer screening measure",
        )
        return instruct_command.recommend(
            title="Discuss breast cancer screening and order mammography",
            button="Plan",
        )
