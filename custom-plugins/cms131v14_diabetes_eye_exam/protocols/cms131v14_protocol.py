import arrow
from django.db.models import Q

from canvas_sdk.commands import PerformCommand, ReferCommand
from canvas_sdk.commands.constants import CodeSystems, ServiceProvider
from canvas_sdk.effects import Effect
from canvas_sdk.effects.protocol_card.protocol_card import ProtocolCard
from canvas_sdk.events import EventType
from canvas_sdk.protocols import ClinicalQualityMeasure
from canvas_sdk.v1.data import Patient
from canvas_sdk.v1.data.condition import Condition
from canvas_sdk.v1.data.observation import Observation
from canvas_sdk.v1.data.claim_line_item import ClaimLineItem
from canvas_sdk.v1.data.encounter import Encounter
from canvas_sdk.v1.data.questionnaire import Interview, InterviewQuestionResponse
from canvas_sdk.v1.data.medication import Medication
from canvas_sdk.v1.data.referral import ReferralReport
from canvas_sdk.value_set.v2026.condition import (
    Diabetes,
    DiabeticRetinopathy,
    AdvancedIllness,
    FrailtyDiagnosis,
    HospiceDiagnosis,
    PalliativeCareDiagnosis,
)
from canvas_sdk.value_set.v2026.communication import DiabeticRetinopathySeverityLevel,AutonomousEyeExamResultOrFinding
from canvas_sdk.value_set.v2026.encounter import (
    OfficeVisit,
    AnnualWellnessVisit,
    PreventiveCareServicesEstablishedOfficeVisit18AndUp,
    HomeHealthcareServices,
    OphthalmologicalServices,
    TelephoneVisits,
    PalliativeCareEncounter,
    HospiceEncounter,
)
from canvas_sdk.value_set.v2026.intervention import (
    HospiceCareAmbulatory,
    PalliativeCareIntervention,
)
from canvas_sdk.value_set.v2026.medication import DementiaMedications
from canvas_sdk.value_set.v2026.physical_exam import RetinalOrDilatedEyeExam
from canvas_sdk.value_set.v2022.condition import (
    DementiaAndMentalDegenerations,
    Cancer,
)
from canvas_sdk.value_set.v2022.encounter import (
    PreventiveCareServicesInitialOfficeVisit_18AndUp,
    CareServicesInLongTermResidentialFacility,
    NursingFacilityVisit,
)
from canvas_sdk.value_set.v2022.medication import ChemotherapyForAdvancedCancer
from logger import log


