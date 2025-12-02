import arrow

from canvas_sdk.commands import InstructCommand
from canvas_sdk.effects import Effect
from canvas_sdk.effects.protocol_card import ProtocolCard, Recommendation
from canvas_sdk.events import EventType
from canvas_sdk.protocols import ClinicalQualityMeasure
from canvas_sdk.protocols.timeframe import Timeframe
from canvas_sdk.v1.data.billing import BillingLineItem
from canvas_sdk.v1.data.condition import Condition
from canvas_sdk.v1.data.encounter import Encounter
from canvas_sdk.v1.data.imaging import ImagingReport
from canvas_sdk.v1.data.medication import Medication
from canvas_sdk.v1.data.patient import Patient
from canvas_sdk.v1.data.protocol_override import ProtocolOverride
from canvas_sdk.value_set.v2026.condition import (
    AdvancedIllness,
    FrailtyDiagnosis,
    HistoryOfBilateralMastectomy,
    PalliativeCareDiagnosis,
    StatusPostLeftMastectomy,
    StatusPostRightMastectomy,
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
from logger import log


class ClinicalQualityMeasure125v14(ClinicalQualityMeasure):
    """
    Breast Cancer Screening.

    Description: Percentage of women 40-74 years of age who had a mammogram to screen
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

    def _get_billing_within_timeframe(self, patient: Patient):  # type: ignore[no-untyped-def]
        """Get billing line items within the measurement period."""
        return BillingLineItem.objects.filter(patient=patient).within(self.timeframe)

    def _has_billing_with_codes(self, patient: Patient, *value_sets) -> bool:  # type: ignore[no-untyped-def]
        """Check if patient has billing codes from any of the provided value sets.

        Args:
            patient: The patient to check
            *value_sets: Value set classes to check codes against

        Returns:
            True if any billing code matches any value set
        """
        billing = self._get_billing_within_timeframe(patient)
        all_codes = self._combine_value_set_codes(*value_sets)
        return bool(all_codes and billing.filter(cpt__in=all_codes).exists())

    def _get_conditions_up_to_end(self, patient: Patient):  # type: ignore[no-untyped-def]
        """Get conditions with onset_date up to end of timeframe."""
        return Condition.objects.filter(
            patient=patient,
            onset_date__lte=self.timeframe.end.date(),
        )

    def _get_conditions_within_timeframe(self, patient: Patient):  # type: ignore[no-untyped-def]
        """Get conditions with onset_date within the measurement period."""
        return Condition.objects.filter(
            patient=patient,
            onset_date__gte=self.timeframe.start.date(),
            onset_date__lte=self.timeframe.end.date(),
        )

    @staticmethod
    def _combine_value_set_codes(*value_sets) -> set[str]:  # type: ignore[no-untyped-def]
        """Combine codes from multiple value sets into a single set.

        Args:
            *value_sets: Value set classes with get_codes() method

        Returns:
            Combined set of all codes from all value sets
        """
        all_codes: set[str] = set()
        for vs in value_sets:
            all_codes.update(vs.get_codes())
        return all_codes

    @staticmethod
    def _build_coding_filter(*value_sets) -> list[dict[str, str | list[str]]]:  # type: ignore[no-untyped-def]
        """Build InstructCommand coding filter from value sets.

        Args:
            *value_sets: Value set classes with values dict

        Returns:
            List of coding filter dicts for InstructCommand
        """
        combined_codes: dict[str, set[str]] = {}
        for vs in value_sets:
            for system, codes in vs.values.items():
                if codes:
                    system_lower = system.lower()
                    if system_lower not in combined_codes:
                        combined_codes[system_lower] = set()
                    combined_codes[system_lower].update(codes)
        return [{"system": system, "code": list(codes)} for system, codes in combined_codes.items()]


    def patient_id_from_target(self) -> str:
        """
        Override to support additional event types beyond the base class.

        Adds support for: OBSERVATION, ENCOUNTER, CLAIM, and PROTOCOL_OVERRIDE events.
        """
        # Return cached value if already set
        if self._patient_id:
            return self._patient_id

        # Events that have patient_id in context - use directly (no DB query needed)
        events_with_patient_in_context = (
            EventType.OBSERVATION_CREATED,
            EventType.OBSERVATION_UPDATED,
            EventType.CLAIM_CREATED,
            EventType.CLAIM_UPDATED,
            EventType.PROTOCOL_OVERRIDE_CREATED,
            EventType.PROTOCOL_OVERRIDE_UPDATED,
            EventType.PROTOCOL_OVERRIDE_DELETED,
        )

        if self.event.type in events_with_patient_in_context:
            self._patient_id = self.event.context["patient"]["id"]
            return self._patient_id

        # Events that require DB query (context is empty for encounters)
        if self.event.type in (EventType.ENCOUNTER_CREATED, EventType.ENCOUNTER_UPDATED):
            # Encounter doesn't have a direct patient field - access via note relationship
            # Encounter -> note -> patient
            patient_id = (
                Encounter.objects.select_related("note__patient")
                .values_list("note__patient__id", flat=True)
                .get(id=self.event.target.id)
            )
            self._patient_id = str(patient_id)
            return self._patient_id

        # Fall back to base class implementation (which also sets self._patient_id)
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
        """Check if patient had a bilateral mastectomy or equivalent."""
        conditions = self._get_conditions_up_to_end(patient)

        # Check for bilateral mastectomy
        bilateral = conditions.find(BilateralMastectomy)
        if not bilateral.exists():
            bilateral = conditions.find(HistoryOfBilateralMastectomy)

        if bilateral.exists():
            return True

        # Check for two unilateral mastectomies (left + right)
        left_unilateral = conditions.find(UnilateralMastectomyLeft)
        right_unilateral = conditions.find(UnilateralMastectomyRight)

        if left_unilateral.exists() and right_unilateral.exists():
            return True

        # Check for unilateral mastectomy + status post on the other side
        if left_unilateral.exists():
            status_post_right = conditions.find(StatusPostRightMastectomy)
            if status_post_right.exists():
                return True

        if right_unilateral.exists():
            status_post_left = conditions.find(StatusPostLeftMastectomy)
            if status_post_left.exists():
                return True

        return False

    def first_due_in(self, patient: Patient) -> int | None:
        """Calculate days until screening first due (when patient turns 42)."""
        patient_age = patient.age_at(self.timeframe.end)

        if (
            patient.sex_at_birth == "F"
            and patient_age < self.AGE_RANGE_START
            and not self.had_mastectomy(patient)
        ):
            # Calculate patient's 42nd birthday
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
        """
        return self._has_billing_with_codes(
            patient,
            OfficeVisit,
            AnnualWellnessVisit,
            PreventiveCareServicesInitialOfficeVisit18AndUp,
            PreventiveCareServicesEstablishedOfficeVisit18AndUp,
            HomeHealthcareServices,
        )

    def in_initial_population(self, patient: Patient) -> bool:
        """
        Initial population: Women 42-74 years of age with a visit during the measurement period.

        Per CMS125v14 spec, the initial population requires a qualifying encounter.
        """
        patient_age = patient.age_at(self.timeframe.end)

        # Check age and sex
        if not (self.AGE_RANGE_START <= patient_age <= self.AGE_RANGE_END):
            return False

        if patient.sex_at_birth != "F":
            return False

        # Check for qualifying visit per CMS125v14 spec
        return self.has_qualifying_visit(patient)

    def in_hospice_care(self, patient: Patient) -> bool:
        """
        Check if patient was in hospice care during the measurement period.

        Checks both:
        1. Billing line items with hospice codes (HospiceCareAmbulatory)
        2. Encounters with hospice codes (HospiceEncounter)
        """
        return self._has_billing_with_codes(patient, HospiceCareAmbulatory, HospiceEncounter)

    def received_palliative_care(self, patient: Patient) -> bool:
        """
        Check if patient received palliative care during the measurement period.

        Checks:
        1. Diagnosis codes for palliative care
        2. Encounter codes for palliative care
        3. Intervention codes for palliative care
        """
        # Check conditions for palliative care diagnosis
        if self._get_conditions_up_to_end(patient).find(PalliativeCareDiagnosis).exists():
            return True

        # Check billing line items for palliative care
        return self._has_billing_with_codes(
            patient, PalliativeCareEncounter, PalliativeCareIntervention
        )

    def has_frailty_indicator(self, patient: Patient) -> bool:
        """
        Check if patient has any frailty indicator during the measurement period.

        Frailty indicators include:
        1. Frailty diagnosis (conditions)
        2. Frailty symptom (conditions)
        3. Frailty encounter (billing)
        4. Frailty device (would need device data - not typically available in Canvas)

        Returns True if any frailty indicator is found.
        """
        # Check for frailty diagnosis or symptom (must be within measurement period)
        frailty_conditions = self._get_conditions_within_timeframe(patient)

        if frailty_conditions.find(FrailtyDiagnosis).exists():
            return True

        if frailty_conditions.find(FrailtySymptom).exists():
            return True

        # Check for frailty encounter billing codes
        return self._has_billing_with_codes(patient, FrailtyEncounter)

    def has_advanced_illness_or_dementia_meds(self, patient: Patient) -> bool:
        """
        Check if patient has advanced illness diagnosis OR is taking dementia medications
        during the measurement period or the year prior.

        Returns True if either condition is met.
        """
        # Check for advanced illness diagnosis (MP or prior year)
        # Prior year = 1 year before measurement period start
        prior_year_start = self.timeframe.start.shift(years=-1)

        advanced_illness_conditions = Condition.objects.filter(
            patient=patient,
            onset_date__gte=prior_year_start.date(),
            onset_date__lte=self.timeframe.end.date(),
        )

        if advanced_illness_conditions.find(AdvancedIllness).exists():
            return True

        # Check for dementia medications (MP or prior year)
        # Use .datetime for timezone-aware datetime comparison on DateTimeField
        dementia_meds = Medication.objects.filter(
            patient=patient,
            start_date__gte=prior_year_start.datetime,
            start_date__lte=self.timeframe.end.datetime,
        )

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
        # Check frailty indicator
        if not self.has_frailty_indicator(patient):
            return False

        # Check advanced illness or dementia medications
        return self.has_advanced_illness_or_dementia_meds(patient)

    def in_nursing_home(self, patient: Patient) -> bool:
        """
        Check if patient is living long-term in a nursing home any time on or before
        the end of the measurement period.

        This is typically determined by:
        1. Coverage/insurance type indicating long-term care facility
        2. Patient address indicating institutional care facility
        3. Frequent SNF/nursing facility encounters

        Note: Canvas may track this differently depending on implementation.
        This method checks Coverage records for long-term care payer types.

        This exclusion only applies to patients age ≥66.
        """
        # Check coverage for long-term care facility indicators
        from canvas_sdk.v1.data.coverage import Coverage, TransactorCoverageType

        # Get all coverages up to end of measurement period
        coverages = Coverage.objects.filter(
            patient=patient,
            coverage_start_date__lte=self.timeframe.end.date(),
        )

        # Check if any coverage indicates long-term care
        for coverage in coverages:
            # Check coverage_type for Long Term Care
            if coverage.coverage_type == TransactorCoverageType.LTC:
                return True

            # Check plan name for keywords as fallback
            if coverage.plan:
                plan_name_lower = str(coverage.plan).lower()
                if any(keyword in plan_name_lower for keyword in self.NURSING_HOME_KEYWORDS):
                    return True

        return False

    def get_stratification(self, patient: Patient) -> int | None:
        """
        Determine which stratification group the patient belongs to.

        Per CMS125v14:
        - Stratum 1: Ages 42-51 at end of measurement period
        - Stratum 2: Ages 52-74 at end of measurement period

        Returns:
            1 for Stratum 1 (ages 42-51)
            2 for Stratum 2 (ages 52-74)
            None if patient not in denominator or outside age ranges
        """
        if not self.in_denominator(patient):
            return None

        patient_age = patient.age_at(self.timeframe.end)

        if self.STRATUM_1_START <= patient_age <= self.STRATUM_1_END:
            return 1
        elif self.STRATUM_2_START <= patient_age <= self.STRATUM_2_END:
            return 2
        else:
            return None

    def in_denominator(self, patient: Patient) -> bool:
        """
        Denominator: Equals Initial Population.

        Exclusions:
        1. Women who had a bilateral mastectomy or who have a history of a bilateral
           mastectomy or for whom there is evidence of a right and a left unilateral mastectomy.
        2. Patients who were in hospice care during the measurement year.
        3. Patients who received palliative care during the measurement period.
        4. Patients age ≥66 with frailty + advanced illness (see has_frailty_with_advanced_illness).
        5. Patients age ≥66 living long-term in nursing home (see in_nursing_home).

        Exceptions: None
        """
        if not self.in_initial_population(patient):
            return False

        # Check hospice exclusion
        if self.in_hospice_care(patient):
            return False

        # Check palliative care exclusion (all ages)
        if self.received_palliative_care(patient):
            return False

        # Check mastectomy exclusion
        if self.had_mastectomy(patient):
            return False

        # Check age-based exclusions (age ≥66 only)
        patient_age = patient.age_at(self.timeframe.end)
        if patient_age >= 66:
            # Check frailty + advanced illness/dementia exclusion
            if self.has_frailty_with_advanced_illness(patient):
                return False

            # Check nursing home exclusion
            if self.in_nursing_home(patient):
                return False

        return True

    def get_protocol_override(self, patient: Patient) -> ProtocolOverride | None:
        """Get active protocol override (adjustment) for this patient and protocol."""
        return ProtocolOverride.objects.get_active_adjustment(patient, self.protocol_key())

    def in_numerator(self, patient: Patient) -> bool:
        """
        Numerator: Women with one or more mammograms between October 1 of two years prior
        to the measurement period and the end of the measurement period (27-month window).

        Exclusions: Not Applicable
        """
        # Check for protocol override
        override = self.get_protocol_override(patient)

        if override:
            # Use custom period from override
            reference_date = arrow.get(override.reference_date)
            cycle_days = override.cycle_in_days

            # Check if we're within the cycle
            days_since_reference = (self.now - reference_date).days

            if days_since_reference <= cycle_days:
                # Within cycle, use measurement period only
                period_start = self.timeframe.start
            else:
                # Outside cycle, fall back to standard logic
                period_start = self.timeframe.start.shift(months=-1 * self.EXTRA_SCREENING_MONTHS)
        else:
            # Standard 27-month window: October 1 of two years prior to end of measurement period
            period_start = self.timeframe.start.shift(months=-1 * self.EXTRA_SCREENING_MONTHS)

        period_end = self.timeframe.end

        # Create extended timeframe for the 27-month window
        extended_timeframe = Timeframe(start=period_start, end=period_end)

        # Query for mammography billing line items using SDK's .within() method
        mammography_billing = BillingLineItem.objects.filter(patient=patient).within(
            extended_timeframe
        )

        # Get all mammography codes from both value sets
        all_screening_codes = self._combine_value_set_codes(Mammography, Tomography)

        if all_screening_codes:
            mammography_billing = mammography_billing.filter(cpt__in=all_screening_codes).order_by(
                "-note__datetime_of_service"
            )

            if mammography_billing.exists():
                # Get the most recent mammography billing item
                last_billing = mammography_billing.first()
                # Get the datetime from the note (exists() guarantees first() returns non-None)
                if (
                    last_billing is not None
                    and last_billing.note is not None
                    and last_billing.note.datetime_of_service
                ):
                    self._on_date = arrow.get(last_billing.note.datetime_of_service)
                    return True

        # Also check imaging reports (for mammographies documented outside billing)
        imaging_reports = (
            ImagingReport.objects.filter(patient=patient)
            .find(Mammography | Tomography)  # type: ignore[arg-type]
            .filter(
                original_date__gte=period_start.date(),
                original_date__lte=period_end.date(),
            )
            .order_by("-original_date")
        )

        if imaging_reports.exists():
            last_report = imaging_reports.first()
            # exists() guarantees first() returns non-None
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

        if not self.in_denominator(patient):
            # Not applicable - check if young patient
            first_due = self.first_due_in(patient)
            if first_due and first_due > 0:
                # Young patient - show when they'll be eligible
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

            # Otherwise excluded (mastectomy, hospice, etc) - no card
            return []

        # Patient is in denominator - check for protocol override for due date calculation
        override = self.get_protocol_override(patient)

        # Get stratification for reporting
        stratum = self.get_stratification(patient)
        stratum_text = self._get_stratum_text(stratum)

        if self.in_numerator(patient) and self._on_date:
            # Screening satisfied - calculate next due date
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

        # Screening due - add recommendations
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
            # Use custom cycle from override
            return (self._on_date.shift(days=override.cycle_in_days) - self.now).days

        # Standard calculation: 27 months (12 + 15)
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
        """Build the screening recommendation with coding filter."""
        coding_filter = self._build_coding_filter(Mammography, Tomography)

        instruct_command = InstructCommand()
        recommendation = instruct_command.recommend(
            title="Discuss breast cancer screening and order imaging as appropriate",
            button="Plan",
        )

        # Override context with our coding filter while preserving effect_type
        recommendation.context = {
            "filter": {"coding": coding_filter},
            "effect_type": recommendation.context.get("effect_type")
            if recommendation.context
            else None,
        }
        return recommendation
