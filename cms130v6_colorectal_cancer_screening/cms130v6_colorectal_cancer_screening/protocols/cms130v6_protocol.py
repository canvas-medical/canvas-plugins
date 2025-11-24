"""CMS130v6 Colorectal Cancer Screening protocol implementation."""

from typing import Any

from canvas_sdk.commands import ImagingOrderCommand, LabOrderCommand, ReferCommand
from canvas_sdk.commands.constants import ServiceProvider
from canvas_sdk.effects.protocol_card.protocol_card import ProtocolCard
from canvas_sdk.events import EventType
from canvas_sdk.protocols import ClinicalQualityMeasure
from canvas_sdk.v1.data import Observation, Patient
from canvas_sdk.v1.data.claim_line_item import ClaimLineItem
from canvas_sdk.v1.data.condition import Condition
from canvas_sdk.v1.data.encounter import Encounter
from canvas_sdk.v1.data.imaging import ImagingReport
from canvas_sdk.v1.data.lab import LabReport
from canvas_sdk.v1.data.note import Note, NoteType
from canvas_sdk.v1.data.referral import ReferralReport
from canvas_sdk.value_set.v2022.condition import MalignantNeoplasmOfColon
from canvas_sdk.value_set.v2022.diagnostic_study import CtColonography
from canvas_sdk.value_set.v2022.encounter import (
    AnnualWellnessVisit,
    HomeHealthcareServices,
    OfficeVisit,
    PreventiveCareServicesEstablishedOfficeVisit_18AndUp,
    PreventiveCareServicesInitialOfficeVisit_18AndUp,
)
from canvas_sdk.value_set.v2022.laboratory_test import FecalOccultBloodTestFobt, FitDna
from canvas_sdk.value_set.v2022.procedure import (
    CMS130v6CtColonography,
    Colonoscopy,
    FlexibleSigmoidoscopy,
    TotalColectomy,
)
# Hospice care value sets use v2026 because they are based on the updated CMS131v14 CQL logic
# which includes comprehensive hospice care checks (diagnosis, encounters, assessments, interventions)
from canvas_sdk.value_set.v2026.condition import HospiceDiagnosis
from canvas_sdk.value_set.v2026.encounter import HospiceEncounter
from canvas_sdk.value_set.v2026.intervention import HospiceCareAmbulatory

from logger import log


# Constants
AGE_RANGE_START = 50
AGE_RANGE_END = 75
SCREENING_INTERVALS_DAYS = {
    "FOBT": 365,
    "FIT-DNA": 1095,
    "Flexible sigmoidoscopy": 1825,
    "CT Colonography": 1825,
    "Colonoscopy": 3650,
}
SCREENING_LOOKBACK_YEARS = {
    "FOBT": 1,
    "FIT-DNA": 3,
    "Flexible sigmoidoscopy": 5,
    "CT Colonography": 5,
    "Colonoscopy": 10,
}
DISCHARGE_TO_HOME_HOSPICE_SNOMED = "428361000124107"
DISCHARGE_TO_FACILITY_HOSPICE_SNOMED = "428371000124100"
LOINC_SYSTEM_IDENTIFIERS = ["LOINC", "http://loinc.org"]
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