class CMS131v14DiabetesEyeExam(ClinicalQualityMeasure):
    class Meta:
        title = "Diabetes: Eye Exam"
        description = (
            "Percentage of patients 18-75 years of age with diabetes and an active diagnosis of retinopathy in any part of the measurement period who had a retinal or dilated eye exam by an eye care professional during the measurement period or diabetics with no diagnosis of retinopathy in any part of the measurement period who had a retinal or dilated eye exam by an eye care professional during the measurement period or in the 12 months prior to the measurement period"
        )
        version = "2025-05-08v14"
        information = "https://ecqi.healthit.gov/ecqm/ec/2026/cms0131v14"
        identifiers = ["CMS131v14"]
        types = ["CQM"]
        authors = ["National Committee for Quality Assurance"]
        references = [
            "American Diabetes Association. Microvascular complications and foot care. Sec. 10. In Standards of Medical Care in Diabetes 2017. Diabetes Care 2017;40(Suppl. 1):S88-S98",
            "American Diabetes Association. (2024). Statistics About Diabetes. Retrieved from https://diabetes.org/about-diabetes/statistics/about-diabetes",
            "Centers for Disease Control and Prevention. (2020). Common Eye Disorders and Diseases. Retrieved from https://www.cdc.gov/visionhealth/basics/ced/index.html",
            "Centers for Disease Control and Prevention. (2022a). What is Diabetes? Retrieved from https://www.cdc.gov/diabetes/basics/diabetes.html",
            "Centers for Disease Control and Prevention. (2022b). National Diabetes Statistics Report, 2021. US Dept of Health and Human Services. Retrieved from https://www.cdc.gov/diabetes/library/reports/reportcard.html",
            "Centers for Disease Control and Prevention. (2024). National Diabetes Statistics Report. Retrieved from https://www.cdc.gov/diabetes/php/data-research/index.html",
            "Parker E, Lin J, Mahoney T, et al. Economic Costs of Diabetes in the U.S. in 2022. Diabetes Care. 2024;47(1):26-43. doi:10.2337/dci23-0085"
        ]

    RESPONDS_TO = [
        EventType.Name(EventType.CONDITION_CREATED),
        EventType.Name(EventType.CONDITION_UPDATED),
        EventType.Name(EventType.CONDITION_RESOLVED),
        EventType.Name(EventType.MEDICATION_LIST_ITEM_CREATED),
        EventType.Name(EventType.MEDICATION_LIST_ITEM_UPDATED),
        EventType.Name(EventType.INTERVIEW_CREATED),
        EventType.Name(EventType.INTERVIEW_UPDATED),
        EventType.Name(EventType.PATIENT_UPDATED),
        EventType.Name(EventType.ENCOUNTER_CREATED),
        EventType.Name(EventType.ENCOUNTER_UPDATED),
        EventType.Name(EventType.CLAIM_CREATED),
        EventType.Name(EventType.CLAIM_UPDATED)
    ]

    # Age range constants
    AGE_RANGE_START = 18
    AGE_RANGE_END = 75

    LOINC_SYSTEM_IDENTIFIERS = ["http://loinc.org", "LOINC"]

    NO_APPARENT_RETINOPATHY_LOINC_CODE = "LA18643-9"
    LEFT_EYE_LOINC_CODE = "71490-7"
    RIGHT_EYE_LOINC_CODE = "71491-5"
    AUTONOMOUS_EYE_EXAM_LOINC_CODE = "105914-6"

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
                log.warning(f"CMS131v14: Could not find patient for condition {target_id}")
                return None, None

            log.warning(f"CMS131v14: Unhandled event type {self.event.type}")

            # Fallback: get patient ID and query patient
            patient_id = self.patient_id_from_target()
            if patient_id:
                return Patient.objects.filter(id=patient_id).first(), None
            return None, None

        except Exception as e:
            log.error(f"CMS131v14: Error getting patient: {str(e)}")
            return None, None

    def _is_condition_diabetes(self, condition: Condition) -> bool:
        try:
            return Condition.objects.filter(id=condition.id).find(Diabetes).exists()
        except Exception as e:
            log.error(f"CMS131v14: Error checking if condition is diabetes: {str(e)}")
            return False

    def _should_remove_card(self, patient: Patient, condition: Condition | None) -> bool:
        try:
            if not condition:
                log.warning(f"CMS131v14: Could not find condition {self.event.target.id}")
                return False

            if not self._is_condition_diabetes(condition):
                log.info(f"CMS131v14: Condition {condition.id} is not diabetes, no action needed")
                return False

            if condition.entered_in_error:
                log.info(
                    f"CMS131v14: Diabetes condition {condition.id} marked as entered_in_error for patient {patient.id}"
                )
                if not self._has_diabetes_diagnosis(patient):
                    log.info(f"CMS131v14: No other diabetes diagnoses found, removing card")
                    return True
                else:
                    log.info(f"CMS131v14: Patient still has other diabetes diagnoses, keeping card")
                    return False

            return False

        except Exception as e:
            log.error(f"CMS131v14: Error checking if card should be removed: {str(e)}")
            return False

    def compute(self) -> list[Effect]:
        try:
            patient, condition = self._get_patient()
            if not patient:
                log.warning("CMS131v14: Could not determine patient from event, skipping")
                return []

            log.info(f"CMS131v14: Processing event for patient_id={patient.id}")

            if self._should_remove_card(patient, condition):
                return [self._create_not_applicable_card(patient)]

            # Calculate age
            age = int(patient.age_at(self.timeframe.end))

            if not self._in_initial_population(patient, age):
                log.info(f"CMS131v14: Patient {patient.id} not in initial population")
                return [self._create_not_applicable_card(patient)]

            if not self._in_denominator(patient, age):
                log.info(f"CMS131v14: Patient {patient.id} excluded from denominator")
                return [self._create_not_applicable_card(patient)]

            if self._in_numerator(patient):
                log.info(f"CMS131v14: Patient {patient.id} meets numerator criteria")
                return [self._create_satisfied_card(patient)]
            else:
                log.info(f"CMS131v14: Patient {patient.id} does not meet numerator criteria")
                return [self._create_due_card(patient)]

        except Exception as e:
            log.error(f"Error in CMS131v14 protocol compute: {str(e)}")
            return []

    def _in_initial_population(self, patient: Patient, age: int) -> bool:
        if not (self.AGE_RANGE_START <= age <= self.AGE_RANGE_END):
            log.info(f"CMS131v14: Patient {patient.id} age {age} not in 18-75 range")
            return False

        if not self._has_diabetes_diagnosis_overlapping_period(patient):
            log.info(f"CMS131v14: Patient {patient.id} does not have diabetes diagnosis overlapping period")
            return False

        if not self._has_eligible_encounter_in_period(patient):
            log.info(f"CMS131v14: Patient {patient.id} has no eligible encounters in period")
            return False

        return True

    def _in_denominator(self, patient: Patient, age: int) -> bool:
        if self._has_hospice_care_in_period(patient):
            log.info(f"CMS131v14: Patient {patient.id} in hospice care")
            return False

        if self._is_age_66_plus_with_frailty(
            patient, age
        ) and self._has_advanced_illness_or_dementia_meds(patient):
            log.info(f"CMS131v14: Patient {patient.id} is age 66+ with frailty and advanced illness or dementia meds")
            return False

        if self._is_age_66_plus_in_nursing_home(patient, age):
            log.info(f"CMS131v14: Patient {patient.id} is age 66+ in nursing home")
            return False

        if self._has_palliative_care_in_period(patient):
            log.info(f"CMS131v14: Patient {patient.id} has palliative care")
            return False

        if self._has_bilateral_absence_of_eyes(patient):
            log.info(f"CMS131v14: Patient {patient.id} has bilateral eye absence")
            return False

        return True

    def _in_numerator(self, patient: Patient) -> bool:
        if self._has_retinopathy_diagnosis_in_period(patient):
            return self._has_retinal_exam_in_period(patient)

        if self._has_retinal_exam_in_period_or_year_prior(patient):
            log.info(
                    f"CMS131v14: Found retinal exam in measurement period or year prior for patient {patient.id}"
                )
            return True

        if self._has_autonomous_eye_exam_in_period(patient):
            log.info(f"CMS131v14: Found autonomous eye exam in measurement period for patient {patient.id}")
            return True

        if self._has_retinal_finding_with_severity_in_period(patient):
            return True

        if self._has_retinal_finding_no_severity_in_prior_year(patient):
            return True

        return False

    def _has_diabetes_diagnosis(self, patient: Patient) -> bool:
        try:
            diabetes_conditions = Condition.objects.for_patient(patient.id).find(Diabetes).active()
            
            has_diabetes = diabetes_conditions.exists()
            
            if has_diabetes:
                log.info(f"CMS131v14: Found diabetes diagnosis for patient {patient.id}")
            else:
                log.info(f"CMS131v14: No active diabetes diagnoses found for patient {patient.id}")
            
            return has_diabetes

        except Exception as e:
            log.error(f"CMS131v14: Error checking diabetes diagnosis: {str(e)}")
            return False

    def _has_diabetes_diagnosis_overlapping_period(self, patient: Patient) -> bool:
        try:
            return Condition.objects.for_patient(patient.id).find(Diabetes).active().exists()

        except Exception as e:
            log.error(f"CMS131v14: Error checking diabetes diagnosis overlapping period: {str(e)}")
            return False

    def _has_eligible_encounter_in_period(self, patient: Patient) -> bool:
        """
        Check if patient has an eligible encounter during the measurement period.
        
        Per CMS131v14 CQL, eligible encounters include:
        - Office Visit
        - Annual Wellness Visit
        - Preventive Care Services Established Office Visit, 18 and Up
        - Preventive Care Services Initial Office Visit, 18 and Up
        - Home Healthcare Services
        - Ophthalmological Services
        - Telephone Visits
        """
        try:
            start_date = self.timeframe.start.datetime
            end_date = self.timeframe.end.datetime
            
            # Check for office visit encounters
            # Office visits are identified by note_type_version codes matching OfficeVisit SNOMED codes
            # Filter for concluded encounters only (state="CON")
            office_visit_codes = OfficeVisit.SNOMEDCT
            
            office_visits = Encounter.objects.filter(
                note__patient=patient,
                note__note_type_version__code="308335008", # Office Visit code
                state="CON",
                start_time__gte=start_date,
                start_time__lte=end_date,
            )

            log.info(f"CMS131v14: Office visits: {office_visits.count()}")
            
            if office_visits.exists():
                log.info(f"CMS131v14: Patient {patient.id} has office visit encounter")
                return True
            
            # Check for encounters/services via claims (AWV, Preventive Care, etc.)
            # Collect all CPT and HCPCS codes from the relevant value sets
            eligible_codes = (
                AnnualWellnessVisit.HCPCSLEVELII |
                PreventiveCareServicesEstablishedOfficeVisit18AndUp.CPT |
                PreventiveCareServicesEstablishedOfficeVisit18AndUp.HCPCSLEVELII |
                PreventiveCareServicesInitialOfficeVisit_18AndUp.CPT |
                PreventiveCareServicesInitialOfficeVisit_18AndUp.HCPCSLEVELII |
                HomeHealthcareServices.CPT |
                HomeHealthcareServices.HCPCSLEVELII |
                OphthalmologicalServices.CPT |
                TelephoneVisits.CPT
            )
            
            # Query ClaimLineItem for any of these codes during the measurement period
            eligible_claims = ClaimLineItem.objects.filter(
                claim__note__patient=patient,
                status="active",
                from_date__gte=self.timeframe.start.date().isoformat(),
                from_date__lte=self.timeframe.end.date().isoformat(),
                proc_code__in=eligible_codes,
            )

            log.info(f"CMS131v14: Eligible claims: {eligible_claims.count()}")
            if eligible_claims.exists():
                found_code = eligible_claims.first().proc_code
                log.info(
                    f"CMS131v14: Patient {patient.id} has eligible encounter claim (code: {found_code})"
                )
                return True
            
            log.info(f"CMS131v14: Patient {patient.id} has no eligible encounters in period")
            return False
            
        except Exception as e:
            log.error(f"CMS131v14: Error checking eligible encounters: {str(e)}")
            return False

    def _has_hospice_care_in_period(self, patient: Patient) -> bool:
        """
        Check if patient is in hospice care during the measurement period.

        Checks for responses in the "Hospice & Frailty" questionnaire indicating hospice care.
        The questionnaire tracks:
        - Discharge to home for Hospice (SNOMED 428361000124107)
        - Discharge to Health Care Facility For Hospice Care (SNOMED 428371000124100)
        - Hospice Ambulatory Care (SNOMED 385765002)
        """
        try:
            # Get all interviews for the patient during the measurement period
            interviews = Interview.objects.filter(
                patient=patient,
                deleted=False,
                created__gte=self.timeframe.start.datetime,
                created__lte=self.timeframe.end.datetime,
            )

            # Check for hospice-related responses in the interviews
            # The hospice question has code "R-020" with SNOMED response codes
            hospice_response_codes = {"428361000124107", "428371000124100", "385765002"}

            # Check if there are any interviews for the patient
            if not interviews.exists():
                return False

            interview_ids = list(interviews.values_list('pk', flat=True))

            # Get all responses for the interviews
            interview_responses = InterviewQuestionResponse.objects.filter(
                interview_id__in=interview_ids,
                status="AC",
            ).select_related('response_option')
            
            # Check if any response has a hospice code
            for response in interview_responses:
                if response.response_option and response.response_option.code in hospice_response_codes:
                    log.info(
                        f"CMS131v14: Found hospice care response (code: {response.response_option.code}) for patient {patient.id}"
                    )
                    return True

            return False

        except Exception as e:
            log.error(f"CMS131v14: Error checking hospice status: {str(e)}")
            return False

    def _is_age_66_plus_with_frailty(self, patient: Patient, age: int) -> bool:
        """
        Check if patient is age 66+ with frailty indicators.
        Per CMS131v14: This exclusion only applies to patients age 66 and older.
        Uses responses from the "Hospice & Frailty" questionnaire.
        """
        # Check age requirement
        if age < 66:
            return False

        try:
            # Check for frailty criteria using questionnaire responses
            # Get all interviews for the patient during the measurement period
            interviews = Interview.objects.filter(
                patient=patient,
                deleted=False,
                created__gte=self.timeframe.start.datetime,
                created__lte=self.timeframe.end.datetime,
            )

            # Check if there are any interviews for the patient
            if not interviews.exists():
                return False

            interview_ids = list(interviews.values_list('pk', flat=True))

            # Get all responses for the interviews
            interview_responses = InterviewQuestionResponse.objects.filter(
                interview_id__in=interview_ids,
                status="AC",
            ).select_related('response_option')

            
            # Check for frailty-related response codes (from "R-021" question)
            frailty_response_codes = {"105501005"}  # Frailty Device
            
            # Check if any response has a frailty code
            for response in interview_responses:
                if response.response_option and response.response_option.code in frailty_response_codes:
                    log.info(
                        f"CMS131v14: Found frailty response (code: {response.response_option.code}) for patient {patient.id}"
                    )
                    return True

            return False

        except Exception as e:
            log.error(f"CMS131v14: Error checking frailty: {str(e)}")
            return False

    def _has_advanced_illness_or_dementia_meds(self, patient: Patient) -> bool:
        """
        Check if patient has advanced illness or dementia medications during the measurement period or year prior.
        Per CMS131v14 CQL:
        - Advanced illness diagnosis during the measurement period or the year prior
        - OR taking dementia medications during the measurement period or the year prior
        """
        try:
            # Calculate the extended timeframe (measurement period + 1 year prior)
            start_date = self.timeframe.start.shift(years=-1).datetime
            end_date = self.timeframe.end.datetime
            
            # Check for advanced illness conditions using separate targeted queries
            has_advanced_illness = (
                Condition.objects.for_patient(patient.id).active().find(DementiaAndMentalDegenerations).exists() or
                Condition.objects.for_patient(patient.id).active().find(Cancer).exists() or
                Condition.objects.for_patient(patient.id).active().find(ChemotherapyForAdvancedCancer).exists()
            )

            if has_advanced_illness:
                log.info(f"CMS131v14: Patient {patient.id} has advanced illness")
                return True
            
            # Check for dementia medications during measurement period or year prior
            has_dementia_meds = (
                Medication.objects.for_patient(patient.id)
                .active()
                .find(DementiaMedications)
                .filter(
                    Q(
                        start_date__lte=end_date,
                        end_date__gte=start_date,
                        end_date__isnull=False
                    ) | Q(
                        start_date__lte=end_date,
                        end_date__isnull=True
                    )
                )
                .exists()
            )
            
            if has_dementia_meds:
                log.info(f"CMS131v14: Patient {patient.id} has dementia medications")
                return True

            return False
        except Exception as e:
            log.error(f"CMS131v14: Error checking advanced illness: {str(e)}")
            return False

    def _is_age_66_plus_in_nursing_home(self, patient: Patient, age: int) -> bool:
        """
        Check for long-term residential care or nursing facility codes.
        Per CMS131v14: This exclusion only applies to patients age 66 and older.
        
        Checks for CPT codes in ClaimLineItem during the measurement period.
        """
        # Check age requirement
        if age < 66:
            return False

        try:
            # Get CPT codes from the value sets
            nursing_facility_codes = NursingFacilityVisit.CPT
            long_term_care_codes = CareServicesInLongTermResidentialFacility.CPT
            all_codes = nursing_facility_codes | long_term_care_codes

            # Check for claim line items with these CPT codes within the measurement period
            claim_line_items = ClaimLineItem.objects.filter(
                claim__note__patient=patient,
                status="active",
                from_date__gte=self.timeframe.start.date().isoformat(),
                from_date__lte=self.timeframe.end.date().isoformat(),
                proc_code__in=all_codes,
            )

            if claim_line_items.exists():
                found_code = claim_line_items.first().proc_code
                log.info(
                    f"CMS131v14: Patient {patient.id} age 66+ has nursing home/long-term care claim (CPT: {found_code})"
                )
                return True

            return False
        except Exception as e:
            log.error(f"CMS131v14: Error checking nursing home status: {str(e)}")
            return False

    def _has_palliative_care_in_period(self, patient: Patient) -> bool:
        """
        Check if the patient received palliative care during the measurement period."""
        try:
            # Check all palliative care value sets in conditions using separate targeted queries
            has_palliative_condition = (
                Condition.objects.for_patient(patient.id).active().find(PalliativeCareDiagnosis).exists() or
                Condition.objects.for_patient(patient.id).active().find(PalliativeCareEncounter).exists() or
                Condition.objects.for_patient(patient.id).active().find(PalliativeCareIntervention).exists()
            )
            
            if has_palliative_condition:
                log.info(f"CMS131v14: Found palliative care in conditions for patient {patient.id}")
                return True
            
            # Combine all palliative care codes for claim line item check 
            palliative_codes = (
                PalliativeCareEncounter.HCPCSLEVELII |
                PalliativeCareEncounter.SNOMEDCT |
                PalliativeCareIntervention.SNOMEDCT
            )
            
            # Check claim line items once with all combined codes
            if palliative_codes:
                palliative_claims = ClaimLineItem.objects.filter(
                    claim__note__patient=patient,
                    status="active",
                    from_date__gte=self.timeframe.start.date().isoformat(),
                    from_date__lte=self.timeframe.end.date().isoformat(),
                    proc_code__in=palliative_codes,
                )
                
                if palliative_claims.exists():
                    log.info(
                        f"CMS131v14: Found palliative care claim (CPT: {palliative_claims.first().proc_code}) for patient {patient.id}"
                    )
                    return True
            
            return False
            
        except Exception as e:
            log.error(f"CMS131v14: Error checking palliative care: {str(e)}")
            return False

    def _has_bilateral_absence_of_eyes(self, patient: Patient) -> bool:
        """Check for bilateral absence of eyes."""
        try:
            has_bilateral_absence = (
                Condition.objects.for_patient(patient.id)
                .active()
                .filter(
                    codings__code="15665641000119103",
                    codings__system__in=["SNOMED", "SNOMEDCT"]
                )
                .exists()
            ) 
            
            if has_bilateral_absence:
                log.info(
                    f"CMS131v14: Found bilateral eye absence (SNOMED 15665641000119103) for patient {patient.id}"
                )
            
            return has_bilateral_absence
            
        except Exception as e:
            log.error(f"CMS131v14: Error checking bilateral eye absence: {str(e)}")
            return False

    def _has_retinopathy_diagnosis_in_period(self, patient: Patient) -> bool:
        """Check for retinopathy diagnosis in period."""
        try:
            has_retinopathy_diagnosis = Condition.objects.for_patient(patient.id).find(DiabeticRetinopathy).active().exists()

            return has_retinopathy_diagnosis
        
        except Exception as e:
            log.error(f"CMS131v14: Error checking retinopathy diagnosis: {str(e)}")
            return False
        

    def _referral_report_exists(self, patient: Patient, timeframe_start, timeframe_end) -> bool:
        """Check if specified referral report exists in specified timeframe."""
        try:
            referral_reports = ReferralReport.objects.for_patient(patient.id).find(RetinalOrDilatedEyeExam).filter(
                original_date__gte=timeframe_start,
                original_date__lt=timeframe_end,
            )

            return referral_reports.exists()

        except Exception as e:
            log.error(f"CMS131v14: Error checking referral report in period: {str(e)}")
            return False


    def _has_retinal_exam_in_period(self, patient: Patient) -> bool:
        """Check for retinal or dilated eye exam in measurement period."""
        try:
            referral_reports = self._referral_report_exists(patient, self.timeframe.start.datetime, self.timeframe.end.datetime)

            return referral_reports
        
        except Exception as e:
            log.error(f"CMS131v14: Error checking retinal exam in period: {str(e)}")
            return False

    def _has_retinal_exam_in_period_or_year_prior(self, patient: Patient) -> bool:
        """Check for retinal or dilated eye exam in measurement period OR year prior."""
        try:
            extended_start = self.timeframe.start.shift(years=-1)
            referral_reports = self._referral_report_exists(patient, extended_start.datetime, self.timeframe.end.datetime)

            return referral_reports
        
        except Exception as e:
            log.error(f"CMS131v14: Error checking retinal exam in period or year prior: {str(e)}")
            return False

    def _observation_exists(self, patient: Patient, codings_code: str, value_codings_codes: set[str], timeframe_start, timeframe_end) -> bool:
        """Check if specified observation exists in specified timeframe."""
        try:
            observations = (
                Observation.objects.for_patient(patient.id)
                .committed()
                .filter(created__gte=timeframe_start, created__lt=timeframe_end, codings__code=codings_code, value_codings__code__in=value_codings_codes)
            )
            return observations.exists()

        except Exception as e:
            log.error(f"CMS131v14: Error checking observation for code {codings_code} and value codes {value_codings_codes}: {str(e)}")
            return False

    def _has_autonomous_eye_exam_in_period(self, patient: Patient) -> bool:
        """Check for autonomous AI eye exam with valid result in measurement period."""
        try:
            result_codes = set(AutonomousEyeExamResultOrFinding.LOINC)
            
            has_exam = self._observation_exists(patient, self.AUTONOMOUS_EYE_EXAM_LOINC_CODE, result_codes, self.timeframe.start.datetime, self.timeframe.end.datetime)

            return has_exam
        
        except Exception as e:
            log.error(f"CMS131v14: Error checking autonomous eye exam: {str(e)}")
            return False

    def _has_retinal_finding_with_severity_in_period(self, patient: Patient) -> bool:
        """Check for retinal exam findings with retinopathy severity level in measurement period."""
        try:
            measurement_start = self.timeframe.start.datetime
            measurement_end = self.timeframe.end.datetime
            
            severity_codes = set(DiabeticRetinopathySeverityLevel.LOINC)
            left_eye_retinopathy = self._observation_exists(
                patient, self.LEFT_EYE_LOINC_CODE, severity_codes, measurement_start, measurement_end
            )
            right_eye_retinopathy = self._observation_exists(
                patient, self.RIGHT_EYE_LOINC_CODE, severity_codes, measurement_start, measurement_end
            )
            
            if left_eye_retinopathy and right_eye_retinopathy:
                log.info(f"CMS131v14: Both eyes have retinopathy severity for patient {patient.id}")
                return True

            prior_year_start = self.timeframe.start.shift(years=-1).datetime
            prior_year_end = self.timeframe.start.datetime
            
            left_eye_no_retinopathy_prior = self._observation_exists(
                patient, self.LEFT_EYE_LOINC_CODE, set(self.NO_APPARENT_RETINOPATHY_LOINC_CODE), prior_year_start, prior_year_end
            )
            right_eye_no_retinopathy_prior = self._observation_exists(
                patient, self.RIGHT_EYE_LOINC_CODE, set(self.NO_APPARENT_RETINOPATHY_LOINC_CODE), prior_year_start, prior_year_end
            )
            
            if left_eye_retinopathy and right_eye_no_retinopathy_prior:
                log.info(
                    f"CMS131v14: Left eye has retinopathy, right eye no retinopathy in prior year for patient {patient.id}"
                )
                return True
            
            if right_eye_retinopathy and left_eye_no_retinopathy_prior:
                log.info(
                    f"CMS131v14: Right eye has retinopathy, left eye no retinopathy in prior year for patient {patient.id}"
                )
                return True
            
            return False
        
        except Exception as e:
            log.error(f"CMS131v14: Error checking retinal finding with severity: {str(e)}")
            return False

    def _has_retinal_finding_no_severity_in_prior_year(self, patient: Patient) -> bool:
        """Check for retinal exam findings with NO retinopathy severity in year prior."""
        try:
            prior_year_start = self.timeframe.start.shift(years=-1).datetime
            prior_year_end = self.timeframe.start.datetime
            
            left_eye_no_retinopathy = self._observation_exists(
                patient, self.LEFT_EYE_LOINC_CODE, set(self.NO_APPARENT_RETINOPATHY_LOINC_CODE), prior_year_start, prior_year_end
            )
            right_eye_no_retinopathy = self._observation_exists(
                patient, self.RIGHT_EYE_LOINC_CODE, set(self.NO_APPARENT_RETINOPATHY_LOINC_CODE), prior_year_start, prior_year_end
            )
            
            if left_eye_no_retinopathy and right_eye_no_retinopathy:
                log.info(
                    f"CMS131v14: Both eyes have no retinopathy in year prior for patient {patient.id}"
                )
                return True
            
            return False
        
        except Exception as e:
            log.error(f"CMS131v14: Error checking retinal finding no severity in prior year: {str(e)}")
            return False

    def _create_not_applicable_card(self, patient: Patient) -> Effect:
        card = ProtocolCard(
            patient_id=patient.id,
            key="CMS131v14",
            title="Diabetes: Eye Exam",
            narrative="",
            status=ProtocolCard.Status.NOT_APPLICABLE,
        )

        return card.apply()

    def _create_satisfied_card(self, patient: Patient) -> Effect:
        narrative = f"{patient.first_name} has diabetes and has completed a retinal examination."

        card = ProtocolCard(
            patient_id=patient.id,
            key="CMS131v14",
            title="Diabetes: Eye Exam",
            narrative=narrative,
            status=ProtocolCard.Status.SATISFIED,
            due_in=-1,
            can_be_snoozed=True,
        )

        return card.apply()

    def _get_diabetes_diagnosis_codes(self, patient: Patient) -> list[str]:
        try:
            diagnosis_codes = []
            diabetes_conditions = Condition.objects.for_patient(patient.id).find(Diabetes).active()

            for condition in diabetes_conditions:
                for coding in condition.codings.all():
                    diagnosis_codes.append(coding.code)

            log.info(
                f"CMS131v14: Found {len(diagnosis_codes)} diabetes diagnosis codes for patient {patient.id}"
            )
            return diagnosis_codes

        except Exception as e:
            log.error(f"CMS131v14: Error extracting diabetes diagnosis codes: {str(e)}")
            return []

    def _create_due_card(self, patient: Patient) -> Effect:
        narrative = f"{patient.first_name} has diabetes and is due for retinal examination."

        card = ProtocolCard(
            patient_id=patient.id,
            key="CMS131v14",
            title="Diabetes: Eye Exam",
            narrative=narrative,
            status=ProtocolCard.Status.DUE,
            due_in=-1,
            can_be_snoozed=True,
        )

        perform_cpt_coding = {
            "system": CodeSystems.CPT,
            "code": "92250",
            "display": "Retinal examination (CPT: 92250)",
        }

        perform_command = PerformCommand(
            cpt_code=perform_cpt_coding,
        )

        icd10_codes = self._get_diabetes_diagnosis_codes(patient)

        refer_command = ReferCommand(
            service_provider=ServiceProvider(
                first_name="Referral",
                last_name="Ophthalmology",
                specialty="Ophthalmology",
                practice_name="Ophthalmology Referral Network",
                notes="Accepts Optometry as alternative specialty.",
            ),
            diagnosis_codes=icd10_codes,
            include_visit_note=False,
        )

        card.recommendations.append(
            perform_command.recommend(title="Perform retinal examination", button="Perform")
        )
        card.recommendations.append(
            refer_command.recommend(title="Refer for retinal examination", button="Refer")
        )

        return card.apply()
