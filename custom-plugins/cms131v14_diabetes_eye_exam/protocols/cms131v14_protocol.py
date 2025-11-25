import datetime
from typing import Any

import arrow
from django.db.models import Q

from canvas_sdk.commands import PerformCommand, ReferCommand
from canvas_sdk.commands.constants import CodeSystems, Coding, ServiceProvider
from canvas_sdk.effects import Effect
from canvas_sdk.effects.protocol_card.protocol_card import ProtocolCard
from canvas_sdk.events import EventType
from canvas_sdk.protocols import ClinicalQualityMeasure
from canvas_sdk.v1.data import Patient
from canvas_sdk.v1.data.claim_line_item import ClaimLineItem
from canvas_sdk.v1.data.condition import Condition
from canvas_sdk.v1.data.device import Device
from canvas_sdk.v1.data.encounter import Encounter
from canvas_sdk.v1.data.medication import Medication
from canvas_sdk.v1.data.observation import Observation
from canvas_sdk.v1.data.referral import ReferralReport
from canvas_sdk.value_set.v2026.communication import (
    AutonomousEyeExamResultOrFinding,
    DiabeticRetinopathySeverityLevel,
)
from canvas_sdk.value_set.v2026.condition import (
    AdvancedIllness,
    Diabetes,
    DiabeticRetinopathy,
    FrailtyDiagnosis,
    HospiceDiagnosis,
    PalliativeCareDiagnosis,
)
from canvas_sdk.value_set.v2026.device import FrailtyDevice
from canvas_sdk.value_set.v2026.encounter import (
    AnnualWellnessVisit,
    CareServicesInLongTermResidentialFacility,
    FrailtyEncounter,
    HomeHealthcareServices,
    HospiceEncounter,
    NursingFacilityVisit,
    OfficeVisit,
    OphthalmologicalServices,
    PalliativeCareEncounter,
    PreventiveCareServicesEstablishedOfficeVisit18AndUp,
    PreventiveCareServicesInitialOfficeVisit18AndUp,
    TelephoneVisits,
)
from canvas_sdk.value_set.v2026.intervention import (
    HospiceCareAmbulatory,
    PalliativeCareIntervention,
)
from canvas_sdk.value_set.v2026.medication import DementiaMedications
from canvas_sdk.value_set.v2026.physical_exam import RetinalOrDilatedEyeExam
from canvas_sdk.value_set.v2026.symptom import FrailtySymptom
from logger import log