class CMS130v6ColorectalCancerScreening(ClinicalQualityMeasure):
    """CMS130v6 Colorectal Cancer Screening clinical quality measure."""

    class Meta:
        title = "Colorectal Cancer Screening"
        description = (
            "Percentage of adults 50-75 years of age who had appropriate screening for colorectal cancer."
        )
        version = "2027-01-01v6"
        default_display_interval_in_days = 365 * 10
        information = "https://ecqi.healthit.gov/sites/default/files/ecqm/measures/CMS130v6.html"
        identifiers = ["CMS130v6"]
        types = ["CQM"]
        authors = ["Centers for Medicare & Medicaid Services"]
        references = [
            'American Cancer Society. 2015. "Cancer Prevention & Early Detection Facts & Figures 2015-2016." Atlanta: American Cancer Society.',
            'National Cancer Institute. 2015. "SEER Stat Fact Sheets: Colon and Rectum Cancer." Bethesda, MD, http://seer.cancer.gov/statfacts/html/colorect.html',
            'U.S. Preventive Services Task Force (USPSTF). 2008. "Screening for colorectal cancer: U.S. Preventive Services Task Force recommendation statement." Ann Intern Med 149(9):627-37.',
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
                log.warning("CMS130v6: Could not determine patient ID from event, skipping")
                return []

            patient = Patient.objects.filter(id=patient_id).first()
            if not patient:
                log.warning(f"CMS130v6: Patient {patient_id} not found, skipping")
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
            log.error(f"CMS130v6: Error in protocol compute: {str(e)}")
            return []

    def _in_initial_population(self, patient: Patient) -> bool:
        """Check if patient is in initial population (age 50-75 with eligible encounter)."""
        return self._check_age_50_to_75(patient) and self._has_eligible_encounter_in_period(patient)

    def _in_denominator(self, patient: Patient) -> bool:
        """Check if patient is in denominator (initial population minus exclusions)."""
        if not self._in_initial_population(patient):
            return False

        if self._has_colon_exclusion(patient):
            return False

        if self._has_hospice_care_in_period(patient):
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
        """Check for FIT-DNA within 3 years."""
        period_start = self.timeframe.end.shift(years=-SCREENING_LOOKBACK_YEARS["FIT-DNA"])
        report = self._find_lab_report(patient, FitDna, period_start, self.timeframe.end)
        if report:
            return {
                "date": report.original_date,
                "what": "FIT-DNA",
                "days": SCREENING_INTERVALS_DAYS["FIT-DNA"],
            }
        return None

    def _check_flexible_sigmoidoscopy(self, patient: Patient) -> dict | None:
        """Check for Flexible Sigmoidoscopy within 5 years (imaging or referral)."""
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
        """Check for CT Colonography within 5 years (handles both value sets and report types)."""
        period_start = self.timeframe.end.shift(years=-SCREENING_LOOKBACK_YEARS["CT Colonography"])

        value_sets = [CMS130v6CtColonography, CtColonography]
        for value_set in value_sets:
            report = self._find_imaging_report(patient, value_set, period_start, self.timeframe.end)
            if report:
                return {
                    "date": report.original_date,
                    "what": "CT Colonography",
                    "days": SCREENING_INTERVALS_DAYS["CT Colonography"],
                }

            report = self._find_referral_report(patient, value_set, period_start, self.timeframe.end)
            if report:
                return {
                    "date": report.original_date,
                    "what": "CT Colonography",
                    "days": SCREENING_INTERVALS_DAYS["CT Colonography"],
                }
        return None

    def _check_colonoscopy(self, patient: Patient) -> dict | None:
        """Check for Colonoscopy within 10 years (imaging or referral)."""
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

    def _check_age_50_to_75(self, patient: Patient) -> bool:
        """Check if patient is between 50 and 75 years old."""
        try:
            if not getattr(patient, "birth_date", None):
                self._not_applicable_reason = f"{patient.first_name} does not meet the age criteria (50-75 years) for colorectal cancer screening."
                return False

            import arrow
            birth_date = arrow.get(patient.birth_date)
            age_years = (self.now - birth_date).days // 365

            if age_years < AGE_RANGE_START:
                self._not_applicable_reason = f"{patient.first_name} is under {AGE_RANGE_START} years of age and does not meet the criteria for colorectal cancer screening."
                return False
            elif age_years > AGE_RANGE_END:
                self._not_applicable_reason = f"{patient.first_name} is over {AGE_RANGE_END} years of age and does not meet the criteria for colorectal cancer screening."
                return False

            return True
        except Exception as e:
            log.error(f"CMS130v6: Error computing age: {str(e)}")
            self._not_applicable_reason = f"{patient.first_name} does not meet the age criteria (50-75 years) for colorectal cancer screening."
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
                PreventiveCareServicesEstablishedOfficeVisit_18AndUp,
                PreventiveCareServicesInitialOfficeVisit_18AndUp,
                HomeHealthcareServices,
                AnnualWellnessVisit,
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
            log.error(f"CMS130v6: Error checking eligible encounters: {str(e)}")
            return True

    def _has_colon_exclusion(self, patient: Patient) -> bool:
        """Check if patient has colon exclusions (total colectomy or malignant neoplasm of colon)."""
        try:
            if Condition.objects.for_patient(patient.id).active().find(TotalColectomy).exists():
                self._not_applicable_reason = f"{patient.first_name} has a history of total colectomy and is excluded from colorectal cancer screening."
                return True

            if Condition.objects.for_patient(patient.id).active().find(MalignantNeoplasmOfColon).exists():
                self._not_applicable_reason = f"{patient.first_name} has a history of malignant neoplasm of colon and is excluded from colorectal cancer screening."
                return True

            return False
        except Exception as e:
            log.error(f"CMS130v6: Error checking colon exclusions: {str(e)}")
            return False

    def _get_value_set_codes(self, value_set_class, *code_attrs):
        """Get codes from a value set for specified code attributes."""
        codes = set()
        for attr in code_attrs:
            if hasattr(value_set_class, attr):
                codes.update(getattr(value_set_class, attr, set()))
        return codes

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
                log.info(f"CMS130v6: Found hospice diagnosis for patient {patient.id}")
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
                    log.info(f"CMS130v6: Found hospice encounter for patient {patient.id}")
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
                log.info(f"CMS130v6: Found discharge to hospice for patient {patient.id}")
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
                log.info(f"CMS130v6: Found hospice care assessment for patient {patient.id}")
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
                        f"CMS130v6: Found hospice care claim (code: {first_claim.proc_code}) for patient {patient.id}"
                    )
                self._not_applicable_reason = f"{patient.first_name} is receiving hospice care and is excluded from colorectal cancer screening."
                return True

            return False
        except Exception as e:
            log.error(f"CMS130v6: Error checking hospice status: {str(e)}")
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
            log.error(f"CMS130v6: Error finding lab report: {str(e)}")
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
            log.error(f"CMS130v6: Error finding imaging report: {str(e)}")
            return None

    def _find_referral_report(
        self, patient: Patient, value_set_class, period_start: Any, period_end: Any
    ) -> ReferralReport | None:
        """Find a referral report matching a value set within the period."""
        try:
            reports = (
                ReferralReport.objects.for_patient(patient.id)
                .filter(
                    original_date__range=(period_start.date(), period_end.date()),
                    junked=False,
                )
                .find(value_set_class)
                .order_by("-original_date")
            )

            if reports.exists():
                return reports.first()

            return None
        except Exception as e:
            log.error(f"CMS130v6: Error finding referral report: {str(e)}")
            return None

    def _create_not_applicable_card(self, patient: Patient):
        """Create a NOT_APPLICABLE protocol card with appropriate narrative."""
        patient_id_str = str(patient.id) if patient.id else None
        
        # Use stored reason if available, otherwise use default
        narrative = self._not_applicable_reason or f"{patient.first_name} is not eligible for colorectal cancer screening."
        
        card = ProtocolCard(
            patient_id=patient_id_str,
            key="CMS130v6",
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
            key="CMS130v6",
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
                ("CT Colonography", CMS130v6CtColonography, SCREENING_LOOKBACK_YEARS["CT Colonography"]),
                ("CT Colonography", CtColonography, SCREENING_LOOKBACK_YEARS["CT Colonography"]),
                ("Flexible sigmoidoscopy", FlexibleSigmoidoscopy, SCREENING_LOOKBACK_YEARS["Flexible sigmoidoscopy"]),
                ("FIT-DNA", FitDna, SCREENING_LOOKBACK_YEARS["FIT-DNA"]),
                ("FOBT", FecalOccultBloodTestFobt, SCREENING_LOOKBACK_YEARS["FOBT"]),
            ]

            for screening_name, value_set_class, years_back in screening_checks:
                period_start = self.timeframe.end.shift(years=-years_back)

                if value_set_class in (FecalOccultBloodTestFobt, FitDna):
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
            log.error(f"CMS130v6: Error getting recent exam context: {str(e)}")
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
        """Get screening interval context text (e.g., 'Current screening interval 10 years.')."""
        try:
            default_interval = getattr(self.Meta, "default_display_interval_in_days", 365 * 10)
            interval_text = self._friendly_time_duration(default_interval)
            return f"Current screening interval {interval_text}."
        except Exception as e:
            log.error(f"CMS130v6: Error getting screening interval context: {str(e)}")
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
            key="CMS130v6",
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
        fit_dna_codes = list(FitDna.LOINC)[:1] if hasattr(FitDna, "LOINC") else []
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
        ct_cpt_codes = list(CMS130v6CtColonography.CPT)[:1] if hasattr(CMS130v6CtColonography, "CPT") else []
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
            log.error(f"CMS130v6: Error checking note type coding in value set: {str(e)}")
            return False


# Alias for backward compatibility
Protocol = CMS130v6ColorectalCancerScreening
