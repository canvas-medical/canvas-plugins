import arrow

from canvas_sdk.commands import PerformCommand, ReferCommand
from canvas_sdk.commands.constants import CodeSystems, ServiceProvider
from canvas_sdk.effects import Effect
from canvas_sdk.effects.protocol_card.protocol_card import ProtocolCard
from canvas_sdk.events import EventType
from canvas_sdk.protocols import ClinicalQualityMeasure
from canvas_sdk.v1.data import Patient
from canvas_sdk.v1.data.condition import Condition, ConditionCoding
from canvas_sdk.value_set.v2022.condition import Diabetes #TODO: Update to v2026 when value set is updated
from canvas_sdk.v1.data.referral import ReferralReport
from canvas_sdk.value_set.v2022.intervention import (
    HospiceCareAmbulatory,
    PalliativeOrHospiceCare,
)
from logger import log


class CMS131v14DiabetesEyeExam(ClinicalQualityMeasure):
    class Meta:
        title = "Diabetes: Eye Exam"
        description = (
            "Patients 18-75 years of age with diabetes who have not had a retinal or "
            "dilated eye exam by an eye care professional."
        )
        version = "2025-05-08v14"
        information = "https://ecqi.healthit.gov/ecqm/ec/2026/cms0131v14"
        identifiers = ["CMS131v14"]
        types = ["CQM"]
        authors = ["National Committee for Quality Assurance"]
        references = [
            "American Diabetes Association. Microvascular complications and foot care. Sec. 10. In Standards of Medical Care in Diabetes 2017. Diabetes Care 2017;40(Suppl. 1):S88-S98"
        ]

    RESPONDS_TO = [
        EventType.Name(EventType.CONDITION_CREATED),
        EventType.Name(EventType.CONDITION_UPDATED),
    ]

    def _get_patient_id(self) -> str | None:
        try:
            target_id = self.event.target.id

            if self.event.type in [
                EventType.CONDITION_CREATED,
                EventType.CONDITION_UPDATED,
            ]:
                condition = Condition.objects.filter(id=target_id).select_related("patient").first()
                if condition and condition.patient:
                    return condition.patient.id
                log.warning(f"CMS131v14: Could not find patient for condition {target_id}")
                return None

            log.warning(f"CMS131v14: Unhandled event type {self.event.type}")

            return self.patient_id_from_target()

        except Exception as e:
            log.error(f"CMS131v14: Error getting patient ID: {str(e)}")
            return None

    def _is_diabetes_code(self, coding) -> bool:
        try:
            normalized_system = coding.system.replace("-", "").upper()
            normalized_code = coding.code.replace(".", "")

            if normalized_system == "ICD10" or normalized_system == "ICD10CM":
                diabetes_codes = getattr(Diabetes, "ICD10CM", set())
                diabetes_codes_normalized = {code.replace(".", "") for code in diabetes_codes}
                return normalized_code in diabetes_codes_normalized
            elif normalized_system == "SNOMEDCT" or normalized_system == "SNOMED":
                diabetes_codes = getattr(Diabetes, "SNOMEDCT", set())
                return coding.code in diabetes_codes

            return False

        except Exception as e:
            log.error(f"CMS131v14: Error checking if code is diabetes: {str(e)}")
            return False

    def _is_condition_diabetes(self, condition: Condition) -> bool:
        try:
            condition_codings = ConditionCoding.objects.filter(condition=condition)
            return any(self._is_diabetes_code(coding) for coding in condition_codings)
        except Exception as e:
            log.error(f"CMS131v14: Error checking if condition is diabetes: {str(e)}")
            return False

    def _should_remove_card(self, patient: Patient) -> bool:
        try:
            condition_id = self.event.target.id
            condition = Condition.objects.filter(id=condition_id).first()

            if not condition:
                log.warning(f"CMS131v14: Could not find condition {condition_id}")
                return False

            if not self._is_condition_diabetes(condition):
                log.info(f"CMS131v14: Condition {condition_id} is not diabetes, no action needed")
                return False

            if condition.entered_in_error:
                log.info(
                    f"CMS131v14: Diabetes condition {condition_id} marked as entered_in_error for patient {patient.id}"
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
            patient_id = self._get_patient_id()
            if not patient_id:
                log.warning("CMS131v14: Could not determine patient ID from event, skipping")
                return []

            log.info(f"CMS131v14: Processing event for patient_id={patient_id}")

            patient = Patient.objects.filter(id=patient_id).first()
            if not patient:
                log.warning(f"CMS131v14: Patient {patient_id} not found, skipping")
                return []

            if self._should_remove_card(patient):
                return [self._create_not_applicable_card(patient)]

            if not self._in_initial_population(patient):
                log.info(f"CMS131v14: Patient {patient_id} not in initial population")
                return [self._create_not_applicable_card(patient)]

            if not self._in_denominator(patient):
                log.info(f"CMS131v14: Patient {patient_id} excluded from denominator")
                return [self._create_not_applicable_card(patient)]

            if self._in_numerator(patient):
                log.info(f"CMS131v14: Patient {patient_id} meets numerator criteria")
                return [self._create_satisfied_card(patient)]
            else:
                log.info(f"CMS131v14: Patient {patient_id} does not meet numerator criteria")
                return [self._create_due_card(patient)]

        except Exception as e:
            log.error(f"Error in CMS131v14 protocol compute: {str(e)}")
            return []

    def _in_initial_population(self, patient: Patient) -> bool:
        if not self._check_age_18_to_75(patient):
            log.info(f"CMS131v14: Patient {patient.id} not in age 18-75 range")
            return False

        if not self._has_diabetes_diagnosis_overlapping_period(patient):
            return False

        if not self._has_eligible_encounter_in_period(patient):
            return False

        return True

    def _in_denominator(self, patient: Patient) -> bool:
        if not self._in_initial_population(patient):
            log.info(f"CMS131v14: Patient {patient.id} not in initial population")
            return False

        if self._has_hospice_care_in_period(patient)
            log.info(f"CMS131v14: Patient {patient.id} in hospice care")
            return False

        if self._is_age_66_plus_with_frailty(
            patient
        ) and self._has_advanced_illness_or_dementia_meds(patient):
            return False

        if self._is_age_66_plus_in_nursing_home(patient):
            return False

        if self._has_palliative_care_in_period(patient):
            return False

        if self._has_bilateral_absence_of_eyes(patient):
            return False

        return True

    def _in_numerator(self, patient: Patient) -> bool:
        if self._has_retinopathy_diagnosis_in_period(patient):
            return self._has_retinal_exam_by_eye_care_professional_in_period(patient)

        if self._has_retinal_exam_in_period_or_year_prior(patient):
            return True

        if self._has_autonomous_eye_exam_in_period(patient):
            return True

        if self._has_retinal_finding_with_severity_in_period(patient):
            return True

        if self._has_retinal_finding_no_severity_in_prior_year(patient):
            return True

        return False

    def _has_diabetes_diagnosis(self, patient: Patient) -> bool:
        try:
            diabetes_conditions = Condition.objects.for_patient(patient.id).active()

            log.info(
                f"CMS131v14: Found {diabetes_conditions.count()} active conditions for patient {patient.id}"
            )

            for condition in diabetes_conditions:
                for coding in condition.codings.all():
                    if self._is_diabetes_code(coding):
                        log.info(f"CMS131v14: Found diabetes diagnosis with code {coding.code}")
                        return True

            log.info(f"CMS131v14: No active diabetes diagnoses found for patient {patient.id}")
            return False

        except Exception as e:
            log.error(f"CMS131v14: Error checking diabetes diagnosis: {str(e)}")
            return False

    def _check_age_18_to_75(self, patient: Patient) -> bool:
        try:
            if not getattr(patient, "birth_date", None):
                log.info("CMS131v14: Missing birth_date; patient fails age check")
                return False

            birth_date = arrow.get(patient.birth_date)
            age_years = (self.now - birth_date).days // 365

            in_range = 18 <= age_years <= 75
            log.info(
                f"CMS131v14: Patient {patient.id} age {age_years} in 18-75 range={in_range}"
            )
            return in_range
        except Exception as e:
            log.error(f"CMS131v14: Error computing age: {str(e)}")
            return False

    def _has_diabetes_diagnosis_overlapping_period(self, patient: Patient) -> bool:
        try:
            diabetes_conditions = Condition.objects.for_patient(patient.id).active()

            for condition in diabetes_conditions:
                for coding in condition.codings.all():
                    if self._is_diabetes_code(coding):
                        return True

            return False

        except Exception as e:
            log.error(f"CMS131v14: Error checking diabetes diagnosis overlapping period: {str(e)}")
            return False

    def _has_eligible_encounter_in_period(self, patient: Patient) -> bool:
        return True

    def _has_hospice_care_in_period(self, patient: Patient) -> bool:
        """
        Check if patient is in hospice or palliative care during the measurement period.

        Checks for:
        - Referral reports to hospice/palliative care services
        - Active condition codings against hospice value sets
        """
        try:
            # Check for hospice/palliative care referral reports
            hospice_reports = ReferralReport.objects.filter(
                patient=patient,
                junked=False,
                original_date__gte=self.timeframe.start.date(),
                original_date__lte=self.timeframe.end.date(),
            ).all()

            # Check if any reports are for hospice specialties
            hospice_specialties = {"Hospice", "Palliative Care", "Palliative Medicine"}
            for report in hospice_reports:
                if report.specialty and any(
                    hospice_specialty.lower() in report.specialty.lower()
                    for hospice_specialty in hospice_specialties
                ):
                    log.info(
                        f"CMS131v14: Found hospice referral report for patient {patient.id}"
                    )
                    return True

            # Additionally check condition codings against hospice value sets
            return self._patient_has_any_code_in_value_sets(
                patient,
                [PalliativeOrHospiceCare, HospiceCareAmbulatory],
            )
        except Exception as e:
            log.error(f"CMS131v14: Error checking hospice status: {str(e)}")
            return False

    def _is_age_66_plus_with_frailty(self, patient: Patient) -> bool:
        return False

    def _has_advanced_illness_or_dementia_meds(self, patient: Patient) -> bool:
        return False

    def _is_age_66_plus_in_nursing_home(self, patient: Patient) -> bool:
        return False

    def _has_palliative_care_in_period(self, patient: Patient) -> bool:
        return False

    def _has_bilateral_absence_of_eyes(self, patient: Patient) -> bool:
        return False

    def _has_retinopathy_diagnosis_in_period(self, patient: Patient) -> bool:
        return False

    def _has_retinal_exam_by_eye_care_professional_in_period(self, patient: Patient) -> bool:
        return False

    def _has_retinal_exam_in_period_or_year_prior(self, patient: Patient) -> bool:
        return False

    def _has_autonomous_eye_exam_in_period(self, patient: Patient) -> bool:
        return False

    def _has_retinal_finding_with_severity_in_period(self, patient: Patient) -> bool:
        return False

    def _has_retinal_finding_no_severity_in_prior_year(self, patient: Patient) -> bool:
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
            diabetes_conditions = Condition.objects.for_patient(patient.id).active()

            for condition in diabetes_conditions:
                for coding in condition.codings.all():
                    if self._is_diabetes_code(coding):
                        normalized_code = coding.code.replace(".", "")
                        diagnosis_codes.append(normalized_code)

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

    def _patient_has_any_code_in_value_sets(
        self, patient: Patient, value_set_classes: list
    ) -> bool:
        """
        Helper to check if patient has any active condition coding present in given value sets.
        
        Args:
            patient: The patient to check
            value_set_classes: List of value set classes (e.g., [PalliativeOrHospiceCare, HospiceCareAmbulatory])
        
        Returns:
            True if any active condition coding matches any of the value sets
        """
        try:
            conditions = Condition.objects.for_patient(patient.id).active()

            for condition in conditions:
                for coding in condition.codings.all():
                    for value_set_class in value_set_classes:
                        if self._coding_in_value_set(coding, value_set_class):
                            log.info(
                                f"CMS131v14: Found matching code {coding.code} in value set for patient {patient.id}"
                            )
                            return True

            return False
        except Exception as e:
            log.error(f"CMS131v14: Error checking codes in value sets: {str(e)}")
            return False

    def _coding_in_value_set(self, coding: ConditionCoding, value_set_class) -> bool:
        """
        Helper to check if a single coding belongs to a value set.
        
        Args:
            coding: The ConditionCoding to check
            value_set_class: Value set class to check against
        
        Returns:
            True if the coding is found in the value set
        """
        try:
            # Normalize the coding system for comparison
            normalized_system = coding.system.replace("-", "").upper()

            # Check common coding systems
            if normalized_system in ["ICD10", "ICD10CM"]:
                codes = getattr(value_set_class, "ICD10CM", set())
                normalized_code = coding.code.replace(".", "")
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

            return False
        except Exception as e:
            log.error(f"CMS131v14: Error checking coding in value set: {str(e)}")
            return False
            