class CMS131v14DiabetesEyeExam(ClinicalQualityMeasure):
    """CMS131v14 Diabetes: Eye Exam clinical quality measure."""

    class Meta:
        title = "Diabetes: Eye Exam"
        description = "Percentage of patients 18-75 years of age with diabetes and an active diagnosis of retinopathy in any part of the measurement period who had a retinal or dilated eye exam by an eye care professional during the measurement period or diabetics with no diagnosis of retinopathy in any part of the measurement period who had a retinal or dilated eye exam by an eye care professional during the measurement period or in the 12 months prior to the measurement period"
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
            "Parker E, Lin J, Mahoney T, et al. Economic Costs of Diabetes in the U.S. in 2022. Diabetes Care. 2024;47(1):26-43. doi:10.2337/dci23-0085",
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
    ]

    # Age range constants
    AGE_RANGE_START = 18
    AGE_RANGE_END = 75

    LOINC_SYSTEM_IDENTIFIERS = ["http://loinc.org", "LOINC"]

    NO_APPARENT_RETINOPATHY_LOINC_CODE = "LA18643-9"
    LEFT_EYE_LOINC_CODE = "71490-7"
    RIGHT_EYE_LOINC_CODE = "71491-5"
    AUTONOMOUS_EYE_EXAM_LOINC_CODE = "105914-6"

    # Additional encounter type SNOMED codes from api_notetype
    # These supplement the value sets to capture additional qualifying encounters
    ADDITIONAL_ENCOUNTER_SNOMED_CODES = {
        "308335008",  # Follow-up encounter
        "439708006",  # Home visit
        "185317003",  # Telephone encounter
    }

    # Hospice discharge disposition codes per CMS131v14 CQL
    DISCHARGE_TO_HOME_HOSPICE_SNOMED = "428361000124107"
    DISCHARGE_TO_FACILITY_HOSPICE_SNOMED = "428371000124100"

    # Bilateral absence of eyes diagnostic code
    BILATERAL_ANOPHTHALMOS_SNOMED = "15665641000119103"

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
                    log.info("CMS131v14: No other diabetes diagnoses found, removing card")
                    return True
                else:
                    log.info("CMS131v14: Patient still has other diabetes diagnoses, keeping card")
                    return False

            return False

        except Exception as e:
            log.error(f"CMS131v14: Error checking if card should be removed: {str(e)}")
            return False

    def _build_period_overlap_query(self, start_date: datetime.date, end_date: datetime.date) -> Q:
        """
        Build query for conditions whose prevalencePeriod overlaps given period.

        Per CMS131v14 and Canvas convention: A condition overlaps if:
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

    def _get_value_set_codes(self, value_set: Any, *attributes: str) -> set[str]:
        """
        Safely retrieve and combine codes from value set attributes.

        Args:
            value_set: The value set class to retrieve codes from
            *attributes: One or more attribute names (e.g., 'SNOMEDCT', 'ICD10CM', 'CPT')

        Returns:
            Set of codes from all specified attributes, empty set if none exist
        """
        codes = set()
        for attr in attributes:
            attr_value = getattr(value_set, attr, None)
            if attr_value:
                codes |= attr_value
        return codes

    def compute(self) -> list[Effect]:
        """Main compute method for CMS131v14 Diabetes Eye Exam measure."""
        try:
            patient, condition = self._get_patient()
            if not patient:
                log.warning("CMS131v14: Could not determine patient from event, skipping")
                return []

            log.debug(f"CMS131v14: Processing event for patient_id={patient.id}")

            if self._should_remove_card(patient, condition):
                log.info("CMS131v14: Removing card")
                return [self._create_not_applicable_card(patient)]

            # Calculate age
            age = int(patient.age_at(self.timeframe.end))

            if not self._in_initial_population(patient, age):
                log.debug(f"CMS131v14: Patient {patient.id} not in initial population")
                return [self._create_not_applicable_card(patient)]

            if not self._in_denominator(patient, age):
                log.info(f"CMS131v14: Patient {patient.id} excluded from denominator")
                return [self._create_not_applicable_card(patient)]

            if self._in_numerator(patient):
                log.info(f"CMS131v14: Created SATISFIED card for patient {patient.id}")
                return [self._create_satisfied_card(patient)]
            else:
                log.info(f"CMS131v14: Created DUE card for patient {patient.id}")
                return [self._create_due_card(patient)]

        except Exception as e:
            log.error(f"Error in CMS131v14 protocol compute: {str(e)}")
            return []

    def _in_initial_population(self, patient: Patient, age: int) -> bool:
        if not (self.AGE_RANGE_START <= age <= self.AGE_RANGE_END):
            log.info(f"CMS131v14: Patient {patient.id} age {age} not in 18-75 range")
            return False

        if not self._has_diabetes_diagnosis_overlapping_period(patient):
            log.info(
                f"CMS131v14: Patient {patient.id} does not have diabetes diagnosis overlapping period"
            )
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
            log.info(
                f"CMS131v14: Patient {patient.id} is age 66+ with frailty and advanced illness or dementia meds"
            )
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
            log.info(
                f"CMS131v14: Found autonomous eye exam in measurement period for patient {patient.id}"
            )
            return True

        if self._has_retinal_finding_with_severity_in_period(patient):
            return True

        return bool(self._has_retinal_finding_no_severity_in_prior_year(patient))

    def _has_diabetes_diagnosis(self, patient: Patient) -> bool:
        try:
            diabetes_conditions = (
                Condition.objects.for_patient(patient.id)  # type: ignore[attr-defined]
                .find(Diabetes)
                .active()
                .filter(entered_in_error_id__isnull=True)
            )

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
        """
        Check if patient has diabetes diagnosis with prevalencePeriod overlapping measurement period.

        Per CMS131v14: DiabetesDx.prevalencePeriod overlaps day of "Measurement Period"

        A condition's prevalencePeriod overlaps with measurement period if:
        - Condition started before or during the measurement period (onset_date <= period_end)
        - AND condition has not ended or ended during/after measurement period start
          (resolution_date is null OR resolution_date >= period_start)

        Per Canvas convention: If onset_date is NULL, the condition is treated as overlapping
        with the measurement period (following the pattern in helper_date_ranges_overlap).
        """
        try:
            measurement_start = self.timeframe.start.date()
            measurement_end = self.timeframe.end.date()

            # Build overlap query using helper method
            overlap_query = self._build_period_overlap_query(measurement_start, measurement_end)

            has_overlap = (
                Condition.objects.for_patient(patient.id)  # type: ignore[attr-defined]
                .find(Diabetes)
                .committed()
                .filter(entered_in_error_id__isnull=True)
                .filter(overlap_query)
                .exists()
            )

            if has_overlap:
                log.info(
                    f"CMS131v14: Patient {patient.id} has diabetes diagnosis overlapping measurement period"
                )
            else:
                log.info(
                    f"CMS131v14: Patient {patient.id} does NOT have diabetes diagnosis overlapping measurement period"
                )

            return has_overlap

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

            # Additional SNOMED codes from api_notetype supplement the value sets
            encounter_snomed_codes = (
                self.ADDITIONAL_ENCOUNTER_SNOMED_CODES
                | OfficeVisit.SNOMEDCT
                | AnnualWellnessVisit.SNOMEDCT
                | HomeHealthcareServices.SNOMEDCT
                | OphthalmologicalServices.SNOMEDCT
                | TelephoneVisits.SNOMEDCT
            )

            eligible_encounters = Encounter.objects.filter(
                note__patient=patient,
                note__note_type_version__code__in=encounter_snomed_codes,
                state__in=["CON", "STA"],
                start_time__gte=start_date,
                start_time__lte=end_date,
            )

            if eligible_encounters.exists():
                encounter = eligible_encounters.first()
                if encounter and encounter.note and encounter.note.note_type_version:
                    log.info(
                        f"CMS131v14: Patient {patient.id} has eligible encounter "
                        f"via Encounter model (SNOMED: {encounter.note.note_type_version.code})"
                    )
                else:
                    log.info(
                        f"CMS131v14: Patient {patient.id} has eligible encounter via Encounter model"
                    )
                return True

            # Check for encounters/services via claims as fallback
            # Collect all CPT and HCPCS codes from the relevant value sets
            # This catches encounters that may not be documented via Encounter model
            eligible_codes = (
                OfficeVisit.CPT
                | AnnualWellnessVisit.HCPCSLEVELII
                | PreventiveCareServicesEstablishedOfficeVisit18AndUp.CPT
                | PreventiveCareServicesInitialOfficeVisit18AndUp.CPT
                | HomeHealthcareServices.CPT
                | OphthalmologicalServices.CPT
                | TelephoneVisits.CPT
            )

            # Query ClaimLineItem for any of these codes during the measurement period
            eligible_claims = ClaimLineItem.objects.filter(
                claim__note__patient=patient,
                status="active",
                from_date__gte=self.timeframe.start.date().isoformat(),
                from_date__lte=self.timeframe.end.date().isoformat(),
                proc_code__in=eligible_codes,
            )

            if eligible_claims.exists():
                first_claim = eligible_claims.first()
                if first_claim:
                    log.info(
                        f"CMS131v14: Patient {patient.id} has eligible encounter claim (code: {first_claim.proc_code})"
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
                Condition.objects.for_patient(patient.id)  # type: ignore[attr-defined]
                .find(HospiceDiagnosis)
                .active()
                .filter(entered_in_error_id__isnull=True)
                .exists()
            )

            if has_hospice_diagnosis:
                log.info(f"CMS131v14: Found hospice diagnosis for patient {patient.id}")
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
                    log.info(f"CMS131v14: Found hospice encounter for patient {patient.id}")
                    return True

            # 3. Check for discharge to hospice via observations (discharge disposition)
            discharge_to_hospice_codes = {
                self.DISCHARGE_TO_HOME_HOSPICE_SNOMED,
                self.DISCHARGE_TO_FACILITY_HOSPICE_SNOMED,
            }

            has_discharge_to_hospice = (
                Observation.objects.for_patient(patient.id)  # type: ignore[attr-defined]
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
                log.info(f"CMS131v14: Found discharge to hospice for patient {patient.id}")
                return True

            # 4. Check for hospice care assessment (LOINC 45755-6 "Hospice care [Minimum Data Set]")
            has_hospice_assessment = (
                Observation.objects.for_patient(patient.id)  # type: ignore[attr-defined]
                .filter(
                    effective_datetime__gte=start_date,
                    effective_datetime__lte=end_date,
                    codings__code="45755-6",
                    codings__system__in=self.LOINC_SYSTEM_IDENTIFIERS,
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
                log.info(f"CMS131v14: Found hospice care assessment for patient {patient.id}")
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
                        f"CMS131v14: Found hospice care claim (code: {first_claim.proc_code}) for patient {patient.id}"
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

        Per CMS131v14 CQL "Has Criteria Indicating Frailty", checks for:
        - Device orders for frailty devices
        - Assessment observations with frailty device results
        - Frailty diagnoses overlapping measurement period
        - Frailty encounters overlapping measurement period
        - Frailty symptoms overlapping measurement period
        """
        # Check age requirement
        if age < 66:
            return False

        try:
            # Check all frailty indicators
            if self._has_frailty_device_orders(patient):
                log.info(f"CMS131v14: Patient {patient.id} age 66+ has frailty device orders")
                return True

            if self._has_frailty_device_observations(patient):
                log.info(f"CMS131v14: Patient {patient.id} age 66+ has frailty device observations")
                return True

            if self._has_frailty_diagnoses(patient):
                log.info(f"CMS131v14: Patient {patient.id} age 66+ has frailty diagnoses")
                return True

            if self._has_frailty_encounters(patient):
                log.info(f"CMS131v14: Patient {patient.id} age 66+ has frailty encounters")
                return True

            if self._has_frailty_symptoms(patient):
                log.info(f"CMS131v14: Patient {patient.id} age 66+ has frailty symptoms")
                return True

            return False
        except Exception as e:
            log.error(f"CMS131v14: Error checking frailty: {str(e)}")
            return False

    def _has_frailty_device_orders(self, patient: Patient) -> bool:
        """
        Check for device orders with frailty device codes during measurement period.

        Per CMS131v14: Device, Order: "Frailty Device" - authorDatetime during day of "Measurement Period".

        Note: Device model in SDK v1 doesn't have a note relationship, only note_id.
        We primarily check via ClaimLineItem for DME codes instead.
        """
        try:
            # Check ClaimLineItem for DME (Durable Medical Equipment) codes
            # FrailtyDevice value set contains HCPCS codes for DME
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
                    log.info(f"CMS131v14: Found frailty device DME claim for patient {patient.id}")
                    return True

            # Also check Device model for any ordered devices (no date filter due to SDK limitation)
            # This is a fallback check - less precise but catches device orders
            has_device_order = Device.objects.filter(
                patient=patient,
                status="ordered",
            ).exists()

            if has_device_order:
                log.info(f"CMS131v14: Found device order for patient {patient.id}")
                return True

            return False
        except Exception as e:
            log.error(f"CMS131v14: Error checking frailty device orders: {str(e)}")
            return False

    def _has_frailty_device_observations(self, patient: Patient) -> bool:
        """
        Check for observations with frailty device codes in value_codings during measurement period.

        Per CMS131v14: Assessment, Performed: "Medical equipment used" result in "Frailty Device".
        """
        try:
            # Get all SNOMED codes from FrailtyDevice value set
            frailty_device_snomed = self._get_value_set_codes(FrailtyDevice, "SNOMEDCT")

            if not frailty_device_snomed:
                return False

            # Check for observations with frailty device codes as value codings
            # Include observations with null effective_datetime or within the measurement period
            has_observation = (
                Observation.objects.for_patient(patient.id)  # type: ignore[attr-defined]
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
                log.info(f"CMS131v14: Found frailty device observation for patient {patient.id}")
                return True

            return False
        except Exception as e:
            log.error(f"CMS131v14: Error checking frailty device observations: {str(e)}")
            return False

    def _has_frailty_diagnoses(self, patient: Patient) -> bool:
        """
        Check for frailty diagnoses overlapping measurement period.

        Per CMS131v14: Diagnosis: "Frailty Diagnosis" - prevalencePeriod overlaps day of "Measurement Period".
        """
        try:
            measurement_start = self.timeframe.start.date()
            measurement_end = self.timeframe.end.date()

            # Build overlap query using helper method
            overlap_query = self._build_period_overlap_query(measurement_start, measurement_end)

            has_frailty_diagnosis = (
                Condition.objects.for_patient(patient.id)  # type: ignore[attr-defined]
                .find(FrailtyDiagnosis)
                .committed()
                .filter(entered_in_error_id__isnull=True)
                .filter(overlap_query)
                .exists()
            )

            if has_frailty_diagnosis:
                log.info(f"CMS131v14: Found frailty diagnosis for patient {patient.id}")

            return has_frailty_diagnosis
        except Exception as e:
            log.error(f"CMS131v14: Error checking frailty diagnoses: {str(e)}")
            return False

    def _has_frailty_encounters(self, patient: Patient) -> bool:
        """
        Check for frailty encounters during measurement period.

        Per CMS131v14: Encounter, Performed: "Frailty Encounter" - relevantPeriod overlaps day of "Measurement Period".
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
                        f"CMS131v14: Found frailty encounter (SNOMED) for patient {patient.id}"
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
                    log.info(f"CMS131v14: Found frailty encounter (claim) for patient {patient.id}")
                    return True

            return False
        except Exception as e:
            log.error(f"CMS131v14: Error checking frailty encounters: {str(e)}")
            return False

    def _has_frailty_symptoms(self, patient: Patient) -> bool:
        """
        Check for frailty symptoms overlapping measurement period.

        Per CMS131v14: Symptom: "Frailty Symptom" - prevalencePeriod overlaps day of "Measurement Period".

        Note: SDK v1 doesn't expose the 'notes' field on Condition.
        We check for frailty symptom codes without differentiating symptoms from diagnoses.
        """
        try:
            measurement_start = self.timeframe.start.date()
            measurement_end = self.timeframe.end.date()

            # Build overlap query using helper method
            overlap_query = self._build_period_overlap_query(measurement_start, measurement_end)

            has_frailty_symptom = (
                Condition.objects.for_patient(patient.id)  # type: ignore[attr-defined]
                .find(FrailtySymptom)
                .committed()
                .filter(entered_in_error_id__isnull=True)
                .filter(overlap_query)
                .exists()
            )

            if has_frailty_symptom:
                log.info(f"CMS131v14: Found frailty symptom for patient {patient.id}")

            return has_frailty_symptom
        except Exception as e:
            log.error(f"CMS131v14: Error checking frailty symptoms: {str(e)}")
            return False

    def _has_advanced_illness_or_dementia_meds(self, patient: Patient) -> bool:
        """
        Check if patient has advanced illness or dementia medications.

        Per CMS131v14 CQL:
        - Advanced illness diagnosis that starts during the measurement period or the year prior
        - OR taking dementia medications during the measurement period or the year prior.
        """
        try:
            start_date = self.timeframe.start.shift(years=-1).date()
            end_date = self.timeframe.end.date()

            # Check for advanced illness conditions in measurement period or year prior
            # Note: Intentionally not using .committed() to include uncommitted advanced illness conditions
            # per CMS131v14 interpretation for early detection of frailty exclusion criteria
            has_advanced_illness = (
                Condition.objects.for_patient(patient.id)  # type: ignore[attr-defined]
                .find(AdvancedIllness)
                .filter(
                    Q(onset_date__isnull=True)  # Include conditions with NULL onset date
                    | Q(onset_date__lte=end_date, onset_date__gte=start_date)
                )
                .filter(entered_in_error_id__isnull=True)
                .exists()
            )

            if has_advanced_illness:
                log.info(f"CMS131v14: Patient {patient.id} has advanced illness")
                return True

            # Convert dates to datetime for efficient comparison (avoids __date lookups that prevent index usage)
            start_datetime = arrow.get(start_date).datetime
            end_datetime = (
                arrow.get(end_date)
                .replace(hour=23, minute=59, second=59, microsecond=999999)
                .datetime
            )

            has_dementia_meds = (
                Medication.objects.for_patient(patient.id)  # type: ignore[attr-defined]
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
            # Get codes from the value sets
            # NursingFacilityVisit has CPT codes, CareServicesInLongTermResidentialFacility has SNOMED
            nursing_facility_cpt = self._get_value_set_codes(NursingFacilityVisit, "CPT")
            nursing_facility_snomed = self._get_value_set_codes(NursingFacilityVisit, "SNOMEDCT")
            long_term_care_snomed = self._get_value_set_codes(
                CareServicesInLongTermResidentialFacility, "SNOMEDCT"
            )

            # Combine all codes for claims (CPT/HCPCS)
            all_claim_codes = nursing_facility_cpt

            # Check for claim line items with CPT codes
            if all_claim_codes:
                claim_line_items = ClaimLineItem.objects.filter(
                    claim__note__patient=patient,
                    status="active",
                    from_date__gte=self.timeframe.start.date().isoformat(),
                    from_date__lte=self.timeframe.end.date().isoformat(),
                    proc_code__in=all_claim_codes,
                )

                if claim_line_items.exists():
                    first_claim = claim_line_items.first()
                    if first_claim:
                        log.info(
                            f"CMS131v14: Patient {patient.id} age 66+ has nursing home/long-term care claim (CPT: {first_claim.proc_code})"
                        )
                    return True

            # Also check for encounters with SNOMED codes
            all_snomed_codes = nursing_facility_snomed | long_term_care_snomed
            if all_snomed_codes:
                encounters = Encounter.objects.filter(
                    note__patient=patient,
                    note__note_type_version__code__in=all_snomed_codes,
                    state__in=["CON", "STA"],
                    start_time__gte=self.timeframe.start.datetime,
                    start_time__lte=self.timeframe.end.datetime,
                )

                if encounters.exists():
                    log.info(
                        f"CMS131v14: Patient {patient.id} age 66+ has nursing home/long-term care encounter"
                    )
                    return True

            return False
        except Exception as e:
            log.error(f"CMS131v14: Error checking nursing home status: {str(e)}")
            return False

    def _has_palliative_care_in_period(self, patient: Patient) -> bool:
        """
        Check if the patient received palliative care during the measurement period.

        Per CMS131v14 CQL, checks for:
        - Palliative Care Assessment (LOINC 71007-9) - Note: May not be captured in standard Canvas data
        - Palliative Care Diagnosis (ICD-10, SNOMED)
        - Palliative Care Encounter (CPT, HCPCS, SNOMED, ICD-10)
        - Palliative Care Intervention (SNOMED)
        """
        try:
            start_date = self.timeframe.start.datetime
            end_date = self.timeframe.end.datetime

            # Check palliative care diagnoses (using Condition model)
            has_palliative_diagnosis = (
                Condition.objects.for_patient(patient.id)  # type: ignore[attr-defined]
                .find(PalliativeCareDiagnosis)
                .active()
                .filter(entered_in_error_id__isnull=True)
                .exists()
            )

            if has_palliative_diagnosis:
                log.info(f"CMS131v14: Found palliative care diagnosis for patient {patient.id}")
                return True

            # Check for Palliative Care Assessment (LOINC 71007-9)
            # Per CMS131v14: Assessment, Performed: "Functional Assessment of Chronic Illness Therapy - Palliative Care Questionnaire (FACIT-Pal)"
            has_palliative_assessment = self._observation_exists(
                patient=patient,
                codings_code="71007-9",
                value_codings_codes=set(),  # No specific value required for this assessment
                timeframe_start=self.timeframe.start.datetime,
                timeframe_end=self.timeframe.end.datetime,
            )

            if has_palliative_assessment:
                log.info(
                    f"CMS131v14: Found palliative care assessment (LOINC 71007-9) for patient {patient.id}"
                )
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
                    log.info(f"CMS131v14: Found palliative care encounter for patient {patient.id}")
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
                        f"CMS131v14: Found palliative care claim (code: {first_claim.proc_code}) for patient {patient.id}"
                    )
                return True

            return False
        except Exception as e:
            log.error(f"CMS131v14: Error checking palliative care: {str(e)}")
            return False

    def _has_bilateral_absence_of_eyes(self, patient: Patient) -> bool:
        """Check for bilateral absence of eyes."""
        # https://www.ncbi.nlm.nih.gov/medgen/768661
        # Bilateral anophthalmos of eyes
        # Synonyms:
        # Anophthalmos of bilateral eyes
        # Anophthalmos of both eyes
        # Bilateral Anophthalmos
        # Bilateral anophthalmos
        # SNOMED CT:
        # Anophthalmos of bilateral eyes (15665641000119103)
        # Anophthalmos of both eyes (15665641000119103)
        # Bilateral anophthalmos (15665641000119103)
        # Bilateral anophthalmos of eyes (15665641000119103)
        try:
            measurement_end = self.timeframe.end.date()

            has_bilateral_absence = (
                Condition.objects.for_patient(patient.id)  # type: ignore[attr-defined]
                .active()
                .filter(
                    entered_in_error_id__isnull=True,
                    codings__code=self.BILATERAL_ANOPHTHALMOS_SNOMED,
                    codings__system__in=["SNOMED", "SNOMEDCT"],
                )
                .filter(Q(onset_date__isnull=True) | Q(onset_date__lte=measurement_end))
                .exists()
            )

            if has_bilateral_absence:
                log.info(
                    f"CMS131v14: Found bilateral eye absence (SNOMED {self.BILATERAL_ANOPHTHALMOS_SNOMED}) "
                    f"starting on or before {measurement_end} for patient {patient.id}"
                )

            return has_bilateral_absence

        except Exception as e:
            log.error(f"CMS131v14: Error checking bilateral eye absence: {str(e)}")
            return False

    def _has_retinopathy_diagnosis_in_period(self, patient: Patient) -> bool:
        """Check for retinopathy diagnosis in period."""
        try:
            has_retinopathy_diagnosis = (
                Condition.objects.for_patient(patient.id)  # type: ignore[attr-defined]
                .find(DiabeticRetinopathy)
                .filter(onset_date__gte=self.timeframe.start.date())
                .filter(onset_date__lte=self.timeframe.end.date())
                .filter(entered_in_error_id__isnull=True)
                .exists()
            )

            return has_retinopathy_diagnosis

        except Exception as e:
            log.error(f"CMS131v14: Error checking retinopathy diagnosis: {str(e)}")
            return False

    def _referral_report_exists(
        self,
        patient: Patient,
        timeframe_start: datetime.datetime,
        timeframe_end: datetime.datetime,
    ) -> bool:
        """
        Check if eye exam referral report exists in specified timeframe.

        Checks for referrals with SNOMEDCT codes from RetinalOrDilatedEyeExam value set.
        """
        try:
            # Get SNOMED codes from RetinalOrDilatedEyeExam value set
            eye_exam_codes = self._get_value_set_codes(RetinalOrDilatedEyeExam, "SNOMEDCT")

            if eye_exam_codes:
                # Filter by codings using the new relationship
                referral_reports = ReferralReport.objects.filter(
                    patient=patient,
                    original_date__gte=timeframe_start,
                    original_date__lt=timeframe_end,
                    codings__code__in=eye_exam_codes,
                )

                if referral_reports.exists():
                    return True

            # Fallback: use specialty field for cases without coding
            referral_reports = ReferralReport.objects.filter(
                patient=patient,
                original_date__gte=timeframe_start,
                original_date__lt=timeframe_end,
            ).filter(
                Q(specialty__icontains="ophthalmol")
                | Q(specialty__icontains="optometr")
                | Q(specialty__icontains="retina")
                | Q(specialty__icontains="eye")
            )

            return referral_reports.exists()

        except Exception as e:
            log.error(f"CMS131v14: Error checking referral report in period: {str(e)}")
            return False

    def _has_retinal_exam_in_period(self, patient: Patient) -> bool:
        """Check for retinal or dilated eye exam in measurement period."""
        try:
            referral_reports = self._referral_report_exists(
                patient, self.timeframe.start.datetime, self.timeframe.end.datetime
            )

            return referral_reports

        except Exception as e:
            log.error(f"CMS131v14: Error checking retinal exam in period: {str(e)}")
            return False

    def _has_retinal_exam_in_period_or_year_prior(self, patient: Patient) -> bool:
        """Check for retinal or dilated eye exam in measurement period OR year prior."""
        try:
            extended_start = self.timeframe.start.shift(years=-1)
            referral_reports = self._referral_report_exists(
                patient, extended_start.datetime, self.timeframe.end.datetime
            )

            return referral_reports

        except Exception as e:
            log.error(f"CMS131v14: Error checking retinal exam in period or year prior: {str(e)}")
            return False

    def _observation_exists(
        self,
        patient: Patient,
        codings_code: str,
        value_codings_codes: set[str],
        timeframe_start: datetime.datetime,
        timeframe_end: datetime.datetime,
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
                Observation.objects.for_patient(patient.id)  # type: ignore[attr-defined]
                .committed()
                .filter(date_filter, code_filter)
            )

            return observations.exists()

        except Exception as e:
            log.error(
                f"CMS131v14: Error checking observation for code {codings_code} and value codes {value_codings_codes}: {str(e)}"
            )
            return False

    def _has_autonomous_eye_exam_in_period(self, patient: Patient) -> bool:
        """Check for autonomous AI eye exam with valid result in measurement period."""
        try:
            result_codes = AutonomousEyeExamResultOrFinding.LOINC

            has_exam = self._observation_exists(
                patient,
                self.AUTONOMOUS_EYE_EXAM_LOINC_CODE,
                result_codes,
                self.timeframe.start.datetime,
                self.timeframe.end.datetime,
            )

            return has_exam

        except Exception as e:
            log.error(f"CMS131v14: Error checking autonomous eye exam: {str(e)}")
            return False

    def _has_retinal_finding_with_severity_in_period(self, patient: Patient) -> bool:
        """Check for retinal exam findings with retinopathy severity level in measurement period."""
        try:
            measurement_start = self.timeframe.start.datetime
            measurement_end = self.timeframe.end.datetime

            severity_codes = DiabeticRetinopathySeverityLevel.LOINC
            left_eye_retinopathy = self._observation_exists(
                patient,
                self.LEFT_EYE_LOINC_CODE,
                severity_codes,
                measurement_start,
                measurement_end,
            )
            right_eye_retinopathy = self._observation_exists(
                patient,
                self.RIGHT_EYE_LOINC_CODE,
                severity_codes,
                measurement_start,
                measurement_end,
            )

            if left_eye_retinopathy and right_eye_retinopathy:
                log.info(f"CMS131v14: Both eyes have retinopathy severity for patient {patient.id}")
                return True

            prior_year_start = self.timeframe.start.shift(years=-1).datetime
            prior_year_end = self.timeframe.start.datetime

            left_eye_no_retinopathy_prior = self._observation_exists(
                patient,
                self.LEFT_EYE_LOINC_CODE,
                {self.NO_APPARENT_RETINOPATHY_LOINC_CODE},
                prior_year_start,
                prior_year_end,
            )
            right_eye_no_retinopathy_prior = self._observation_exists(
                patient,
                self.RIGHT_EYE_LOINC_CODE,
                {self.NO_APPARENT_RETINOPATHY_LOINC_CODE},
                prior_year_start,
                prior_year_end,
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
                patient,
                self.LEFT_EYE_LOINC_CODE,
                {self.NO_APPARENT_RETINOPATHY_LOINC_CODE},
                prior_year_start,
                prior_year_end,
            )
            right_eye_no_retinopathy = self._observation_exists(
                patient,
                self.RIGHT_EYE_LOINC_CODE,
                {self.NO_APPARENT_RETINOPATHY_LOINC_CODE},
                prior_year_start,
                prior_year_end,
            )

            if left_eye_no_retinopathy and right_eye_no_retinopathy:
                log.info(
                    f"CMS131v14: Both eyes have no retinopathy in year prior for patient {patient.id}"
                )
                return True

            return False

        except Exception as e:
            log.error(
                f"CMS131v14: Error checking retinal finding no severity in prior year: {str(e)}"
            )
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

            diabetes_conditions = (
                Condition.objects.for_patient(patient.id)  # type: ignore[attr-defined]
                .find(Diabetes)
                .active()
                .filter(entered_in_error_id__isnull=True)
            )

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

        perform_cpt_coding: Coding = {
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
