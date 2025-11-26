import arrow

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.protocol_card import ProtocolCard, Recommendation
from canvas_sdk.events import EventType
from canvas_sdk.protocols import ClinicalQualityMeasure
from canvas_sdk.protocols.timeframe import Timeframe
from canvas_sdk.v1.data.billing import BillingLineItem
from canvas_sdk.v1.data.condition import Condition
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


class ClinicalQualityMeasure125v14(ClinicalQualityMeasure):
    """
    Breast Cancer Screening.

    Description: Percentage of women 42-74 years of age who had a mammogram to screen for breast
    cancer

    Definition: None

    Rationale: Breast cancer is one of the most common types of cancers, accounting for a quarter
    of all new cancer diagnoses for women in the U.S. (BreastCancer.Org, 2011). It ranks as the
    second leading cause of cancer-related mortality in women, accounting for nearly 40,000
    estimated deaths in 2013 (American Cancer Society, 2011).

    According to the National Cancer Institute's Surveillance Epidemiology and End Results program,
    the chance of a woman being diagnosed with breast cancer in a given year increases with age. By
    age 30, it is one in 2,212. By age 40, the chances increase to one in 235, by age 50, it
    becomes one in 54, and, by age 60, it is one in 25. From 2004 to 2008, the median age at the
    time of breast cancer diagnosis was 61 years among adult women (Tangka et al, 2010).

    In the U.S., costs associated with a diagnosis of breast cancer range from $451 to $2,520,
    factoring in continued testing, multiple office visits, and varying procedures. The total costs
    related to breast cancer add up to nearly $7 billion per year in the U.S., including $2 billion
    spent on late-stage treatment (Lavigne et al, 2008; Boykoff et al, 2009).

    Guidance: Patient self-report for procedures as well as diagnostic studies should be recorded
    in 'Procedure, Performed' template or 'Diagnostic Study, Performed' template in QRDA-1. Patient
    self-report is not allowed for laboratory tests.

    This measure evaluates primary screening. Do not count biopsies, breast ultrasounds, or MRIs,
    because they are not appropriate methods for primary breast cancer screening. Tomosynthesis
    (3D mammography) IS allowed as of CMS125v14 and is included in the screening codes.

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
            "American Cancer Society. 2010. Cancer Facts & Figures 2010. Atlanta: American Cancer Society.",
            'National Cancer Institute. 2010. "Breast Cancer Screening." http://www.cancer.gov/cancertopics/pdq/screening/breast/healthprofessional',
            "National Business Group on Health. 2011. Pathways to Managing Cancer in the Workplace. Washington: National Business Group on Health.",
            'U.S. Preventive Services Task Force (USPSTF). 2009. 1) "Screening for breast cancer: U.S. Preventive Services Task Force recommendation statement." 2) "December 2009 addendum." Ann Intern Med 151(10):716-726.',
            "BreastCancer.org. 2012. U.S. Breast Cancer Statistics. http://www.breastcancer.org/symptoms/understand_bc/statistics.jsp",
        ]

    RESPONDS_TO = EventType.Name(EventType.ASSESS_COMMAND__CONDITION_SELECTED)
    NARRATIVE_STRING = "Breast Cancer Screening CMS125v14"

    _on_date = None
    AGE_RANGE_START = 42
    AGE_RANGE_END = 74
    EXTRA_SCREENING_MONTHS = 15

    # Stratification age boundaries
    STRATUM_1_START = 42
    STRATUM_1_END = 51
    STRATUM_2_START = 52
    STRATUM_2_END = 74

    def compute(self) -> list[Effect]:
        """Compute the protocol result and return effects."""
        import json

        # For ASSESS_COMMAND__CONDITION_SELECTED events, return a log effect
        if self.event.type == EventType.ASSESS_COMMAND__CONDITION_SELECTED:
            note_uuid = self.event.context.get("note", {}).get("uuid", "unknown")
            return [
                Effect(
                    type=EffectType.LOG,
                    payload=json.dumps(
                        {"message": f"{self.NARRATIVE_STRING} triggered", "note_uuid": note_uuid}
                    ),
                )
            ]

        # For other event types, compute full protocol results
        # Get patient
        patient_id = self.patient_id_from_target()
        patient = Patient.objects.get(id=patient_id)

        # Compute and return protocol cards
        return self.compute_results(patient)

    def had_mastectomy(self, patient: Patient) -> bool:
        """Check if patient had a bilateral mastectomy or equivalent."""
        # Base query for conditions up to end of timeframe
        conditions = Condition.objects.filter(
            patient=patient, onset_date__lte=self.timeframe.end.date()
        )

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
            return (birthday_42 - self.timeframe.end).days
        return None

    def has_qualifying_visit(self, patient: Patient) -> bool:
        """
        Check if patient had a qualifying visit during the measurement period.

        Qualifying visits include:
        - Office Visit
        - Preventive Care Services
        - Annual Wellness Visit
        - Home Healthcare Services
        """
        # Get all billing line items within timeframe using SDK's .within() method
        qualifying_visits = BillingLineItem.objects.filter(patient=patient).within(self.timeframe)

        # Combine all value sets using native get_codes() method
        value_sets = [
            OfficeVisit,
            AnnualWellnessVisit,
            PreventiveCareServicesInitialOfficeVisit18AndUp,
            PreventiveCareServicesEstablishedOfficeVisit18AndUp,
            HomeHealthcareServices,
        ]

        all_codes: set[str] = set()
        for vs in value_sets:
            all_codes.update(vs.get_codes())

        return bool(all_codes and qualifying_visits.filter(cpt__in=all_codes).exists())

    def in_initial_population(self, patient: Patient) -> bool:
        """
        Initial population: Women 42-74 years of age with a visit during the measurement period.

        For canvas_sdk, we check billing line items for qualifying visit codes.
        """
        patient_age = patient.age_at(self.timeframe.end)

        # Check age and sex
        if not (self.AGE_RANGE_START <= patient_age <= self.AGE_RANGE_END):
            return False

        if patient.sex_at_birth != "F":
            return False

        # Check for qualifying visits
        return self.has_qualifying_visit(patient)

    def in_hospice_care(self, patient: Patient) -> bool:
        """
        Check if patient was in hospice care during the measurement period.

        Checks both:
        1. Billing line items with hospice codes (HospiceCareAmbulatory)
        2. Encounters with hospice codes (HospiceEncounter)
        """
        # Check billing line items for hospice codes using SDK's .within() method
        hospice_billing = BillingLineItem.objects.filter(patient=patient).within(self.timeframe)

        hospice_care_codes = HospiceCareAmbulatory.get_codes()
        hospice_encounter_codes = HospiceEncounter.get_codes()
        all_hospice_codes = hospice_care_codes | hospice_encounter_codes

        return bool(
            all_hospice_codes and hospice_billing.filter(cpt__in=all_hospice_codes).exists()
        )

    def received_palliative_care(self, patient: Patient) -> bool:
        """
        Check if patient received palliative care during the measurement period.

        Checks:
        1. Diagnosis codes for palliative care
        2. Encounter codes for palliative care
        3. Intervention codes for palliative care
        """
        # Check conditions for palliative care diagnosis
        palliative_conditions = Condition.objects.filter(
            patient=patient,
            onset_date__lte=self.timeframe.end.date(),
        )

        if palliative_conditions.find(PalliativeCareDiagnosis).exists():
            return True

        # Check billing line items for palliative care using SDK's .within() method
        palliative_billing = BillingLineItem.objects.filter(patient=patient).within(self.timeframe)

        palliative_encounter_codes = PalliativeCareEncounter.get_codes()
        palliative_intervention_codes = PalliativeCareIntervention.get_codes()
        all_palliative_codes = palliative_encounter_codes | palliative_intervention_codes

        return bool(
            all_palliative_codes
            and palliative_billing.filter(cpt__in=all_palliative_codes).exists()
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
        # Check for frailty diagnosis or symptom
        frailty_conditions = Condition.objects.filter(
            patient=patient,
            onset_date__gte=self.timeframe.start.date(),
            onset_date__lte=self.timeframe.end.date(),
        )

        if frailty_conditions.find(FrailtyDiagnosis).exists():
            return True

        if frailty_conditions.find(FrailtySymptom).exists():
            return True

        # Check for frailty encounter using SDK's .within() method
        frailty_billing = BillingLineItem.objects.filter(patient=patient).within(self.timeframe)

        frailty_encounter_codes = FrailtyEncounter.get_codes()
        return bool(
            frailty_encounter_codes
            and frailty_billing.filter(cpt__in=frailty_encounter_codes).exists()
        )

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
        # PayerType code "26" = "Medicaid - Long Term Care"
        # PayerType code "94" = "Long-term Care Insurance"
        # PayerType codes with "32123" = "Contract Nursing Home/Community Nursing Home"
        for coverage in coverages:
            # Check coverage_type for Long Term Care
            if coverage.coverage_type == TransactorCoverageType.LTC:
                return True

            # Check plan name for keywords as fallback
            if coverage.plan:
                plan_name_lower = str(coverage.plan).lower()
                if any(
                    keyword in plan_name_lower
                    for keyword in [
                        "long term care",
                        "long-term care",
                        "nursing home",
                        "nursing facility",
                        "skilled nursing",
                    ]
                ):
                    return True

        # Alternative: Check patient addresses for institutional facility indicators
        # This would need access to patient.addresses and checking for facility types
        # Not implementing this check as Canvas Patient model may not have this data easily accessible

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
        """Get active protocol override for this patient and protocol."""
        return ProtocolOverride.objects.get_active_adjustment(patient, "CMS125v14")

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
            # (measurement period start - 15 months = October 1 of two years prior)
            period_start = self.timeframe.start.shift(months=-1 * self.EXTRA_SCREENING_MONTHS)

        period_end = self.timeframe.end

        # Create extended timeframe for the 27-month window
        extended_timeframe = Timeframe(start=period_start, end=period_end)

        # Query for mammography billing line items using SDK's .within() method
        mammography_billing = BillingLineItem.objects.filter(patient=patient).within(
            extended_timeframe
        )

        # Get all mammography codes from both value sets using native get_codes()
        mammography_codes = Mammography.get_codes()
        tomography_codes = Tomography.get_codes()
        all_screening_codes = mammography_codes | tomography_codes

        if all_screening_codes:
            mammography_billing = mammography_billing.filter(cpt__in=all_screening_codes).order_by(
                "-note__datetime_of_service"
            )

            if mammography_billing.exists():
                # Get the most recent mammography billing item
                last_billing = mammography_billing.first()
                # Get the datetime from the note
                if (
                    last_billing is not None
                    and last_billing.note is not None
                    and last_billing.note.datetime_of_service
                ):
                    self._on_date = arrow.get(last_billing.note.datetime_of_service)
                    return True

        # Also check imaging reports (for mammographies documented outside billing)
        # Use ImagingReport.find() to filter by mammography/tomography codes
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
            if last_report is not None and last_report.original_date is not None:
                self._on_date = arrow.get(last_report.original_date)
                return True

        return False

    def compute_results(self, patient: Patient) -> list[Effect]:
        """
        Compute the results for the protocol and return effects.

        Clinical recommendation: The U.S. Preventive Services Task Force (USPSTF) recommends
        biennial screening mammography for women aged 50-74 years (B recommendation).

        Returns:
            list[Effect]: Protocol cards to display in Canvas UI
        """
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
                    key="CMS125v14",
                    title="Breast Cancer Screening",
                    narrative=narrative,
                    status=ProtocolCard.Status.NOT_APPLICABLE,
                    due_in=first_due,
                )
                return [card.apply()]

            # Otherwise excluded (mastectomy, hospice, etc) - no card
            return []

        # Patient is in denominator
        # Check for protocol override for due date calculation
        override = self.get_protocol_override(patient)

        # Get stratification for reporting
        stratum = self.get_stratification(patient)
        stratum_text = ""
        if stratum == 1:
            stratum_text = " (Stratum 1: Ages 42-51)"
        elif stratum == 2:
            stratum_text = " (Stratum 2: Ages 52-74)"

        if self.in_numerator(patient) and self._on_date:
            # Screening satisfied - calculate next due date
            if override:
                # Use custom cycle from override
                cycle_days = override.cycle_in_days
                due_in_days = (self._on_date.shift(days=cycle_days) - self.now).days
            else:
                # Standard calculation: 27 months (12 + 15)
                extra_months = self.EXTRA_SCREENING_MONTHS
                due_in_days = (
                    self._on_date.shift(days=self.timeframe.duration, months=extra_months)
                    - self.now
                ).days

            months_ago = (self.now - self._on_date).days // 30
            if months_ago == 0:
                time_phrase = "today"
            elif months_ago == 1:
                time_phrase = "1 month ago"
            else:
                time_phrase = f"{months_ago} months ago"

            narrative = (
                f"{patient.first_name} had a mammography {time_phrase} on "
                f"{self._on_date.format('M/D/YY')}. "
                f"Next screening due in {due_in_days} days.{stratum_text}"
            )

            card = ProtocolCard(
                patient_id=patient.id,
                key="CMS125v14",
                title="Breast Cancer Screening",
                narrative=narrative,
                status=ProtocolCard.Status.SATISFIED,
                due_in=due_in_days,
            )

            return [card.apply()]

        else:
            # Screening due - add recommendations
            narrative = (
                f"No mammography found in the last 27 months. "
                f"{patient.first_name} is due for breast cancer screening.{stratum_text}"
            )

            card = ProtocolCard(
                patient_id=patient.id,
                key="CMS125v14",
                title="Breast Cancer Screening",
                narrative=narrative,
                status=ProtocolCard.Status.DUE,
                due_in=-1,  # Already overdue
                recommendations=[
                    Recommendation(
                        title="Discuss breast cancer screening and order mammography",
                        button="Order",
                    )
                ],
            )

            return [card.apply()]
