"""CMS130v14 Colorectal Cancer Screening protocol implementation."""

from typing import Any

from django.db.models import Q

from canvas_sdk.commands import ImagingOrderCommand, LabOrderCommand, ReferCommand
from canvas_sdk.commands.constants import ServiceProvider
from canvas_sdk.effects.protocol_card.protocol_card import ProtocolCard
from canvas_sdk.events import EventType
from canvas_sdk.protocols import ClinicalQualityMeasure
from canvas_sdk.v1.data import Observation, Patient
from canvas_sdk.v1.data.claim_line_item import ClaimLineItem
from canvas_sdk.v1.data.condition import Condition
from canvas_sdk.v1.data.device import Device
from canvas_sdk.v1.data.encounter import Encounter
from canvas_sdk.v1.data.imaging import ImagingReport
from canvas_sdk.v1.data.lab import LabReport
from canvas_sdk.v1.data.medication import Medication
from canvas_sdk.v1.data.note import Note, NoteType
from canvas_sdk.v1.data.referral import ReferralReport
from canvas_sdk.value_set.v2026.condition import (
    AdvancedIllness,
    FrailtyDiagnosis,
    HospiceDiagnosis,
    MalignantNeoplasmOfColon,
    PalliativeCareDiagnosis,
)
from canvas_sdk.value_set.v2026.diagnostic_study import CtColonography
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
from canvas_sdk.value_set.v2026.laboratory_test import FecalOccultBloodTestFobt, SdnaFitTest
from canvas_sdk.value_set.v2026.medication import DementiaMedications
from canvas_sdk.value_set.v2026.procedure import (
    Colonoscopy,
    FlexibleSigmoidoscopy,
    TotalColectomy,
)
from canvas_sdk.value_set.v2026.device import FrailtyDevice
from canvas_sdk.value_set.v2026.symptom import FrailtySymptom

from logger import log


# Constants
AGE_RANGE_START = 46
AGE_RANGE_END = 75
SCREENING_INTERVALS_DAYS = {
    "FOBT": 365,
    "FIT-DNA": 730,  # 2 years
    "Flexible sigmoidoscopy": 1460,  # 4 years
    "CT Colonography": 1460,  # 4 years
    "Colonoscopy": 3285,  # 9 years
}
SCREENING_LOOKBACK_YEARS = {
    "FOBT": 1,
    "FIT-DNA": 2,
    "Flexible sigmoidoscopy": 4,
    "CT Colonography": 4,
    "Colonoscopy": 9,
}
DISCHARGE_TO_HOME_HOSPICE_SNOMED = "428361000124107"
DISCHARGE_TO_FACILITY_HOSPICE_SNOMED = "428371000124100"
LOINC_SYSTEM_IDENTIFIERS = ["LOINC", "http://loinc.org"]
HOUSING_STATUS_LOINC = "71802-3"
LIVES_IN_NURSING_HOME_SNOMED = "160734000"
PALLIATIVE_CARE_ASSESSMENT_LOINC = "71007-9"
SCREENING_DIAGNOSIS_CODE = "Z1211"
SCREENING_CONTEXT = {
    "conditions": [
        [
            {
                "code": SCREENING_DIAGNOSIS_CODE,
                "system": "ICD-10",
                "display": "Encounter for screening for malignant neoplasm of colon",
            }
        ]
    ]
}


