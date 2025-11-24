from typing import Any

from django.db.models import Q

from canvas_sdk.commands import LabOrderCommand, ImagingOrderCommand, ReferCommand
from canvas_sdk.commands.constants import ServiceProvider
from canvas_sdk.effects import Effect
from canvas_sdk.effects.protocol_card.protocol_card import ProtocolCard
from canvas_sdk.events import EventType
from canvas_sdk.protocols import ClinicalQualityMeasure
from canvas_sdk.v1.data import Patient, InterviewQuestionResponse, Interview, Observation
from canvas_sdk.v1.data.appointment import Appointment
from canvas_sdk.v1.data.condition import Condition, ConditionCoding
from canvas_sdk.v1.data.imaging import ImagingReport
from canvas_sdk.v1.data.lab import LabReport
from canvas_sdk.v1.data.note import Note, NoteType, PracticeLocationPOS
from canvas_sdk.v1.data.referral import ReferralReport
# Import from v2022 (existing value sets)
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
from canvas_sdk.value_set.v2022.procedure import Colonoscopy, FlexibleSigmoidoscopy, TotalColectomy, CMS130v6CtColonography

from logger import log

class CMS130v6ColorectalCancerScreening(ClinicalQualityMeasure):
    class Meta:
        title = "Colorectal Cancer Screening"
        description = (
            "Percentage of adults 50-75 years of age who had appropriate screening for colorectal cancer."
        )
        version = "2027-01-01v6"
        default_display_interval_in_days = 365 * 10  # 10 years (matches legacy)
        information = "https://ecqi.healthit.gov/sites/default/files/ecqm/measures/CMS130v6.html"
        identifiers = ["CMS130v6"]
        types = ["CQM"]
        authors = ["Centers for Medicare & Medicaid Services"]
        references = [
            # "https://ecqi.healthit.gov/sites/default/files/ecqm/measures/CMS130v6.html",
            'American Cancer Society. 2015. "Cancer Prevention & Early Detection Facts & Figures 2015-2016." Atlanta: American Cancer Society.',
            'National Cancer Institute. 2015. "SEER Stat Fact Sheets: Colon and Rectum Cancer." Bethesda, MD, http://seer.cancer.gov/statfacts/html/colorect.html',
            'U.S. Preventive Services Task Force (USPSTF). 2008. "Screening for colorectal cancer: U.S. Preventive Services Task Force recommendation statement." Ann Intern Med 149(9):627-37.',
        ]

    RESPONDS_TO = [
        EventType.Name(EventType.CONDITION_CREATED),
        EventType.Name(EventType.CONDITION_UPDATED),
        # EventType.Name(EventType.LAB_REPORT_CREATED),
        # EventType.Name(EventType.LAB_REPORT_UPDATED),
        # EventType.Name(EventType.IMAGING_REPORT_CREATED),
        # EventType.Name(EventType.IMAGING_REPORT_UPDATED),
        # EventType.Name(EventType.REFERRAL_REPORT_CREATED),
        # EventType.Name(EventType.REFERRAL_REPORT_UPDATED),
        EventType.Name(EventType.PATIENT_CREATED),
        EventType.Name(EventType.PATIENT_UPDATED),
        # EventType.Name(EventType.PROTOCOL_OVERRIDE_CREATED),
        # EventType.Name(EventType.PROTOCOL_OVERRIDE_UPDATED),
        EventType.Name(EventType.OBSERVATION_CREATED),
        EventType.Name(EventType.OBSERVATION_UPDATED),
    ]

    # Age range constants
    AGE_RANGE_START = 50
    AGE_RANGE_END = 75
    
    # Track last exam found (priority-based, matches old implementation)
    _last_exam = None

    def _first_due_in(self, patient: Patient) -> int | None:
        """
        Calculate when a patient will first be due (when they turn 50).
        Returns days until first due date, or None if already in age range or has exclusion.
        """
        try:
            import arrow
            patient_age = int(patient.age_at(self.timeframe.end))
            
            # Only calculate if patient is under age range start and doesn't have exclusion
            if patient_age < self.AGE_RANGE_START and not self._has_colon_exclusion(patient):
                # Calculate birthday at age 50
                birthday_at_50 = arrow.get(patient.birthday).shift(years=self.AGE_RANGE_START)
                # Calculate days until that date
                days_until_due = (birthday_at_50 - arrow.get(self.timeframe.end.datetime)).days
                return days_until_due
            
            return None
        except Exception as e:
            log.error(f"CMS130v6: Error calculating first_due_in: {str(e)}")
            return None

    def _get_patient(self) -> tuple[Patient | None, Condition | None]:
        try:
            target_id = self.event.target.id

            if self.event.type in [
                EventType.CONDITION_CREATED,
                EventType.CONDITION_UPDATED,
            ]:
                condition = Condition.objects.filter(id=target_id).select_related("patient").first()
                if condition and condition.patient:
                    return condition.patient, condition
                log.warning(f"CMS130v6: Could not find patient for condition {target_id}")
                return None, None

            log.warning(f"CMS130v6: Unhandled event type {self.event.type}")

            # Fallback: get patient ID and query patient
            patient_id = self.patient_id_from_target()
            if patient_id:
                return Patient.objects.filter(id=patient_id).first(), None
            return None, None

        except Exception as e:
            log.error(f"CMS130v6: Error getting patient: {str(e)}")
            return None, None

    def compute(self) -> list[Effect]:
        try:
            # patient_id = self._get_patient_id()
            patient_id = self.context.get("patient", {}).get("id")
            if not patient_id:
                log.warning("CMS130v6: Could not determine patient ID from event, skipping")
                return []

            patient = Patient.objects.filter(id=patient_id).first()
            if not patient:
                log.warning(f"CMS130v6: Patient {patient_id} not found, skipping")
                return []
            log.info("CMS130v6: starting in_initial_population")
            if not self._in_initial_population(patient):
                log.info(f"CMS130v6: Patient {patient_id} not in initial population")
                return [self._create_not_applicable_card(patient)]
            log.info("CMS130v6: starting in_denominator")
            if not self._in_denominator(patient):
                log.info(f"CMS130v6: Patient {patient_id} excluded from denominator")
                return [self._create_not_applicable_card(patient)]
            log.info("CMS130v6: starting in_numerator")
            if self._in_numerator(patient):
                log.info(f"CMS130v6: Patient {patient_id} meets numerator criteria")
                return [self._create_satisfied_card(patient, self._last_exam)]
            else:
                log.info(f"CMS130v6: Patient {patient_id} does not meet numerator criteria")
                return [self._create_due_card(patient)]

        except Exception as e:
            log.error(f"CMS130v6: Error in protocol compute: {str(e)}")
            return []

    def _in_initial_population(self, patient: Patient) -> bool:
        if not self._check_age_50_to_75(patient):
            return False

        if not self._has_eligible_encounter_in_period(patient):
            return False

        return True

    def _in_denominator(self, patient: Patient) -> bool:
        if not self._in_initial_population(patient):
            return False

        if self._has_colon_exclusion(patient):
            log.info(f"CMS130v6: Patient {patient.id} has colon exclusion")
            return False

        if self._has_hospice_care_in_period(patient):
            log.info(f"CMS130v6: Patient {patient.id} in hospice care")
            return False

        return True

    def _in_numerator(self, patient: Patient) -> bool:
        """
        Check if patient has had appropriate screening.
        
        Matches old behavior: checks screening types in priority order and sets _last_exam
        when found, returning immediately. Priority order:
        1. FOBT
        2. FIT-DNA
        3. Flexible Sigmoidoscopy
        4. CT Colonography
        5. Colonoscopy
        """
        self._last_exam = None
        
        # Screening intervals in days
        SCREENING_INTERVALS = {
            "FOBT": 365,  # 1 year
            "FIT-DNA": 1095,  # 3 years
            "Flexible sigmoidoscopy": 1825,  # 5 years
            "CT Colonography": 1825,  # 5 years
            "Colonoscopy": 3650,  # 10 years
        }
        
        # Check all screening types with appropriate lookback periods
        # FOBT: within measurement period (priority 1)
        fobt_period_start = self.timeframe.end.shift(years=-1)
        fobt_report = self._find_lab_report(patient, FecalOccultBloodTestFobt, fobt_period_start, self.timeframe.end)
        if fobt_report:
            log.info(f"CMS130v6: Found FOBT report {fobt_report.id}, patient meets numerator")
            self._last_exam = {
                "date": fobt_report.original_date,
                "what": "FOBT",
                "days": SCREENING_INTERVALS["FOBT"],
            }
            return True

        # FIT-DNA: within 3 years prior (priority 2)
        fit_dna_period_start = self.timeframe.end.shift(years=-3)
        fit_dna_report = self._find_lab_report(patient, FitDna, fit_dna_period_start, self.timeframe.end)
        if fit_dna_report:
            log.info(f"CMS130v6: Found FIT-DNA report {fit_dna_report.id}, patient meets numerator")
            self._last_exam = {
                "date": fit_dna_report.original_date,
                "what": "FIT-DNA",
                "days": SCREENING_INTERVALS["FIT-DNA"],
            }
            return True

        # Flexible Sigmoidoscopy: within 5 years prior (priority 3)
        sigmoid_period_start = self.timeframe.end.shift(years=-5)
        log.info(f"CMS130v6: Checking Flexible Sigmoidoscopy - period: {sigmoid_period_start.datetime} to {self.timeframe.end.datetime}")
        sigmoid_imaging = self._find_imaging_report(patient, FlexibleSigmoidoscopy, sigmoid_period_start, self.timeframe.end)
        if sigmoid_imaging:
            log.info(f"CMS130v6: Found Flexible Sigmoidoscopy report {sigmoid_imaging.id}, original_date={sigmoid_imaging.original_date}, patient meets numerator")
            self._last_exam = {
                "date": sigmoid_imaging.original_date,
                "what": "Flexible sigmoidoscopy",
                "days": SCREENING_INTERVALS["Flexible sigmoidoscopy"],
            }
            return True
        sigmoid_referral = self._find_referral_report(patient, FlexibleSigmoidoscopy, sigmoid_period_start, self.timeframe.end)
        if sigmoid_referral:
            log.info(f"CMS130v6: Found Flexible Sigmoidoscopy referral {sigmoid_referral.id}, patient meets numerator")
            self._last_exam = {
                "date": sigmoid_referral.original_date,
                "what": "Flexible sigmoidoscopy",
                "days": SCREENING_INTERVALS["Flexible sigmoidoscopy"],
            }
            return True

        # CT Colonography: within 5 years prior (priority 4)
        ct_period_start = self.timeframe.end.shift(years=-5)
        ct_imaging = self._find_imaging_report(patient, CtColonography, ct_period_start, self.timeframe.end)
        if ct_imaging:
            log.info(f"CMS130v6: Found CT Colonography report {ct_imaging.id}, patient meets numerator")
            self._last_exam = {
                "date": ct_imaging.original_date,
                "what": "CT Colonography",
                "days": SCREENING_INTERVALS["CT Colonography"],
            }
            return True
        ct_imaging_v6 = self._find_imaging_report(patient, CMS130v6CtColonography, ct_period_start, self.timeframe.end)
        if ct_imaging_v6:
            log.info(f"CMS130v6: Found CT Colonography report {ct_imaging_v6.id}, patient meets numerator")
            self._last_exam = {
                "date": ct_imaging_v6.original_date,
                "what": "CT Colonography",
                "days": SCREENING_INTERVALS["CT Colonography"],
            }
            return True
        ct_referral = self._find_referral_report(patient, CtColonography, ct_period_start, self.timeframe.end)
        if ct_referral:
            log.info(f"CMS130v6: Found CT Colonography referral {ct_referral.id}, patient meets numerator")
            self._last_exam = {
                "date": ct_referral.original_date,
                "what": "CT Colonography",
                "days": SCREENING_INTERVALS["CT Colonography"],
            }
            return True
        ct_referral_v6 = self._find_referral_report(patient, CMS130v6CtColonography, ct_period_start, self.timeframe.end)
        if ct_referral_v6:
            log.info(f"CMS130v6: Found CT Colonography referral {ct_referral_v6.id}, patient meets numerator")
            self._last_exam = {
                "date": ct_referral_v6.original_date,
                "what": "CT Colonography",
                "days": SCREENING_INTERVALS["CT Colonography"],
            }
            return True

        # Colonoscopy: within 10 years prior (priority 5)
        colon_period_start = self.timeframe.end.shift(years=-10)
        colon_imaging = self._find_imaging_report(patient, Colonoscopy, colon_period_start, self.timeframe.end)
        if colon_imaging:
            log.info(f"CMS130v6: Found Colonoscopy report {colon_imaging.id}, patient meets numerator")
            self._last_exam = {
                "date": colon_imaging.original_date,
                "what": "Colonoscopy",
                "days": SCREENING_INTERVALS["Colonoscopy"],
            }
            return True
        colon_referral = self._find_referral_report(patient, Colonoscopy, colon_period_start, self.timeframe.end)
        if colon_referral:
            log.info(f"CMS130v6: Found Colonoscopy referral {colon_referral.id}, patient meets numerator")
            self._last_exam = {
                "date": colon_referral.original_date,
                "what": "Colonoscopy",
                "days": SCREENING_INTERVALS["Colonoscopy"],
            }
            return True

        return False

    def _check_age_50_to_75(self, patient: Patient) -> bool:
        try:
            if not getattr(patient, "birth_date", None):
                return False

            import arrow
            birth_date = arrow.get(patient.birth_date)
            age_years = (self.now - birth_date).days // 365

            return self.AGE_RANGE_START <= age_years <= self.AGE_RANGE_END
        except Exception as e:
            log.error(f"CMS130v6: Error computing age: {str(e)}")
            return False

    def _has_eligible_encounter_in_period(self, patient: Patient) -> bool:
        try:
            # Check for notes with eligible visit types within measurement period
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

                note_type = note.note_type_version
                for value_set_class in visit_value_sets:
                    if self._coding_in_value_set_for_note_type(note_type, value_set_class):
                        return True

            # If no matches found, return True for now (similar to CMS131v14)
            # This can be refined later when NoteType coding structure is better understood
            return True
        except Exception as e:
            log.error(f"CMS130v6: Error checking eligible encounters: {str(e)}")
            return True

    def _has_colon_exclusion(self, patient: Patient) -> bool:
        """
        Check if patient has colon exclusions (total colectomy or malignant neoplasm of colon).
        
        Uses the .find() pattern to match conditions against value sets, similar to CMS131v14.
        """
        try:
            # Check for TotalColectomy conditions
            has_total_colectomy = (
                Condition.objects.for_patient(patient.id)
                .active()
                .find(TotalColectomy)
                .exists()
            )
            
            if has_total_colectomy:
                log.info(f"CMS130v6: Found TotalColectomy exclusion for patient {patient.id}")
                return True
            
            # Check for MalignantNeoplasmOfColon conditions
            has_malignant_neoplasm = (
                Condition.objects.for_patient(patient.id)
                .active()
                .find(MalignantNeoplasmOfColon)
                .exists()
            )
            
            if has_malignant_neoplasm:
                log.info(f"CMS130v6: Found MalignantNeoplasmOfColon exclusion for patient {patient.id}")
                return True
            
            return False
        except Exception as e:
            log.error(f"CMS130v6: Error checking colon exclusions: {str(e)}")
            return False

    def _has_hospice_care_in_period(self, patient: Patient) -> bool:
        """
        Check if patient is in hospice care during the measurement period.

        Checks for:
        1. Notes with place of service = Hospice (code "34")
        2. Observations with SNOMED codes indicating hospice care:
           - Discharge to home for Hospice (SNOMED 428361000124107)
           - Discharge to Health Care Facility For Hospice Care (SNOMED 428371000124100)
           - Hospice Ambulatory Care (SNOMED 385765002)
        """
        try:
            # Check for notes with hospice place of service during measurement period
            has_hospice_note = Note.objects.filter(
                patient__id=patient.id,
                datetime_of_service__range=(
                    self.timeframe.start.datetime,
                    self.timeframe.end.datetime,
                ),
                place_of_service=PracticeLocationPOS.HOSPICE,
            ).exists()

            if has_hospice_note:
                log.info(f"CMS130v6: Found hospice note for patient {patient.id}")
                return True

            # SNOMED codes for hospice care
            hospice_codes = {"428361000124107", "428371000124100", "385765002"}

            # Check for observations with hospice SNOMED codes as values during measurement period
            has_hospice_observation = Observation.objects.for_patient(patient.id).filter(
                Q(effective_datetime__isnull=True) |
                Q(effective_datetime__gte=self.timeframe.start.datetime,
                  effective_datetime__lte=self.timeframe.end.datetime),
                value_codings__code__in=hospice_codes,
                value_codings__system__in=["SNOMED", "SNOMEDCT", "http://snomed.info/sct"]
            ).exists()

            if has_hospice_observation:
                log.info(f"CMS130v6: Found hospice care observation for patient {patient.id}")
                return True

            return False
        except Exception as e:
            log.error(f"CMS130v6: Error checking hospice status: {str(e)}")
            return False


    def _find_lab_report(
        self, patient: Patient, value_set_class, period_start: Any, period_end: Any
    ) -> LabReport | None:
        """
        Find a lab report matching a value set.
        
        This matches the legacy behavior:
        patient.lab_reports.find(ValueSet).within(period).last()
        
        NOTE: Uses 'codings' not 'loinc_codes' - this is the plugin service
        relationship name (LabValueCoding has related_name='codings').
        """
        try:
            # Get value set codes (LOINC codes for lab tests)
            value_set_codes = set()
            if hasattr(value_set_class, "LOINC"):
                value_set_codes.update(value_set_class.LOINC)

            if not value_set_codes:
                return None

            # This matches the legacy behavior: patient.lab_reports.find(ValueSet).within(period).last()
            # Plugin service uses 'codings' not 'loinc_codes' (LabValueCoding has related_name='codings')
            # Use .distinct() to avoid duplicate LabReports when a report has multiple LabValues with matching codes
            # This matches the behavior of ImagingReportQuerySet.find() and ReferralReportQuerySet.find()
            lab_reports = LabReport.objects.filter(
                patient__id=patient.id,
                values__codings__code__in=value_set_codes,  # Plugin service uses 'codings', not 'loinc_codes'
                original_date__gte=period_start.datetime,
                original_date__lte=period_end.datetime,
                junked=False,
            ).distinct().order_by("-original_date")

            log.info(f"LAB REPORTS: Found {len(lab_reports)} distinct lab reports")

            if lab_reports.exists():
                return lab_reports.first()

            return None
        except Exception as e:
            log.error(f"CMS130v6: Error finding lab report: {str(e)}")
            return None

    def _find_imaging_report(
        self, patient: Patient, value_set_class, period_start: Any, period_end: Any
    ) -> ImagingReport | None:
        try:
            import arrow
            
            # Convert period_start and period_end to datetime for comparison
            # Handle both arrow objects and datetime objects
            if hasattr(period_start, 'datetime'):
                period_start_dt = period_start.datetime
            elif hasattr(period_start, 'date'):
                # If it's a date, convert to datetime at start of day
                period_start_dt = arrow.get(period_start.date()).datetime if hasattr(period_start, 'date') else arrow.get(period_start).datetime
            else:
                period_start_dt = arrow.get(period_start).datetime
            
            if hasattr(period_end, 'datetime'):
                period_end_dt = period_end.datetime
            elif hasattr(period_end, 'date'):
                # If it's a date, convert to datetime at end of day
                period_end_dt = arrow.get(period_end.date()).replace(hour=23, minute=59, second=59).datetime if hasattr(period_end, 'date') else arrow.get(period_end).datetime
            else:
                period_end_dt = arrow.get(period_end).datetime
            
            log.info(f"CMS130v6: Searching imaging reports - period: {period_start_dt} to {period_end_dt}")
            
            # Use the find() method to match via codings
            # Note: original_date is a DateField, so we need to compare with date objects
            # Legacy uses .within(period) which uses __range (inclusive on both ends)
            # Use __lte (less than or equal) to include the end date, matching legacy .within() behavior
            reports = (
                ImagingReport.objects.for_patient(patient.id)
                .filter(
                    original_date__gte=period_start_dt.date(),
                    original_date__lte=period_end_dt.date(),  # Include end date (inclusive)
                    junked=False,
                )
                .find(value_set_class)
                .order_by("-original_date")
            )
            
            log.info(f"CMS130v6: Found {reports.count()} imaging reports matching value set")

            if reports.exists():
                report = reports.first()
                log.info(f"CMS130v6: Selected imaging report {report.id}, original_date={report.original_date}")
                return report

            return None
        except Exception as e:
            log.error(f"CMS130v6: Error finding imaging report: {str(e)}")
            return None

    def _find_referral_report(
        self, patient: Patient, value_set_class, period_start: Any, period_end: Any
    ) -> ReferralReport | None:
        try:
            # Use the find() method to match via codings
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

    def _get_most_recent_screening(self, patient: Patient) -> dict | None:
        """Get the most recent screening with its type, date, and screening interval (days)."""
        most_recent = None
        most_recent_date = None

        # Screening intervals in days
        SCREENING_INTERVALS = {
            "FOBT": 365,  # 1 year
            "FIT-DNA": 1095,  # 3 years
            "Flexible Sigmoidoscopy": 1825,  # 5 years
            "CT Colonography": 1825,  # 5 years
            "Colonoscopy": 3650,  # 10 years
        }

        # Check all screening types
        screenings = []

        # FOBT
        fobt_period_start = self.timeframe.end.shift(years=-1)
        fobt_report = self._find_lab_report(patient, FecalOccultBloodTestFobt, fobt_period_start, self.timeframe.end)
        if fobt_report:
            screenings.append(("FOBT", fobt_report.original_date, SCREENING_INTERVALS["FOBT"]))

        # FIT-DNA
        fit_dna_period_start = self.timeframe.end.shift(years=-3)
        fit_dna_report = self._find_lab_report(patient, FitDna, fit_dna_period_start, self.timeframe.end)
        if fit_dna_report:
            screenings.append(("FIT-DNA", fit_dna_report.original_date, SCREENING_INTERVALS["FIT-DNA"]))

        # Flexible Sigmoidoscopy
        sigmoid_period_start = self.timeframe.end.shift(years=-5)
        sigmoid_imaging = self._find_imaging_report(patient, FlexibleSigmoidoscopy, sigmoid_period_start, self.timeframe.end)
        if sigmoid_imaging:
            screenings.append(("Flexible Sigmoidoscopy", sigmoid_imaging.original_date, SCREENING_INTERVALS["Flexible Sigmoidoscopy"]))
        sigmoid_referral = self._find_referral_report(patient, FlexibleSigmoidoscopy, sigmoid_period_start, self.timeframe.end)
        if sigmoid_referral:
            screenings.append(("Flexible Sigmoidoscopy", sigmoid_referral.original_date, SCREENING_INTERVALS["Flexible Sigmoidoscopy"]))

        # CT Colonography
        ct_period_start = self.timeframe.end.shift(years=-5)
        ct_imaging = self._find_imaging_report(patient, CtColonography, ct_period_start, self.timeframe.end)
        if ct_imaging:
            screenings.append(("CT Colonography", ct_imaging.original_date, SCREENING_INTERVALS["CT Colonography"]))
        ct_imaging_v6 = self._find_imaging_report(patient, CMS130v6CtColonography, ct_period_start, self.timeframe.end)
        if ct_imaging_v6:
            screenings.append(("CT Colonography", ct_imaging_v6.original_date, SCREENING_INTERVALS["CT Colonography"]))
        ct_referral = self._find_referral_report(patient, CtColonography, ct_period_start, self.timeframe.end)
        if ct_referral:
            screenings.append(("CT Colonography", ct_referral.original_date, SCREENING_INTERVALS["CT Colonography"]))
        ct_referral_v6 = self._find_referral_report(patient, CMS130v6CtColonography, ct_period_start, self.timeframe.end)
        if ct_referral_v6:
            screenings.append(("CT Colonography", ct_referral_v6.original_date, SCREENING_INTERVALS["CT Colonography"]))

        # Colonoscopy
        colon_period_start = self.timeframe.end.shift(years=-10)
        colon_imaging = self._find_imaging_report(patient, Colonoscopy, colon_period_start, self.timeframe.end)
        if colon_imaging:
            screenings.append(("Colonoscopy", colon_imaging.original_date, SCREENING_INTERVALS["Colonoscopy"]))
        colon_referral = self._find_referral_report(patient, Colonoscopy, colon_period_start, self.timeframe.end)
        if colon_referral:
            screenings.append(("Colonoscopy", colon_referral.original_date, SCREENING_INTERVALS["Colonoscopy"]))

        # Find most recent
        import arrow
        for screening_type, screening_date, days in screenings:
            if screening_date:
                date_arrow = arrow.get(screening_date) if screening_date else None
                if date_arrow and (most_recent_date is None or date_arrow > most_recent_date):
                    most_recent_date = date_arrow
                    most_recent = {"type": screening_type, "date": date_arrow, "days": days}

        return most_recent

    def _create_not_applicable_card(self, patient: Patient) -> Effect:
        card = ProtocolCard(
            patient_id=patient.id,
            key="CMS130v6",
            title="Colorectal Cancer Screening - NOT APPLICABLE",
            narrative="DEBUGGING: ",
            status=ProtocolCard.Status.NOT_APPLICABLE,
        )
        return card.apply()

    def _format_date_with_relative_time(self, exam_date) -> str:
        """
        Format date with relative time like "2 weeks ago on 10/31/25".
        Matches old implementation's display_date format.
        """
        import arrow
        
        now = arrow.get(self.timeframe.end.datetime)
        # Convert to arrow if not already (avoid isinstance check with arrow.Arrow type)
        if hasattr(exam_date, 'format'):
            # Already an arrow object
            exam_arrow = exam_date
        else:
            # Convert datetime/date to arrow
            exam_arrow = arrow.get(exam_date)
        
        # Calculate time difference
        days_diff = (now - exam_arrow).days
        
        # Format relative time
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
        
        # Format date as MM/DD/YY
        date_formatted = exam_arrow.format("M/D/YY")
        
        return f"{relative_time} on {date_formatted}"

    def _create_satisfied_card(self, patient: Patient, last_exam: dict | None) -> Effect:
        import arrow
        
        if last_exam and last_exam.get("date"):
            exam_date = arrow.get(last_exam["date"])
            # Match old format: "{name} had a {what} {relative_time} on {date}."
            date_with_relative = self._format_date_with_relative_time(exam_date)
            narrative = f"DEBUGGING: {patient.first_name} had a {last_exam.get('what', 'screening')} {date_with_relative}."
            
            # Calculate due_in: (last_exam_date + screening_interval_days - now).days
            if last_exam.get("days"):
                next_due_date = exam_date.shift(days=last_exam["days"])
                now = arrow.get(self.timeframe.end.datetime)
                due_in = (next_due_date - now).days
            else:
                due_in = -1
        else:
            narrative = f"DEBUGGING: {patient.first_name} has had appropriate colorectal cancer screening."
            due_in = -1

        card = ProtocolCard(
            patient_id=patient.id,
            key="CMS130v6",
            title="Colorectal Cancer Screening - SATISFIED DEBUGGING: ",
            narrative=narrative,
            status=ProtocolCard.Status.SATISFIED,
            due_in=due_in,
            can_be_snoozed=True,
        )
        return card.apply()

    def _recent_exam_context(self, patient: Patient) -> str:
        """
        Get context about the most recent exam of any type (not just in numerator).
        Returns: "Last {what} done {date}." or "No relevant exams found."
        """
        import arrow
        
        try:
            # Search for most recent exam of any type, regardless of measurement period
            most_recent = None
            most_recent_date = None
            
            # Check Colonoscopy (10 year lookback)
            colon_period_start = self.timeframe.end.shift(years=-10)
            colon_imaging = self._find_imaging_report(patient, Colonoscopy, colon_period_start, self.timeframe.end)
            if colon_imaging and colon_imaging.original_date:
                date_arrow = arrow.get(colon_imaging.original_date)
                if most_recent_date is None or date_arrow > most_recent_date:
                    most_recent_date = date_arrow
                    most_recent = {"what": "Colonoscopy", "date": date_arrow}
            
            colon_referral = self._find_referral_report(patient, Colonoscopy, colon_period_start, self.timeframe.end)
            if colon_referral and colon_referral.original_date:
                date_arrow = arrow.get(colon_referral.original_date)
                if most_recent_date is None or date_arrow > most_recent_date:
                    most_recent_date = date_arrow
                    most_recent = {"what": "Colonoscopy", "date": date_arrow}
            
            # Check CT Colonography (5 year lookback)
            ct_period_start = self.timeframe.end.shift(years=-5)
            ct_imaging = self._find_imaging_report(patient, CtColonography, ct_period_start, self.timeframe.end)
            if ct_imaging and ct_imaging.original_date:
                date_arrow = arrow.get(ct_imaging.original_date)
                if most_recent_date is None or date_arrow > most_recent_date:
                    most_recent_date = date_arrow
                    most_recent = {"what": "CT Colonography", "date": date_arrow}
            
            ct_imaging_v6 = self._find_imaging_report(patient, CMS130v6CtColonography, ct_period_start, self.timeframe.end)
            if ct_imaging_v6 and ct_imaging_v6.original_date:
                date_arrow = arrow.get(ct_imaging_v6.original_date)
                if most_recent_date is None or date_arrow > most_recent_date:
                    most_recent_date = date_arrow
                    most_recent = {"what": "CT Colonography", "date": date_arrow}
            
            ct_referral = self._find_referral_report(patient, CtColonography, ct_period_start, self.timeframe.end)
            if ct_referral and ct_referral.original_date:
                date_arrow = arrow.get(ct_referral.original_date)
                if most_recent_date is None or date_arrow > most_recent_date:
                    most_recent_date = date_arrow
                    most_recent = {"what": "CT Colonography", "date": date_arrow}
            
            ct_referral_v6 = self._find_referral_report(patient, CMS130v6CtColonography, ct_period_start, self.timeframe.end)
            if ct_referral_v6 and ct_referral_v6.original_date:
                date_arrow = arrow.get(ct_referral_v6.original_date)
                if most_recent_date is None or date_arrow > most_recent_date:
                    most_recent_date = date_arrow
                    most_recent = {"what": "CT Colonography", "date": date_arrow}
            
            # Check Flexible Sigmoidoscopy (5 year lookback)
            sigmoid_period_start = self.timeframe.end.shift(years=-5)
            sigmoid_imaging = self._find_imaging_report(patient, FlexibleSigmoidoscopy, sigmoid_period_start, self.timeframe.end)
            if sigmoid_imaging and sigmoid_imaging.original_date:
                date_arrow = arrow.get(sigmoid_imaging.original_date)
                if most_recent_date is None or date_arrow > most_recent_date:
                    most_recent_date = date_arrow
                    most_recent = {"what": "Flexible sigmoidoscopy", "date": date_arrow}
            
            sigmoid_referral = self._find_referral_report(patient, FlexibleSigmoidoscopy, sigmoid_period_start, self.timeframe.end)
            if sigmoid_referral and sigmoid_referral.original_date:
                date_arrow = arrow.get(sigmoid_referral.original_date)
                if most_recent_date is None or date_arrow > most_recent_date:
                    most_recent_date = date_arrow
                    most_recent = {"what": "Flexible sigmoidoscopy", "date": date_arrow}
            
            # Check FIT-DNA (3 year lookback)
            fit_dna_period_start = self.timeframe.end.shift(years=-3)
            fit_dna_report = self._find_lab_report(patient, FitDna, fit_dna_period_start, self.timeframe.end)
            if fit_dna_report and fit_dna_report.original_date:
                date_arrow = arrow.get(fit_dna_report.original_date)
                if most_recent_date is None or date_arrow > most_recent_date:
                    most_recent_date = date_arrow
                    most_recent = {"what": "FIT-DNA", "date": date_arrow}
            
            # Check FOBT (1 year lookback)
            fobt_period_start = self.timeframe.end.shift(years=-1)
            fobt_report = self._find_lab_report(patient, FecalOccultBloodTestFobt, fobt_period_start, self.timeframe.end)
            if fobt_report and fobt_report.original_date:
                date_arrow = arrow.get(fobt_report.original_date)
                if most_recent_date is None or date_arrow > most_recent_date:
                    most_recent_date = date_arrow
                    most_recent = {"what": "FOBT", "date": date_arrow}
            
            if most_recent:
                date_formatted = most_recent["date"].format("MMMM D, YYYY")
                return f"Last {most_recent['what']} done {date_formatted}."
            else:
                return "No relevant exams found."
                
        except Exception as e:
            log.error(f"CMS130v6: Error getting recent exam context: {str(e)}")
            return "No relevant exams found."

    def _friendly_time_duration(self, duration_in_days: int) -> str:
        """
        Convert duration in days to friendly format (e.g., "10 years", "2 months, 5 days").
        Matches legacy implementation's friendly_time_duration method.
        """
        friendly_duration = 'invalid duration'
        if duration_in_days >= 1:
            friendly_duration = f'{duration_in_days} days'
            if duration_in_days >= 365:
                years, days = divmod(duration_in_days, 365)
                plural = 's' if years > 1 else ''
                friendly_duration = f'{years} year{plural}'
                if days >= 30:
                    months = days // 30
                    plural = 's' if months > 1 else ''
                    friendly_duration = friendly_duration + f', {months} month{plural}'
            elif duration_in_days >= 30:
                months, days = divmod(duration_in_days, 30)
                plural = 's' if months > 1 else ''
                friendly_duration = f'{months} month{plural}'
                if days > 0:
                    plural = 's' if days > 1 else ''
                    friendly_duration = friendly_duration + f', {days} day{plural}'
        return friendly_duration

    def _screening_interval_context(self) -> str:
        """
        Get screening interval context text (e.g., "Current screening interval 10 years.").
        Matches legacy implementation's screening_interval_context method.
        """
        try:
            # Get default display interval from Meta (10 years = 3650 days)
            # Access Meta class attribute directly
            default_interval = getattr(self.Meta, 'default_display_interval_in_days', 365 * 10)
            interval_text = self._friendly_time_duration(default_interval)
            
            # TODO: Handle period_adjustment if needed (for protocol overrides)
            # The legacy checks: if self.period_adjustment: interval_text = self._friendly_time_duration(self.period_adjustment['cycleDays'])
            # We don't have period_adjustment in the plugin SDK yet, so using default for now
            
            return f'Current screening interval {interval_text}.'
        except Exception as e:
            log.error(f"CMS130v6: Error getting screening interval context: {str(e)}")
            return ''

    def _create_due_card(self, patient: Patient) -> Effect:
        # Build narrative with multiple parts (matching old format)
        # Legacy uses newlines to join: result.add_narrative() joins with '\n'
        narrative_parts = [
            f"DEBUGGING: {patient.first_name} is due for a Colorectal Cancer Screening.",
            self._recent_exam_context(patient),
            self._screening_interval_context(),
        ]
        narrative = "\n".join(narrative_parts)  # Join with newlines to match legacy

        card = ProtocolCard(
            patient_id=patient.id,
            key="CMS130v6",
            title="Colorectal Cancer Screening - DUE DEBUGGING: ",
            narrative=narrative,
            status=ProtocolCard.Status.DUE,
            due_in=-1,
            can_be_snoozed=True,
        )

        # Context with ICD-10 code Z1211 for screening encounter
        screening_context = {
            "conditions": [
                [
                    {
                        "code": "Z1211",
                        "system": "ICD-10",
                        "display": "Encounter for screening for malignant neoplasm of colon",
                    }
                ]
            ]
        }

        # Add recommendations for all screening options (ranked by priority)
        # Rank 1: FOBT - LabOrderCommand
        fobt_codes = list(FecalOccultBloodTestFobt.LOINC)[:1] if hasattr(FecalOccultBloodTestFobt, "LOINC") else []
        if fobt_codes:
            fobt_command = LabOrderCommand(
                tests_order_codes=fobt_codes,
                diagnosis_codes=["Z1211"],  # ICD-10 code for screening encounter
            )
            fobt_recommendation = fobt_command.recommend(
                title="Order a FOBT",
                button="Order"
            )
            # Add context with conditions
            if fobt_recommendation.context:
                fobt_recommendation.context.update(screening_context)
            else:
                fobt_recommendation.context = screening_context
            card.recommendations.append(fobt_recommendation)

        # Rank 2: FIT-DNA - LabOrderCommand
        fit_dna_codes = list(FitDna.LOINC)[:1] if hasattr(FitDna, "LOINC") else []
        if fit_dna_codes:
            fit_dna_command = LabOrderCommand(
                tests_order_codes=fit_dna_codes,
                diagnosis_codes=["Z1211"],  # ICD-10 code for screening encounter
            )
            fit_dna_recommendation = fit_dna_command.recommend(
                title="Order a FIT-DNA",
                button="Order"
            )
            # Add context with conditions
            if fit_dna_recommendation.context:
                fit_dna_recommendation.context.update(screening_context)
            else:
                fit_dna_recommendation.context = screening_context
            card.recommendations.append(fit_dna_recommendation)

        # Rank 3: Flexible Sigmoidoscopy - ReferCommand
        sigmoid_command = ReferCommand(
            service_provider=ServiceProvider(
                first_name="Referral",
                last_name="Gastroenterology",
                specialty="Gastroenterology",
                practice_name="Gastroenterology Referral Network",
                notes="For flexible sigmoidoscopy screening.",
            ),
            diagnosis_codes=["Z1211"],  # ICD-10 code for screening encounter
            include_visit_note=False,
        )
        sigmoid_recommendation = sigmoid_command.recommend(
            title="Order a Flexible sigmoidoscopy",
            button="Order"
        )
        # Add context with conditions and specialties
        sigmoid_context = {
            **screening_context,
            "specialties": ["Gastroenterology"],
        }
        if sigmoid_recommendation.context:
            sigmoid_recommendation.context.update(sigmoid_context)
        else:
            sigmoid_recommendation.context = sigmoid_context
        card.recommendations.append(sigmoid_recommendation)

        # Rank 4: CT Colonography - ImagingOrderCommand
        # Use CPT codes from CMS130v6CtColonography value set
        ct_cpt_codes = list(CMS130v6CtColonography.CPT)[:1] if hasattr(CMS130v6CtColonography, "CPT") else []
        if ct_cpt_codes:
            ct_command = ImagingOrderCommand(
                image_code=ct_cpt_codes[0],
                diagnosis_codes=["Z1211"],  # ICD-10 code for screening encounter
            )
            ct_recommendation = ct_command.recommend(
                title="Order a CT Colonography",
                button="Order"
            )
            # Add context with conditions and specialties
            ct_context = {
                **screening_context,
                "specialties": ["Radiology"],
            }
            if ct_recommendation.context:
                ct_recommendation.context.update(ct_context)
            else:
                ct_recommendation.context = ct_context
            card.recommendations.append(ct_recommendation)

        # Rank 5: Colonoscopy - ReferCommand
        colonoscopy_command = ReferCommand(
            service_provider=ServiceProvider(
                first_name="Referral",
                last_name="Gastroenterology",
                specialty="Gastroenterology",
                practice_name="Gastroenterology Referral Network",
                notes="For colonoscopy screening.",
            ),
            diagnosis_codes=["Z1211"],  # ICD-10 code for screening encounter
            include_visit_note=False,
        )
        colonoscopy_recommendation = colonoscopy_command.recommend(
            title="Order a Colonoscopy",
            button="Order"
        )
        # Add context with conditions and specialties
        colonoscopy_context = {
            **screening_context,
            "specialties": ["Gastroenterology"],
        }
        if colonoscopy_recommendation.context:
            colonoscopy_recommendation.context.update(colonoscopy_context)
        else:
            colonoscopy_recommendation.context = colonoscopy_context
        card.recommendations.append(colonoscopy_recommendation)

        return card.apply()

    def _coding_in_value_set(self, coding: ConditionCoding, value_set_class) -> bool:
        """Check if a ConditionCoding belongs to a value set."""
        try:
            normalized_system = coding.system.replace("-", "").upper() if coding.system else ""
            normalized_code = coding.code.replace(".", "") if coding.code else ""
            
            # Extract SNOMED CT from URLs like http://snomed.info/sct
            if "SNOMED" in normalized_system or "SCT" in normalized_system:
                normalized_system = "SNOMEDCT"

            if normalized_system in ["ICD10", "ICD10CM"]:
                codes = getattr(value_set_class, "ICD10CM", set())
                codes_normalized = {code.replace(".", "") for code in codes}
                return normalized_code in codes_normalized
            elif normalized_system in ["SNOMEDCT", "SNOMED"]:
                codes = getattr(value_set_class, "SNOMEDCT", set())
                return coding.code in codes
            elif normalized_system == "CPT":
                codes = getattr(value_set_class, "CPT", set())
                return coding.code in codes
            elif normalized_system == "HCPCS":
                codes = getattr(value_set_class, "HCPCS", set())
                return coding.code in codes
            elif normalized_system == "ICD10PCS":
                codes = getattr(value_set_class, "ICD10PCS", set())
                return coding.code in codes

            return False
        except Exception as e:
            log.error(f"CMS130v6: Error checking coding in value set: {str(e)}")
            return False

    def _coding_in_value_set_for_note_type(self, note_type: NoteType, value_set_class) -> bool:
        """Check if a NoteType coding belongs to a value set."""
        try:
            # NoteType inherits from Coding, so it has code and system directly
            normalized_system = note_type.system.replace("-", "").upper() if note_type.system else ""
            normalized_code = note_type.code.replace(".", "") if note_type.code else ""
            
            # Extract SNOMED CT from URLs like http://snomed.info/sct
            if "SNOMED" in normalized_system or "SCT" in normalized_system:
                normalized_system = "SNOMEDCT"

            if normalized_system in ["ICD10", "ICD10CM"]:
                codes = getattr(value_set_class, "ICD10CM", set())
                codes_normalized = {code.replace(".", "") for code in codes}
                return normalized_code in codes_normalized
            elif normalized_system in ["SNOMEDCT", "SNOMED"]:
                codes = getattr(value_set_class, "SNOMEDCT", set())
                return note_type.code in codes
            elif normalized_system == "CPT":
                codes = getattr(value_set_class, "CPT", set())
                return note_type.code in codes
            elif normalized_system == "HCPCS":
                codes = getattr(value_set_class, "HCPCS", set())
                return note_type.code in codes

            return False
        except Exception as e:
            log.error(f"CMS130v6: Error checking note type coding in value set: {str(e)}")
            return False


# Alias for backward compatibility
Protocol = CMS130v6ColorectalCancerScreening