class CMS130v14ColorectalCancerScreening(ClinicalQualityMeasure):
    """CMS130v14 Colorectal Cancer Screening clinical quality measure."""

    class Meta:
        title = "Colorectal Cancer Screening"
        description = (
            "Percentage of adults 45-75 years of age who had appropriate screening for colorectal cancer."
        )
        version = "2026-01-01v14"
        default_display_interval_in_days = 365 * 9
        information = "https://ecqi.healthit.gov/sites/default/files/ecqm/measures/CMS130-v14.0.000-QDM.html"
        identifiers = ["CMS130v14"]
        types = ["CQM"]
        authors = ["National Committee for Quality Assurance"]
        references = [
            'Howlader N, Noone AM, Krapcho M, Miller D, Brest A, Yu M, Ruhl J, Tatalovich Z, Mariotto A, Lewis DR, Chen HS, Feuer EJ, Cronin KA (2020). SEER Cancer Statistics Review, 195-2017. Retrieved September 22, 2020, https://seer.cancer.gov/csr/1975_2017/',
            'SEER. (n.d.). Cancer of the Colon and Rectum. https://seer.cancer.gov/statfacts/html/colorect.html',
            'US Preventive Services Task Force, Davidson, K. W., Barry, M. J., Mangione, C. M., Cabana, M., Caughey, A. B., Davis, E. M., Donahue, K. E., Doubeni, C. A., Krist, A. H., Kubik, M., Li, L., Ogedegbe, G., Owens, D. K., Pbert, L., Silverstein, M., Stevermer, J., Tseng, C. W., & Wong, J. B. (2021). Screening for Colorectal Cancer: US Preventive Services Task Force Recommendation Statement. JAMA, 325(19), 1965–1977. https://doi.org/10.1001/jama.2021.6238',
        ]

    RESPONDS_TO = [
        EventType.Name(EventType.CONDITION_CREATED),
        EventType.Name(EventType.CONDITION_UPDATED),
        EventType.Name(EventType.PATIENT_CREATED),
        EventType.Name(EventType.PATIENT_UPDATED),
        EventType.Name(EventType.OBSERVATION_CREATED),
        EventType.Name(EventType.OBSERVATION_UPDATED),
    ]

    def __init__(self, *args, **kwargs):
        """Initialize protocol instance."""
        super().__init__(*args, **kwargs)
        self._last_exam = None
        self._not_applicable_reason = None

    def compute(self) -> list:
        """Compute protocol result for the patient."""
        try:
            patient_id = self.context.get("patient", {}).get("id")
            if not patient_id:
                log.warning("CMS130v14: Could not determine patient ID from event, skipping")
                return []

            patient = Patient.objects.filter(id=patient_id).first()
            if not patient:
                log.warning(f"CMS130v14: Patient {patient_id} not found, skipping")
                return []

            # Reset reason tracking
            self._not_applicable_reason = None

            if not self._in_initial_population(patient):
                return [self._create_not_applicable_card(patient)]

            if not self._in_denominator(patient):
                return [self._create_not_applicable_card(patient)]

            if self._in_numerator(patient):
                return [self._create_satisfied_card(patient, self._last_exam)]
            else:
                return [self._create_due_card(patient)]

        except Exception as e:
            log.error(f"CMS130v14: Error in protocol compute: {str(e)}")
            return []

    def _in_initial_population(self, patient: Patient) -> bool:
        """Check if patient is in initial population (age 46-75 with eligible encounter)."""
        return self._check_age_46_to_75(patient) and self._has_eligible_encounter_in_period(patient)

    def _in_denominator(self, patient: Patient) -> bool:
        """
        Check if patient is in denominator (initial population minus exclusions).
        
        Note: This method assumes the patient is already in the initial population
        (checked in compute() before calling this method).
        
        Per CMS130v14 Denominator Exclusions:
        - Exclude patients who are in hospice care for any part of the measurement period
        - Exclude patients with a diagnosis or past history of total colectomy or colorectal cancer
        - Exclude patients 66 and older with frailty AND (advanced illness OR dementia meds)
        - Exclude patients 66 and older who are living long term in a nursing home
        - Exclude patients receiving palliative care for any part of the measurement period
        """
        if self._has_colon_exclusion(patient):
            return False

        if self._has_hospice_care_in_period(patient):
            return False

        # Check age once for age 66+ exclusions
        age = self._calculate_age(patient)
        if age is not None and age >= 66:
            # Exclude patients 66+ with frailty AND (advanced illness OR dementia meds)
            if self._has_frailty_indicators(patient) and self._has_advanced_illness_or_dementia_meds(patient):
                self._not_applicable_reason = f"{patient.first_name} is age 66 or older with frailty and advanced illness or dementia medications and is excluded from colorectal cancer screening."
                return False

            # Exclude patients 66+ living long term in nursing home
            if self._is_living_in_nursing_home(patient):
                return False

        if self._has_palliative_care_in_period(patient):
            return False

        return True

    def _in_numerator(self, patient: Patient) -> bool:
        """
        Check if patient has had appropriate screening.
        
        Checks screening types in priority order and sets _last_exam when found, returning immediately.
        Priority order: FOBT > FIT-DNA > Flexible Sigmoidoscopy > CT Colonography > Colonoscopy
        """
        self._last_exam = None

        if exam := self._check_fobt(patient):
            self._last_exam = exam
            return True

        if exam := self._check_fit_dna(patient):
            self._last_exam = exam
            return True

        if exam := self._check_flexible_sigmoidoscopy(patient):
            self._last_exam = exam
            return True

        if exam := self._check_ct_colonography(patient):
            self._last_exam = exam
            return True

        if exam := self._check_colonoscopy(patient):
            self._last_exam = exam
            return True

        return False

    def _check_fobt(self, patient: Patient) -> dict | None:
        """Check for FOBT within 1 year."""
        period_start = self.timeframe.end.shift(years=-SCREENING_LOOKBACK_YEARS["FOBT"])
        report = self._find_lab_report(patient, FecalOccultBloodTestFobt, period_start, self.timeframe.end)
        if report:
            return {
                "date": report.original_date,
                "what": "FOBT",
                "days": SCREENING_INTERVALS_DAYS["FOBT"],
            }
        return None

    def _check_fit_dna(self, patient: Patient) -> dict | None:
        """Check for FIT-DNA (sDNA FIT Test) within 2 years."""
        period_start = self.timeframe.end.shift(years=-SCREENING_LOOKBACK_YEARS["FIT-DNA"])
        report = self._find_lab_report(patient, SdnaFitTest, period_start, self.timeframe.end)
        if report:
            return {
                "date": report.original_date,
                "what": "FIT-DNA",
                "days": SCREENING_INTERVALS_DAYS["FIT-DNA"],
            }
        return None

    def _check_flexible_sigmoidoscopy(self, patient: Patient) -> dict | None:
        """Check for Flexible Sigmoidoscopy within 4 years (imaging or referral)."""
        period_start = self.timeframe.end.shift(years=-SCREENING_LOOKBACK_YEARS["Flexible sigmoidoscopy"])

        report = self._find_imaging_report(patient, FlexibleSigmoidoscopy, period_start, self.timeframe.end)
        if report:
            return {
                "date": report.original_date,
                "what": "Flexible sigmoidoscopy",
                "days": SCREENING_INTERVALS_DAYS["Flexible sigmoidoscopy"],
            }

        report = self._find_referral_report(patient, FlexibleSigmoidoscopy, period_start, self.timeframe.end)
        if report:
            return {
                "date": report.original_date,
                "what": "Flexible sigmoidoscopy",
                "days": SCREENING_INTERVALS_DAYS["Flexible sigmoidoscopy"],
            }
        return None

    def _check_ct_colonography(self, patient: Patient) -> dict | None:
        """Check for CT Colonography within 4 years (imaging or referral)."""
        period_start = self.timeframe.end.shift(years=-SCREENING_LOOKBACK_YEARS["CT Colonography"])

        report = self._find_imaging_report(patient, CtColonography, period_start, self.timeframe.end)
        if report:
            return {
                "date": report.original_date,
                "what": "CT Colonography",
                "days": SCREENING_INTERVALS_DAYS["CT Colonography"],
            }

        report = self._find_referral_report(patient, CtColonography, period_start, self.timeframe.end)
        if report:
            return {
                "date": report.original_date,
                "what": "CT Colonography",
                "days": SCREENING_INTERVALS_DAYS["CT Colonography"],
            }
        return None

    def _check_colonoscopy(self, patient: Patient) -> dict | None:
        """Check for Colonoscopy within 9 years (imaging or referral)."""
        period_start = self.timeframe.end.shift(years=-SCREENING_LOOKBACK_YEARS["Colonoscopy"])

        report = self._find_imaging_report(patient, Colonoscopy, period_start, self.timeframe.end)
        if report:
            return {
                "date": report.original_date,
                "what": "Colonoscopy",
                "days": SCREENING_INTERVALS_DAYS["Colonoscopy"],
            }

        report = self._find_referral_report(patient, Colonoscopy, period_start, self.timeframe.end)
        if report:
            return {
                "date": report.original_date,
                "what": "Colonoscopy",
                "days": SCREENING_INTERVALS_DAYS["Colonoscopy"],
            }
        return None

    def _calculate_age(self, patient: Patient) -> int | None:
        """Calculate patient age at end of measurement period."""
        try:
            if not getattr(patient, "birth_date", None):
                return None

            import arrow
            birth_date = arrow.get(patient.birth_date)
            age_years = (self.timeframe.end - birth_date).days // 365
            return age_years
        except Exception as e:
            log.error(f"CMS130v14: Error calculating age: {str(e)}")
            return None

    def _check_age_46_to_75(self, patient: Patient) -> bool:
        """Check if patient is between 46 and 75 years old."""
        try:
            if not getattr(patient, "birth_date", None):
                self._not_applicable_reason = f"{patient.first_name} does not meet the age criteria (46-75 years) for colorectal cancer screening."
                return False

            import arrow
            birth_date = arrow.get(patient.birth_date)
            age_years = (self.timeframe.end - birth_date).days // 365

            if age_years < AGE_RANGE_START:
                self._not_applicable_reason = f"{patient.first_name} is under {AGE_RANGE_START} years of age and does not meet the criteria for colorectal cancer screening."
                return False
            elif age_years > AGE_RANGE_END:
                self._not_applicable_reason = f"{patient.first_name} is over {AGE_RANGE_END} years of age and does not meet the criteria for colorectal cancer screening."
                return False

            return True
        except Exception as e:
            log.error(f"CMS130v14: Error computing age: {str(e)}")
            self._not_applicable_reason = f"{patient.first_name} does not meet the age criteria (46-75 years) for colorectal cancer screening."
            return False

    def _has_eligible_encounter_in_period(self, patient: Patient) -> bool:
        """Check if patient has eligible encounter within measurement period."""
        try:
            notes = Note.objects.filter(
                patient__id=patient.id,
                datetime_of_service__range=(
                    self.timeframe.start.datetime,
                    self.timeframe.end.datetime,
                ),
            ).select_related("note_type_version")

            visit_value_sets = [
                OfficeVisit,
                PreventiveCareServicesEstablishedOfficeVisit18AndUp,
                PreventiveCareServicesInitialOfficeVisit18AndUp,
                HomeHealthcareServices,
                AnnualWellnessVisit,
                VirtualEncounter,
                TelephoneVisits,
            ]

            for note in notes:
                if not note.note_type_version:
                    continue

                if self._coding_in_value_set_for_note_type(note.note_type_version, visit_value_sets):
                    return True

            # Optimistic rule: allow processing even without matched encounter
            # Don't set reason here as this is expected behavior
            return True
        except Exception as e:
            log.error(f"CMS130v14: Error checking eligible encounters: {str(e)}")
            return True

    def _has_colon_exclusion(self, patient: Patient) -> bool:
        """
        Check if patient has colon exclusions (total colectomy or malignant neoplasm of colon).
        
        Per CMS130v14 Denominator Exclusions:
        - Diagnosis of colorectal cancer that starts on or before the end of the measurement period
        - OR a past history of total colectomy that ends on or before the end of the measurement period
        """
        try:
            end_date = self.timeframe.end.date()
            
            # Check for total colectomy: past history that ends on or before the end of measurement period
            # Per spec: "a past history of total colectomy that ends on or before the end of the measurement period"
            # This means resolution_date <= end_date (for resolved/past history)
            # We also include active total colectomies that started on or before end_date (if still active, they're excluded)
            has_total_colectomy = (
                Condition.objects.for_patient(patient.id)
                .committed()
                .find(TotalColectomy)
                .filter(entered_in_error_id__isnull=True)
                .filter(
                    # Past history: resolved and ended on or before end of measurement period
                    Q(resolution_date__isnull=False, resolution_date__lte=end_date)
                    # Active: started on or before end of measurement period (still active, so excluded)
                    | Q(resolution_date__isnull=True, onset_date__lte=end_date)
                    # NULL onset_date treated as overlapping per Canvas convention
                    | Q(onset_date__isnull=True)
                )
                .exists()
            )
            
            if has_total_colectomy:
                self._not_applicable_reason = f"{patient.first_name} has a history of total colectomy and is excluded from colorectal cancer screening."
                return True

            # Check for colorectal cancer: diagnosis that starts on or before the end of measurement period
            # onset_date <= end_date OR onset_date IS NULL (treated as overlapping per Canvas convention)
            has_colorectal_cancer = (
                Condition.objects.for_patient(patient.id)
                .committed()
                .find(MalignantNeoplasmOfColon)
                .filter(entered_in_error_id__isnull=True)
                .filter(
                    Q(onset_date__isnull=True) | Q(onset_date__lte=end_date)
                )
                .exists()
            )
            
            if has_colorectal_cancer:
                self._not_applicable_reason = f"{patient.first_name} has a history of malignant neoplasm of colon and is excluded from colorectal cancer screening."
                return True

            return False
        except Exception as e:
            log.error(f"CMS130v14: Error checking colon exclusions: {str(e)}")
            return False

    def _build_period_overlap_query(self, start_date, end_date) -> Q:
        """
        Build query for conditions whose prevalencePeriod overlaps given period.

        Per CMS130v14 and Canvas convention: A condition overlaps if:
        - onset_date is NULL (treated as overlapping per Canvas convention), OR
        - onset_date <= end_date AND (no resolution OR resolution_date >= start_date)

        Args:
            start_date: Start of the period to check
            end_date: End of the period to check

        Returns:
            Django Q object for filtering conditions
        """
        return Q(onset_date__isnull=True) | (
            Q(onset_date__lte=end_date)
            & (Q(resolution_date__isnull=True) | Q(resolution_date__gte=start_date))
        )

    def _get_value_set_codes(self, value_set_class, *code_attrs):
        """
        Safely retrieve and combine codes from value set attributes.

        Args:
            value_set_class: The value set class to retrieve codes from
            *code_attrs: One or more attribute names (e.g., 'SNOMEDCT', 'ICD10CM', 'CPT')

        Returns:
            Set of codes from all specified attributes, empty set if none exist
        """
        codes = set()
        for attr in code_attrs:
            attr_value = getattr(value_set_class, attr, None)
            if attr_value:
                codes |= attr_value
        return codes

    def _observation_exists(
        self,
        patient: Patient,
        codings_code: str,
        value_codings_codes: set[str],
        timeframe_start,
        timeframe_end,
    ) -> bool:
        """
        Check if specified observation exists in specified timeframe.

        Handles two patterns due to inconsistent home-app implementation:
        1. Physical Exam Pattern: codings=exam type (LOINC), value_codings=result
        2. Questionnaire Pattern: codings=finding (SNOMED) directly

        Also handles datetime fallbacks:
        - effective_datetime (when observation occurred - vitals, labs, imaging)
        - is_member_of.effective_datetime (for child observations like individual lab values or vital signs)
        """
        try:
            date_filter = Q(
                effective_datetime__gte=timeframe_start,
                effective_datetime__lte=timeframe_end,
            ) | Q(
                is_member_of__effective_datetime__gte=timeframe_start,
                is_member_of__effective_datetime__lte=timeframe_end,
                effective_datetime__isnull=True,
            )

            code_filter = Q(
                codings__code=codings_code, value_codings__code__in=value_codings_codes
            ) | Q(codings__code__in=value_codings_codes)

            observations = (
                Observation.objects.for_patient(patient.id)
                .committed()
                .filter(date_filter, code_filter)
            )

            return observations.exists()

        except Exception as e:
            log.error(
                f"CMS130v14: Error checking observation for code {codings_code} and value codes {value_codings_codes}: {str(e)}"
            )
            return False

    def _has_hospice_care_in_period(self, patient: Patient) -> bool:
        """
        Check if patient is in hospice care during the measurement period.

        Per CMS131v14 CQL "Hospice.Has Hospice Services", checks for:
        - Inpatient encounter with discharge disposition to hospice (SNOMED 428361000124107, 428371000124100)
        - Hospice Encounter overlapping measurement period
        - Hospice care assessment (LOINC 45755-6) with result "Yes"
        - Hospice Care Ambulatory intervention orders/performed
        - Hospice Diagnosis overlapping measurement period
        """
        try:
            start_date = self.timeframe.start.datetime
            end_date = self.timeframe.end.datetime

            # 1. Check for hospice diagnosis (using Condition model)
            has_hospice_diagnosis = (
                Condition.objects.for_patient(patient.id)
                .find(HospiceDiagnosis)
                .active()
                .filter(entered_in_error_id__isnull=True)
                .exists()
            )

            if has_hospice_diagnosis:
                log.info(f"CMS130v14: Found hospice diagnosis for patient {patient.id}")
                self._not_applicable_reason = f"{patient.first_name} is receiving hospice care and is excluded from colorectal cancer screening."
                return True

            # 2. Check for hospice encounters (using Encounter model)
            hospice_encounter_codes = self._get_value_set_codes(
                HospiceEncounter, "SNOMEDCT", "ICD10CM"
            )

            if hospice_encounter_codes:
                has_hospice_encounter = Encounter.objects.filter(
                    note__patient=patient,
                    note__note_type_version__code__in=hospice_encounter_codes,
                    state__in=["CON", "STA"],
                    start_time__gte=start_date,
                    start_time__lte=end_date,
                ).exists()

                if has_hospice_encounter:
                    log.info(f"CMS130v14: Found hospice encounter for patient {patient.id}")
                    self._not_applicable_reason = f"{patient.first_name} is receiving hospice care and is excluded from colorectal cancer screening."
                    return True

            # 3. Check for discharge to hospice via observations (discharge disposition)
            discharge_to_hospice_codes = {
                DISCHARGE_TO_HOME_HOSPICE_SNOMED,
                DISCHARGE_TO_FACILITY_HOSPICE_SNOMED,
            }

            has_discharge_to_hospice = (
                Observation.objects.for_patient(patient.id)
                .filter(
                    effective_datetime__gte=start_date,
                    effective_datetime__lte=end_date,
                    value_codings__code__in=discharge_to_hospice_codes,
                    value_codings__system__in=[
                        "SNOMED",
                        "SNOMEDCT",
                        "http://snomed.info/sct",
                    ],
                )
                .exists()
            )

            if has_discharge_to_hospice:
                log.info(f"CMS130v14: Found discharge to hospice for patient {patient.id}")
                self._not_applicable_reason = f"{patient.first_name} is receiving hospice care and is excluded from colorectal cancer screening."
                return True

            # 4. Check for hospice care assessment (LOINC 45755-6 "Hospice care [Minimum Data Set]")
            has_hospice_assessment = (
                Observation.objects.for_patient(patient.id)
                .filter(
                    effective_datetime__gte=start_date,
                    effective_datetime__lte=end_date,
                    codings__code="45755-6",
                    codings__system__in=LOINC_SYSTEM_IDENTIFIERS,
                    value_codings__code="373066001",  # Yes (qualifier value)
                    value_codings__system__in=[
                        "SNOMED",
                        "SNOMEDCT",
                        "http://snomed.info/sct",
                    ],
                )
                .exists()
            )

            if has_hospice_assessment:
                log.info(f"CMS130v14: Found hospice care assessment for patient {patient.id}")
                self._not_applicable_reason = f"{patient.first_name} is receiving hospice care and is excluded from colorectal cancer screening."
                return True

            # 5. Check for hospice care ambulatory interventions via claims (orders/performed)
            hospice_intervention_codes = (
                HospiceCareAmbulatory.CPT
                | HospiceCareAmbulatory.HCPCSLEVELII
                | HospiceCareAmbulatory.SNOMEDCT
            )

            hospice_claims = ClaimLineItem.objects.filter(
                claim__note__patient=patient,
                status="active",
                from_date__gte=self.timeframe.start.date().isoformat(),
                from_date__lte=self.timeframe.end.date().isoformat(),
                proc_code__in=hospice_intervention_codes,
            )

            if hospice_claims.exists():
                first_claim = hospice_claims.first()
                if first_claim:
                    log.info(
                        f"CMS130v14: Found hospice care claim (code: {first_claim.proc_code}) for patient {patient.id}"
                    )
                self._not_applicable_reason = f"{patient.first_name} is receiving hospice care and is excluded from colorectal cancer screening."
                return True

            return False
        except Exception as e:
            log.error(f"CMS130v14: Error checking hospice status: {str(e)}")
            return False

    def _has_frailty_indicators(self, patient: Patient) -> bool:
        """
        Check if patient has frailty indicators during measurement period.
        
        Per CMS130v14 CQL "Has Criteria Indicating Frailty", checks for:
        - Device orders for frailty devices
        - Assessment observations with frailty device results
        - Frailty diagnoses overlapping measurement period
        - Frailty encounters overlapping measurement period
        - Frailty symptoms overlapping measurement period
        
        Note: This method is only called for patients age 66+.
        """
        try:
            # Check all frailty indicators
            if self._has_frailty_device_orders(patient):
                log.info(f"CMS130v14: Patient {patient.id} age 66+ has frailty device orders")
                return True

            if self._has_frailty_device_observations(patient):
                log.info(f"CMS130v14: Patient {patient.id} age 66+ has frailty device observations")
                return True

            if self._has_frailty_diagnoses(patient):
                log.info(f"CMS130v14: Patient {patient.id} age 66+ has frailty diagnoses")
                return True

            if self._has_frailty_encounters(patient):
                log.info(f"CMS130v14: Patient {patient.id} age 66+ has frailty encounters")
                return True

            if self._has_frailty_symptoms(patient):
                log.info(f"CMS130v14: Patient {patient.id} age 66+ has frailty symptoms")
                return True

            return False
        except Exception as e:
            log.error(f"CMS130v14: Error checking frailty: {str(e)}")
            return False

    def _has_frailty_device_orders(self, patient: Patient) -> bool:
        """
        Check for device orders with frailty device codes during measurement period.

        Per CMS130v14: Device, Order: "Frailty Device" - authorDatetime during day of "Measurement Period".

        Note: Device model in SDK v1 doesn't have a note relationship, only note_id.
        We primarily check via ClaimLineItem for DME codes instead.
        """
        try:
            # Check ClaimLineItem for DME (Durable Medical Equipment) codes
            frailty_device_hcpcs = (
                FrailtyDevice.HCPCSLEVELII if hasattr(FrailtyDevice, "HCPCSLEVELII") else set()
            )

            if frailty_device_hcpcs:
                has_dme_claim = ClaimLineItem.objects.filter(
                    claim__note__patient=patient,
                    status="active",
                    from_date__gte=self.timeframe.start.date().isoformat(),
                    from_date__lte=self.timeframe.end.date().isoformat(),
                    proc_code__in=frailty_device_hcpcs,
                ).exists()

                if has_dme_claim:
                    log.info(f"CMS130v14: Found frailty device DME claim for patient {patient.id}")
                    return True

            # Also check Device model for any ordered devices (no date filter due to SDK limitation)
            # This is a fallback check - less precise but catches device orders
            has_device_order = Device.objects.filter(
                patient=patient,
                status="ordered",
            ).exists()

            if has_device_order:
                log.info(f"CMS130v14: Found device order for patient {patient.id}")
                return True

            return False
        except Exception as e:
            log.error(f"CMS130v14: Error checking frailty device orders: {str(e)}")
            return False

    def _has_frailty_device_observations(self, patient: Patient) -> bool:
        """
        Check for observations with frailty device codes in value_codings during measurement period.

        Per CMS130v14: Assessment, Performed: "Medical equipment used" result in "Frailty Device".
        """
        try:
            # Get all SNOMED codes from FrailtyDevice value set
            frailty_device_snomed = self._get_value_set_codes(FrailtyDevice, "SNOMEDCT")

            if not frailty_device_snomed:
                return False

            # Check for observations with frailty device codes as value codings
            # Include observations with null effective_datetime or within the measurement period
            has_observation = (
                Observation.objects.for_patient(patient.id)
                .filter(
                    Q(effective_datetime__isnull=True)
                    | Q(
                        effective_datetime__gte=self.timeframe.start.datetime,
                        effective_datetime__lte=self.timeframe.end.datetime,
                    ),
                    value_codings__code__in=frailty_device_snomed,
                    value_codings__system__in=[
                        "SNOMED",
                        "SNOMEDCT",
                        "http://snomed.info/sct",
                    ],
                )
                .exists()
            )

            if has_observation:
                log.info(f"CMS130v14: Found frailty device observation for patient {patient.id}")
                return True

            return False
        except Exception as e:
            log.error(f"CMS130v14: Error checking frailty device observations: {str(e)}")
            return False

    def _has_frailty_diagnoses(self, patient: Patient) -> bool:
        """
        Check for frailty diagnoses overlapping measurement period.

        Per CMS130v14: Diagnosis: "Frailty Diagnosis" - prevalencePeriod overlaps day of "Measurement Period".
        """
        try:
            start_date = self.timeframe.start.date()
            end_date = self.timeframe.end.date()

            # Build overlap query using helper method
            overlap_query = self._build_period_overlap_query(start_date, end_date)

            has_frailty_diagnosis = (
                Condition.objects.for_patient(patient.id)
                .find(FrailtyDiagnosis)
                .committed()
                .filter(entered_in_error_id__isnull=True)
                .filter(overlap_query)
                .exists()
            )

            if has_frailty_diagnosis:
                log.info(f"CMS130v14: Found frailty diagnosis for patient {patient.id}")

            return has_frailty_diagnosis
        except Exception as e:
            log.error(f"CMS130v14: Error checking frailty diagnoses: {str(e)}")
            return False

    def _has_frailty_encounters(self, patient: Patient) -> bool:
        """
        Check for frailty encounters during measurement period.
        
        Per CMS130v14: Encounter, Performed: "Frailty Encounter" - relevantPeriod overlaps day of "Measurement Period".
        """
        try:
            start_date = self.timeframe.start.datetime
            end_date = self.timeframe.end.datetime

            # Check via Encounter model for SNOMED codes
            frailty_snomed = self._get_value_set_codes(FrailtyEncounter, "SNOMEDCT")

            if frailty_snomed:
                has_encounter = Encounter.objects.filter(
                    note__patient=patient,
                    note__note_type_version__code__in=frailty_snomed,
                    state__in=["CON", "STA"],
                    start_time__gte=start_date,
                    start_time__lte=end_date,
                ).exists()

                if has_encounter:
                    log.info(
                        f"CMS130v14: Found frailty encounter (SNOMED) for patient {patient.id}"
                    )
                    return True

            # Check via ClaimLineItem for CPT/HCPCS codes
            frailty_cpt = FrailtyEncounter.CPT if hasattr(FrailtyEncounter, "CPT") else set()
            frailty_hcpcs = (
                FrailtyEncounter.HCPCSLEVELII
                if hasattr(FrailtyEncounter, "HCPCSLEVELII")
                else set()
            )
            frailty_codes = frailty_cpt | frailty_hcpcs

            if frailty_codes:
                has_claim = ClaimLineItem.objects.filter(
                    claim__note__patient=patient,
                    status="active",
                    from_date__gte=self.timeframe.start.date().isoformat(),
                    from_date__lte=self.timeframe.end.date().isoformat(),
                    proc_code__in=frailty_codes,
                ).exists()

                if has_claim:
                    log.info(f"CMS130v14: Found frailty encounter (claim) for patient {patient.id}")
                    return True

            return False
        except Exception as e:
            log.error(f"CMS130v14: Error checking frailty encounters: {str(e)}")
            return False

    def _has_frailty_symptoms(self, patient: Patient) -> bool:
        """
        Check for frailty symptoms overlapping measurement period.

        Per CMS130v14: Symptom: "Frailty Symptom" - prevalencePeriod overlaps day of "Measurement Period".

        Note: SDK v1 doesn't expose the 'notes' field on Condition.
        We check for frailty symptom codes without differentiating symptoms from diagnoses.
        """
        try:
            start_date = self.timeframe.start.date()
            end_date = self.timeframe.end.date()

            # Build overlap query using helper method
            overlap_query = self._build_period_overlap_query(start_date, end_date)

            has_frailty_symptom = (
                Condition.objects.for_patient(patient.id)
                .find(FrailtySymptom)
                .committed()
                .filter(entered_in_error_id__isnull=True)
                .filter(overlap_query)
                .exists()
            )

            if has_frailty_symptom:
                log.info(f"CMS130v14: Found frailty symptom for patient {patient.id}")

            return has_frailty_symptom
        except Exception as e:
            log.error(f"CMS130v14: Error checking frailty symptoms: {str(e)}")
            return False

    def _has_advanced_illness_or_dementia_meds(self, patient: Patient) -> bool:
        """
        Check if patient has advanced illness or dementia medications.
        
        Per CMS130v14 CQL:
        - Advanced illness diagnosis that starts during the measurement period or the year prior
        - OR taking dementia medications during the measurement period or the year prior.
        """
        try:
            start_date = self.timeframe.start.shift(years=-1).date()
            end_date = self.timeframe.end.date()

            # Check for advanced illness conditions in measurement period or year prior
            from django.db.models import Q
            has_advanced_illness = (
                Condition.objects.for_patient(patient.id)
                .find(AdvancedIllness)
                .filter(
                    Q(onset_date__isnull=True)  # Include conditions with NULL onset date
                    | Q(onset_date__lte=end_date, onset_date__gte=start_date)
                )
                .filter(entered_in_error_id__isnull=True)
                .exists()
            )

            if has_advanced_illness:
                log.info(f"CMS130v14: Patient {patient.id} has advanced illness")
                return True

            # Convert dates to datetime for efficient comparison
            import arrow
            start_datetime = arrow.get(start_date).datetime
            end_datetime = (
                arrow.get(end_date)
                .replace(hour=23, minute=59, second=59, microsecond=999999)
                .datetime
            )

            has_dementia_meds = (
                Medication.objects.for_patient(patient.id)
                .committed()
                .find(DementiaMedications)
                .filter(
                    Q(
                        start_date__lte=end_datetime,
                        end_date__gte=start_datetime,
                        end_date__isnull=False,
                    )
                    | Q(start_date__lte=end_datetime, end_date__isnull=True)
                )
                .exists()
            )

            if has_dementia_meds:
                log.info(f"CMS130v14: Patient {patient.id} has dementia medications")
                return True

            return False
        except Exception as e:
            log.error(f"CMS130v14: Error checking advanced illness: {str(e)}")
            return False

    def _is_living_in_nursing_home(self, patient: Patient) -> bool:
        """
        Check if patient is living long term in a nursing home.
        
        Per CMS130v14: Assessment, Performed: "Housing status" result ~ "Lives in nursing home (finding)"
        Checks for housing status observation (LOINC 71802-3) with result "Lives in nursing home" (SNOMED 160734000)
        any time on or before the end of the measurement period.
        
        Note: This method is only called for patients age 66+.
        """
        try:
            # Per CMS130v14: Check for housing status assessment with result "Lives in nursing home"
            # The assessment must be on or before the end of the measurement period
            # TODO: check if this is correct!
            has_housing_status = (
                Observation.objects.for_patient(patient.id)
                .filter(
                    effective_datetime__lte=self.timeframe.end.datetime,
                    codings__code=HOUSING_STATUS_LOINC,
                    codings__system__in=LOINC_SYSTEM_IDENTIFIERS,
                    value_codings__code=LIVES_IN_NURSING_HOME_SNOMED,
                    value_codings__system__in=[
                        "SNOMED",
                        "SNOMEDCT",
                        "http://snomed.info/sct",
                    ],
                )
                .order_by("-effective_datetime")
                .first()
            )

            if has_housing_status:
                log.info(
                    f"CMS130v14: Patient {patient.id} age 66+ has housing status indicating nursing home"
                )
                self._not_applicable_reason = f"{patient.first_name} is living long term in a nursing home and is excluded from colorectal cancer screening."
                return True

            return False
        except Exception as e:
            log.error(f"CMS130v14: Error checking nursing home status: {str(e)}")
            return False

    def _has_palliative_care_in_period(self, patient: Patient) -> bool:
        """
        Check if the patient received palliative care during the measurement period.
        
        Per CMS130v14 CQL, checks for:
        - Palliative Care Assessment (LOINC 71007-9)
        - Palliative Care Diagnosis (ICD-10, SNOMED)
        - Palliative Care Encounter (CPT, HCPCS, SNOMED, ICD-10)
        - Palliative Care Intervention (SNOMED)
        """
        try:
            start_date = self.timeframe.start.datetime
            end_date = self.timeframe.end.datetime

            # Check palliative care diagnoses (using Condition model)
            has_palliative_diagnosis = (
                Condition.objects.for_patient(patient.id)
                .find(PalliativeCareDiagnosis)
                .active()
                .filter(entered_in_error_id__isnull=True)
                .exists()
            )

            if has_palliative_diagnosis:
                log.info(f"CMS130v14: Found palliative care diagnosis for patient {patient.id}")
                self._not_applicable_reason = f"{patient.first_name} is receiving palliative care and is excluded from colorectal cancer screening."
                return True

            # Check for Palliative Care Assessment (LOINC 71007-9)
            # Per CMS130v14: Assessment, Performed: "Functional Assessment of Chronic Illness Therapy - Palliative Care Questionnaire (FACIT-Pal)"
            has_palliative_assessment = self._observation_exists(
                patient=patient,
                codings_code="71007-9",
                value_codings_codes=set(),  # No specific value required for this assessment
                timeframe_start=self.timeframe.start.datetime,
                timeframe_end=self.timeframe.end.datetime,
            )

            if has_palliative_assessment:
                log.info(
                    f"CMS130v14: Found palliative care assessment (LOINC 71007-9) for patient {patient.id}"
                )
                self._not_applicable_reason = f"{patient.first_name} is receiving palliative care and is excluded from colorectal cancer screening."
                return True

            # Check palliative care encounters (using Encounter model)
            palliative_encounter_codes = self._get_value_set_codes(
                PalliativeCareEncounter, "SNOMEDCT", "ICD10CM"
            )

            if palliative_encounter_codes:
                has_palliative_encounter = Encounter.objects.filter(
                    note__patient=patient,
                    note__note_type_version__code__in=palliative_encounter_codes,
                    state__in=["CON", "STA"],
                    start_time__gte=start_date,
                    start_time__lte=end_date,
                ).exists()

                if has_palliative_encounter:
                    log.info(f"CMS130v14: Found palliative care encounter for patient {patient.id}")
                    self._not_applicable_reason = f"{patient.first_name} is receiving palliative care and is excluded from colorectal cancer screening."
                    return True

            # Check palliative care via claims (CPT, HCPCS, SNOMED codes)
            palliative_codes = (
                PalliativeCareEncounter.HCPCSLEVELII | PalliativeCareIntervention.SNOMEDCT
            )

            palliative_claims = ClaimLineItem.objects.filter(
                claim__note__patient=patient,
                status="active",
                from_date__gte=self.timeframe.start.date().isoformat(),
                from_date__lte=self.timeframe.end.date().isoformat(),
                proc_code__in=palliative_codes,
            )

            if palliative_claims.exists():
                first_claim = palliative_claims.first()
                if first_claim:
                    log.info(
                        f"CMS130v14: Found palliative care claim (code: {first_claim.proc_code}) for patient {patient.id}"
                    )
                self._not_applicable_reason = f"{patient.first_name} is receiving palliative care and is excluded from colorectal cancer screening."
                return True

            return False
        except Exception as e:
            log.error(f"CMS130v14: Error checking palliative care: {str(e)}")
            return False

    def _find_lab_report(
        self, patient: Patient, value_set_class, period_start: Any, period_end: Any
    ) -> LabReport | None:
        """Find a lab report matching a value set within the period."""
        try:
            value_set_codes = set()
            if hasattr(value_set_class, "LOINC"):
                value_set_codes.update(value_set_class.LOINC)

            if not value_set_codes:
                return None

            lab_reports = (
                LabReport.objects.filter(
                    patient__id=patient.id,
                    values__codings__code__in=value_set_codes,
                    original_date__gte=period_start.datetime,
                    original_date__lte=period_end.datetime,
                    junked=False,
                )
                .distinct()
                .order_by("-original_date")
            )

            if lab_reports.exists():
                return lab_reports.first()

            return None
        except Exception as e:
            log.error(f"CMS130v14: Error finding lab report: {str(e)}")
            return None

    def _find_imaging_report(
        self, patient: Patient, value_set_class, period_start: Any, period_end: Any
    ) -> ImagingReport | None:
        """Find an imaging report matching a value set within the period."""
        try:
            import arrow

            period_start_date = period_start.date() if hasattr(period_start, "date") else arrow.get(period_start).date()
            period_end_date = period_end.date() if hasattr(period_end, "date") else arrow.get(period_end).date()

            reports = (
                ImagingReport.objects.for_patient(patient.id)
                .filter(
                    original_date__gte=period_start_date,
                    original_date__lte=period_end_date,
                    junked=False,
                )
                .find(value_set_class)
                .order_by("-original_date")
            )

            if reports.exists():
                return reports.first()

            return None
        except Exception as e:
            log.error(f"CMS130v14: Error finding imaging report: {str(e)}")
            return None

    def _find_referral_report(
        self, patient: Patient, value_set_class, period_start: Any, period_end: Any
    ) -> ReferralReport | None:
        """Find a referral report matching a value set within the period."""
        try:
            import arrow

            period_start_date = period_start.date() if hasattr(period_start, "date") else arrow.get(period_start).date()
            period_end_date = period_end.date() if hasattr(period_end, "date") else arrow.get(period_end).date()

            reports = (
                ReferralReport.objects.for_patient(patient.id)
                .filter(
                    original_date__gte=period_start_date,
                    original_date__lte=period_end_date,
                    junked=False,
                )
                .find(value_set_class)
                .order_by("-original_date")
            )

            if reports.exists():
                return reports.first()

            return None
        except Exception as e:
            log.error(f"CMS130v14: Error finding referral report: {str(e)}")
            return None

    def _create_not_applicable_card(self, patient: Patient):
        """Create a NOT_APPLICABLE protocol card with appropriate narrative."""
        patient_id_str = str(patient.id) if patient.id else None
        
        # Use stored reason if available, otherwise use default
        narrative = self._not_applicable_reason or f"{patient.first_name} is not eligible for colorectal cancer screening."
        
        card = ProtocolCard(
            patient_id=patient_id_str,
            key="CMS130v14",
            title="Colorectal Cancer Screening",
            narrative=narrative,
            status=ProtocolCard.Status.NOT_APPLICABLE,
            due_in=-1,
            can_be_snoozed=True,
        )
        return card.apply()

    def _format_date_with_relative_time(self, exam_date) -> str:
        """Format date with relative time like '2 weeks ago on 10/31/25'."""
        import arrow

        now = arrow.get(self.timeframe.end.datetime)
        exam_arrow = exam_date if hasattr(exam_date, "format") else arrow.get(exam_date)

        days_diff = (now - exam_arrow).days

        if days_diff < 7:
            relative_time = f"{days_diff} day{'s' if days_diff != 1 else ''} ago"
        elif days_diff < 30:
            weeks = days_diff // 7
            relative_time = f"{weeks} week{'s' if weeks != 1 else ''} ago"
        elif days_diff < 365:
            months = days_diff // 30
            relative_time = f"{months} month{'s' if months != 1 else ''} ago"
        else:
            years = days_diff // 365
            relative_time = f"{years} year{'s' if years != 1 else ''} ago"

        date_formatted = exam_arrow.format("M/D/YY")
        return f"{relative_time} on {date_formatted}"

    def _create_satisfied_card(self, patient: Patient, last_exam: dict | None):
        """Create a SATISFIED protocol card."""
        import arrow

        patient_id_str = str(patient.id) if patient.id else None

        if last_exam and last_exam.get("date"):
            exam_date = arrow.get(last_exam["date"])
            date_with_relative = self._format_date_with_relative_time(exam_date)
            narrative = f"{patient.first_name} had a {last_exam.get('what', 'screening')} {date_with_relative}."

            if last_exam.get("days"):
                next_due_date = exam_date.shift(days=last_exam["days"])
                now = arrow.get(self.timeframe.end.datetime)
                due_in = (next_due_date - now).days
            else:
                due_in = -1
        else:
            narrative = f"{patient.first_name} has had appropriate colorectal cancer screening."
            due_in = -1

        card = ProtocolCard(
            patient_id=patient_id_str,
            key="CMS130v14",
            title="Colorectal Cancer Screening",
            narrative=narrative,
            status=ProtocolCard.Status.SATISFIED,
            due_in=due_in,
            can_be_snoozed=True,
        )
        return card.apply()

    def _recent_exam_context(self, patient: Patient) -> str:
        """Get context about the most recent exam of any type."""
        import arrow

        try:
            most_recent = None
            most_recent_date = None

            screening_checks = [
                ("Colonoscopy", Colonoscopy, SCREENING_LOOKBACK_YEARS["Colonoscopy"]),
                ("CT Colonography", CtColonography, SCREENING_LOOKBACK_YEARS["CT Colonography"]),
                ("Flexible sigmoidoscopy", FlexibleSigmoidoscopy, SCREENING_LOOKBACK_YEARS["Flexible sigmoidoscopy"]),
                ("FIT-DNA", SdnaFitTest, SCREENING_LOOKBACK_YEARS["FIT-DNA"]),
                ("FOBT", FecalOccultBloodTestFobt, SCREENING_LOOKBACK_YEARS["FOBT"]),
            ]

            for screening_name, value_set_class, years_back in screening_checks:
                period_start = self.timeframe.end.shift(years=-years_back)

                if value_set_class in (FecalOccultBloodTestFobt, SdnaFitTest):
                    report = self._find_lab_report(patient, value_set_class, period_start, self.timeframe.end)
                    if report and report.original_date:
                        date_arrow = arrow.get(report.original_date)
                        if most_recent_date is None or date_arrow > most_recent_date:
                            most_recent_date = date_arrow
                            most_recent = {"what": screening_name, "date": date_arrow}
                else:
                    for find_method in [self._find_imaging_report, self._find_referral_report]:
                        report = find_method(patient, value_set_class, period_start, self.timeframe.end)
                        if report and report.original_date:
                            date_arrow = arrow.get(report.original_date)
                            if most_recent_date is None or date_arrow > most_recent_date:
                                most_recent_date = date_arrow
                                most_recent = {"what": screening_name, "date": date_arrow}
                                break

            if most_recent:
                date_formatted = most_recent["date"].format("MMMM D, YYYY")
                return f"Last {most_recent['what']} done {date_formatted}."
            else:
                return "No relevant exams found."

        except Exception as e:
            log.error(f"CMS130v14: Error getting recent exam context: {str(e)}")
            return "No relevant exams found."

    def _friendly_time_duration(self, duration_in_days: int) -> str:
        """Convert duration in days to friendly format (e.g., '10 years', '2 months, 5 days')."""
        if duration_in_days < 1:
            return "invalid duration"

        if duration_in_days >= 365:
            years, days = divmod(duration_in_days, 365)
            plural = "s" if years > 1 else ""
            friendly_duration = f"{years} year{plural}"
            if days >= 30:
                months = days // 30
                plural = "s" if months > 1 else ""
                friendly_duration = f"{friendly_duration}, {months} month{plural}"
            return friendly_duration
        elif duration_in_days >= 30:
            months, days = divmod(duration_in_days, 30)
            plural = "s" if months > 1 else ""
            friendly_duration = f"{months} month{plural}"
            if days > 0:
                plural = "s" if days > 1 else ""
                friendly_duration = f"{friendly_duration}, {days} day{plural}"
            return friendly_duration
        else:
            return f"{duration_in_days} days"

    def _screening_interval_context(self) -> str:
        """Get screening interval context text (e.g., 'Current screening interval 9 years.')."""
        try:
            default_interval = getattr(self.Meta, "default_display_interval_in_days", 365 * 9)
            interval_text = self._friendly_time_duration(default_interval)
            return f"Current screening interval {interval_text}."
        except Exception as e:
            log.error(f"CMS130v14: Error getting screening interval context: {str(e)}")
            return ""

    def _create_due_card(self, patient: Patient):
        """Create a DUE protocol card with recommendations."""
        patient_id_str = str(patient.id) if patient.id else None

        narrative_parts = [
            f"{patient.first_name} is due for a Colorectal Cancer Screening.",
            self._recent_exam_context(patient),
            self._screening_interval_context(),
        ]
        narrative = "\n".join(narrative_parts)

        card = ProtocolCard(
            patient_id=patient_id_str,
            key="CMS130v14",
            title="Colorectal Cancer Screening",
            narrative=narrative,
            status=ProtocolCard.Status.DUE,
            due_in=-1,
            can_be_snoozed=True,
        )

        self._add_fobt_recommendation(card)
        self._add_fit_dna_recommendation(card)
        self._add_flexible_sigmoidoscopy_recommendation(card)
        self._add_ct_colonography_recommendation(card)
        self._add_colonoscopy_recommendation(card)

        return card.apply()

    def _add_recommendation_context(self, recommendation, specialties=None):
        """Add context to a recommendation with conditions and optional specialties."""
        context = SCREENING_CONTEXT.copy()
        if specialties:
            context["specialties"] = specialties

        if recommendation.context:
            recommendation.context.update(context)
        else:
            recommendation.context = context

    def _add_fobt_recommendation(self, card: ProtocolCard):
        """Add FOBT recommendation (Rank 1)."""
        fobt_codes = list(FecalOccultBloodTestFobt.LOINC)[:1] if hasattr(FecalOccultBloodTestFobt, "LOINC") else []
        if fobt_codes:
            command = LabOrderCommand(tests_order_codes=fobt_codes, diagnosis_codes=[SCREENING_DIAGNOSIS_CODE])
            recommendation = command.recommend(title="Order a FOBT", button="Order")
            self._add_recommendation_context(recommendation)
            card.recommendations.append(recommendation)

    def _add_fit_dna_recommendation(self, card: ProtocolCard):
        """Add FIT-DNA recommendation (Rank 2)."""
        fit_dna_codes = list(SdnaFitTest.LOINC)[:1] if hasattr(SdnaFitTest, "LOINC") else []
        if fit_dna_codes:
            command = LabOrderCommand(tests_order_codes=fit_dna_codes, diagnosis_codes=[SCREENING_DIAGNOSIS_CODE])
            recommendation = command.recommend(title="Order a FIT-DNA", button="Order")
            self._add_recommendation_context(recommendation)
            card.recommendations.append(recommendation)

    def _add_flexible_sigmoidoscopy_recommendation(self, card: ProtocolCard):
        """Add Flexible Sigmoidoscopy recommendation (Rank 3)."""
        command = ReferCommand(
            service_provider=ServiceProvider(
                first_name="Referral",
                last_name="Gastroenterology",
                specialty="Gastroenterology",
                practice_name="Gastroenterology Referral Network",
                notes="For flexible sigmoidoscopy screening.",
            ),
            diagnosis_codes=[SCREENING_DIAGNOSIS_CODE],
            include_visit_note=False,
        )
        recommendation = command.recommend(title="Order a Flexible sigmoidoscopy", button="Order")
        self._add_recommendation_context(recommendation, specialties=["Gastroenterology"])
        card.recommendations.append(recommendation)

    def _add_ct_colonography_recommendation(self, card: ProtocolCard):
        """Add CT Colonography recommendation (Rank 4)."""
        ct_cpt_codes = list(CtColonography.CPT)[:1] if hasattr(CtColonography, "CPT") else []
        if ct_cpt_codes:
            command = ImagingOrderCommand(image_code=ct_cpt_codes[0], diagnosis_codes=[SCREENING_DIAGNOSIS_CODE])
            recommendation = command.recommend(title="Order a CT Colonography", button="Order")
            self._add_recommendation_context(recommendation, specialties=["Radiology"])
            card.recommendations.append(recommendation)

    def _add_colonoscopy_recommendation(self, card: ProtocolCard):
        """Add Colonoscopy recommendation (Rank 5)."""
        command = ReferCommand(
            service_provider=ServiceProvider(
                first_name="Referral",
                last_name="Gastroenterology",
                specialty="Gastroenterology",
                practice_name="Gastroenterology Referral Network",
                notes="For colonoscopy screening.",
            ),
            diagnosis_codes=[SCREENING_DIAGNOSIS_CODE],
            include_visit_note=False,
        )
        recommendation = command.recommend(title="Order a Colonoscopy", button="Order")
        self._add_recommendation_context(recommendation, specialties=["Gastroenterology"])
        card.recommendations.append(recommendation)

    def _normalize_system(self, system: str) -> str:
        """Normalize coding system name for comparison."""
        if not system:
            return ""
        normalized = system.replace("-", "").upper()
        if "SNOMED" in normalized or "SCT" in normalized:
            return "SNOMEDCT"
        return normalized

    def _coding_in_value_set_for_note_type(self, note_type: NoteType, value_set_classes) -> bool:
        """Check if a NoteType coding belongs to any of the provided value sets."""
        try:
            normalized_system = self._normalize_system(note_type.system)
            normalized_code = note_type.code.replace(".", "") if note_type.code else ""

            for value_set_class in value_set_classes:
                if normalized_system in ["ICD10", "ICD10CM"]:
                    codes = getattr(value_set_class, "ICD10CM", set())
                    codes_normalized = {code.replace(".", "") for code in codes}
                    if normalized_code in codes_normalized:
                        return True
                elif normalized_system in ["SNOMEDCT", "SNOMED"]:
                    codes = getattr(value_set_class, "SNOMEDCT", set())
                    if note_type.code in codes:
                        return True
                elif normalized_system == "CPT":
                    codes = getattr(value_set_class, "CPT", set())
                    if note_type.code in codes:
                        return True
                elif normalized_system == "HCPCS":
                    codes = getattr(value_set_class, "HCPCS", set())
                    if note_type.code in codes:
                        return True

            return False
        except Exception as e:
            log.error(f"CMS130v14: Error checking note type coding in value set: {str(e)}")
            return False


# Alias for backward compatibility
Protocol = CMS130v14ColorectalCancerScreening

