import datetime
from typing import Any

import arrow
from django.db.models import Q

from canvas_sdk.commands import InstructCommand, LabOrderCommand
from canvas_sdk.commands.constants import CodeSystems
from canvas_sdk.effects import Effect
from canvas_sdk.effects.protocol_card.protocol_card import ProtocolCard
from canvas_sdk.events import EventType
from canvas_sdk.protocols import ClinicalQualityMeasure
from canvas_sdk.v1.data import Patient
from canvas_sdk.v1.data.claim_line_item import ClaimLineItem
from canvas_sdk.v1.data.condition import Condition
from canvas_sdk.v1.data.device import Device
from canvas_sdk.v1.data.encounter import Encounter
from canvas_sdk.v1.data.lab import LabReport
from canvas_sdk.v1.data.medication import Medication
from canvas_sdk.v1.data.note import Note
from canvas_sdk.v1.data.observation import Observation
from canvas_sdk.value_set.v2026.condition import (
    AdvancedIllness,
    Diabetes,
    FrailtyDiagnosis,
    HospiceDiagnosis,
    PalliativeCareDiagnosis,
)
from canvas_sdk.value_set.v2026.device import FrailtyDevice
from canvas_sdk.value_set.v2026.encounter import (
    AnnualWellnessVisit,
    CareServicesInLongTermResidentialFacility,
    EncounterInpatient,
    FrailtyEncounter,
    HomeHealthcareServices,
    HospiceEncounter,
    NursingFacilityVisit,
    NutritionServices,
    OfficeVisit,
    PalliativeCareEncounter,
    PreventiveCareServicesEstablishedOfficeVisit18AndUp,
    PreventiveCareServicesInitialOfficeVisit18AndUp,
    TelephoneVisits,
)
from canvas_sdk.value_set.v2026.intervention import (
    DietaryRecommendations,
    HospiceCareAmbulatory,
    PalliativeCareIntervention,
)
from canvas_sdk.value_set.v2026.laboratory_test import Hba1cLaboratoryTest
from canvas_sdk.value_set.v2026.medication import DementiaMedications
from canvas_sdk.value_set.v2026.symptom import FrailtySymptom
from cms122v14_diabetes_hemoglobin_a1c_poor_control.constants import (
    ADDITIONAL_ENCOUNTER_SNOMED_CODES,
    AGE_RANGE_END,
    AGE_RANGE_START,
    DISCHARGE_TO_FACILITY_HOSPICE_SNOMED,
    DISCHARGE_TO_HOME_HOSPICE_SNOMED,
    GLYCEMIC_THRESHOLD,
    GMI_LOINC_CODE,
    HOSPICE_MDS_LOINC,
    HOUSING_STATUS_LOINC,
    LIVES_IN_NURSING_HOME_SNOMED,
    LOINC_SYSTEM_IDENTIFIERS,
    MNT_CPT_CODES,
    MNT_HCPCS_CODES,
    PALLIATIVE_CARE_ASSESSMENT_LOINC,
    PROTOCOL_KEY,
    SNOMED_SYSTEM_IDENTIFIERS,
    TEST_TYPE_GMI,
    TEST_TYPE_HBA1C,
    YES_QUALIFIER_SNOMED,
)
from logger import log


class CMS122v14DiabetesGlycemicStatusPoorControl(ClinicalQualityMeasure):
    """
    CMS122v14: Diabetes - Glycemic Status Assessment Greater Than 9%.

    Clinical Quality Measure for 2026 measurement period.

    Percentage of patients 18-75 years of age with diabetes who had a glycemic status
    assessment (HbA1c or GMI) > 9.0% during the measurement period.

    Key changes from v6:
    - Name: "Hemoglobin A1c Poor Control" -> "Glycemic Status Assessment Greater Than 9%"
    - Glycemic assessment now includes GMI (LOINC 97506-0) in addition to HbA1c
    - Requires qualifying encounter during measurement period
    - Expanded denominator exclusions: Hospice, Age 66+ Nursing Home,
      Age 66+ Frailty+Advanced Illness, Palliative Care
    - If multiple tests on same day, lowest result is used

    Guidance:
    - Patient is in numerator if most recent glycemic status > 9%, is missing, or has no result
    - Glycemic status = HbA1c OR GMI (Glucose Management Indicator)
    - If multiple tests on same day, the LOWEST result is used
    - Only Type 1 or Type 2 diabetes should be included (not secondary diabetes)

    More information: https://ecqi.healthit.gov/ecqm/ec/2026/cms0122v14
    """

    class Meta:
        title = "Diabetes: Glycemic Status Assessment Greater Than 9%"
        version = "2026-v14.0.000"
        description = (
            "Percentage of patients 18-75 years of age with diabetes who had a "
            "glycemic status assessment (HbA1c or GMI) > 9.0% during the measurement period"
        )
        information = "https://ecqi.healthit.gov/ecqm/ec/2026/cms0122v14"
        identifiers = ["CMS122v14"]
        types = ["CQM"]
        authors = ["National Committee for Quality Assurance"]
        references = [
            "American Diabetes Association. (2018). Economic Costs of Diabetes in the U.S. in 2017.",
            "American Diabetes Association. (2022a). Statistics About Diabetes.",
            "Centers for Disease Control and Prevention. (2022a). What is Diabetes?",
            "Centers for Disease Control and Prevention. (2022b). Diabetes Report Card 2021.",
            "ElSayed, N.A., et al. (2022). 6. Glycemic Targets: Standards of Care in Diabetes—2023.",
        ]

    RESPONDS_TO = [
        EventType.Name(EventType.CONDITION_CREATED),
        EventType.Name(EventType.CONDITION_UPDATED),
        EventType.Name(EventType.CONDITION_RESOLVED),
        EventType.Name(EventType.LAB_REPORT_CREATED),
        EventType.Name(EventType.LAB_REPORT_UPDATED),
        EventType.Name(EventType.PATIENT_CREATED),
        EventType.Name(EventType.PATIENT_UPDATED),
        EventType.Name(EventType.OBSERVATION_CREATED),
        EventType.Name(EventType.OBSERVATION_UPDATED),
        EventType.Name(EventType.ENCOUNTER_CREATED),
        EventType.Name(EventType.ENCOUNTER_UPDATED),
        EventType.Name(EventType.CLAIM_CREATED),
        EventType.Name(EventType.CLAIM_UPDATED),
        EventType.Name(EventType.PROTOCOL_OVERRIDE_CREATED),
        EventType.Name(EventType.PROTOCOL_OVERRIDE_UPDATED),
    ]

    def compute(self) -> list[Effect]:
        """Main compute method that determines protocol status and returns appropriate card."""
        try:
            patient, condition = self._get_patient_and_condition()
            if not patient:
                return []

            if self._should_remove_card(patient, condition):
                return [self._create_not_applicable_card(patient)]

            age = int(patient.age_at(self.timeframe.end))

            if not self._in_initial_population(patient, age):
                return [self._create_not_applicable_card(patient)]

            if not self._in_denominator(patient, age):
                return [self._create_not_applicable_card(patient)]

            if self._in_numerator(patient):
                return [self._create_satisfied_card(patient)]
            else:
                return [self._create_due_card(patient)]

        except Exception as e:
            log.error(f"CMS122v14: Error in compute: {str(e)}", exc_info=True)
            return []

    def _get_patient_and_condition(self) -> tuple[Patient | None, Condition | None]:
        """Get patient from event based on event type."""
        target_id = self.event.target.id

        if self.event.type in [
            EventType.CONDITION_CREATED,
            EventType.CONDITION_UPDATED,
            EventType.CONDITION_RESOLVED,
        ]:
            condition = Condition.objects.filter(id=target_id).select_related("patient").first()
            if condition and condition.patient:
                return condition.patient, condition
            return None, None

        if self.event.type in [
            EventType.PATIENT_CREATED,
            EventType.PATIENT_UPDATED,
        ]:
            try:
                patient_id = self.patient_id_from_target()
                return Patient.objects.filter(id=patient_id).first(), None
            except (ValueError, AttributeError):
                return None, None

        patient_id = self.event.context.get("patient", {}).get("id")
        if patient_id:
            return Patient.objects.filter(id=patient_id).first(), None

        try:
            patient_id = self.patient_id_from_target()
            return Patient.objects.filter(id=patient_id).first(), None
        except (ValueError, AttributeError):
            pass

        return None, None

    def _is_condition_diabetes(self, condition: Condition) -> bool:
        """Check if the given condition is a diabetes diagnosis."""
        return Condition.objects.filter(id=condition.id).find(Diabetes).exists()

    def _should_remove_card(self, patient: Patient, condition: Condition | None) -> bool:
        """Check if protocol card should be removed due to condition changes."""
        if not condition:
            return False

        if not self._is_condition_diabetes(condition):
            return False

        if condition.entered_in_error:
            return not self._has_diabetes_diagnosis(patient)

        return False

    def _build_period_overlap_query(self, start_date: datetime.date, end_date: datetime.date) -> Q:
        """
        Build query for conditions whose prevalencePeriod overlaps given period.

        A condition overlaps if:
        - onset_date is NULL (treated as overlapping), OR
        - onset_date <= end_date AND (no resolution OR resolution_date >= start_date)
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
            Set of codes from all specified attributes
        """
        codes = set()
        for attr in attributes:
            attr_value = getattr(value_set, attr, None)
            if attr_value:
                codes |= attr_value
        return codes

    def _in_initial_population(self, patient: Patient, age: int) -> bool:
        """
        Initial Population: Patients 18-75 years of age with diabetes
        AND a qualifying encounter during the measurement period.
        """
        if not (AGE_RANGE_START <= age <= AGE_RANGE_END):
            return False

        if not self._has_diabetes_diagnosis_overlapping_period(patient):
            return False

        return self._has_qualifying_encounter(patient)

    def _has_diabetes_diagnosis(self, patient: Patient) -> bool:
        """Check if patient has any active diabetes diagnosis."""
        return (
            Condition.objects.for_patient(patient.id)
            .find(Diabetes)
            .active()
            .filter(entered_in_error_id__isnull=True)
            .exists()
        )

    def _has_diabetes_diagnosis_overlapping_period(self, patient: Patient) -> bool:
        """Check if patient has diabetes diagnosis overlapping measurement period."""
        measurement_start = self.timeframe.start.date()
        measurement_end = self.timeframe.end.date()

        overlap_query = self._build_period_overlap_query(measurement_start, measurement_end)

        return (
            Condition.objects.for_patient(patient.id)
            .find(Diabetes)
            .committed()
            .filter(entered_in_error_id__isnull=True)
            .filter(overlap_query)
            .exists()
        )

    def _has_qualifying_encounter(self, patient: Patient) -> bool:
        """
        Check if patient has a qualifying encounter during the measurement period.

        Per CMS122v14 CQL, qualifying encounters include:
        - Office Visit
        - Annual Wellness Visit
        - Preventive Care Services (Established/Initial, 18+)
        - Home Healthcare Services
        - Nutrition Services
        - Medical Nutrition Therapy (CPT: 97802, 97803, 97804; HCPCS: G0270, G0271)
        - Telephone Visits
        """
        return self._check_encounter_by_snomed(patient) or self._check_encounter_by_claim(patient)

    def _check_encounter_by_snomed(self, patient: Patient) -> bool:
        """Check for qualifying encounters using SNOMED codes."""
        encounter_snomed_codes = (
            ADDITIONAL_ENCOUNTER_SNOMED_CODES
            | self._get_value_set_codes(OfficeVisit, "SNOMEDCT")
            | self._get_value_set_codes(AnnualWellnessVisit, "SNOMEDCT")
            | self._get_value_set_codes(HomeHealthcareServices, "SNOMEDCT")
            | self._get_value_set_codes(TelephoneVisits, "SNOMEDCT")
            | self._get_value_set_codes(NutritionServices, "SNOMEDCT")
        )

        return Encounter.objects.filter(
            note__patient=patient,
            note__note_type_version__code__in=encounter_snomed_codes,
            state__in=["CON", "STA"],
            start_time__gte=self.timeframe.start.datetime,
            start_time__lte=self.timeframe.end.datetime,
        ).exists()

    def _check_encounter_by_claim(self, patient: Patient) -> bool:
        """Check for qualifying encounters using CPT/HCPCS claim codes."""
        eligible_codes = (
            self._get_value_set_codes(OfficeVisit, "CPT")
            | self._get_value_set_codes(AnnualWellnessVisit, "HCPCSLEVELII")
            | self._get_value_set_codes(PreventiveCareServicesEstablishedOfficeVisit18AndUp, "CPT")
            | self._get_value_set_codes(PreventiveCareServicesInitialOfficeVisit18AndUp, "CPT")
            | self._get_value_set_codes(HomeHealthcareServices, "CPT")
            | self._get_value_set_codes(NutritionServices, "CPT", "HCPCSLEVELII")
            | self._get_value_set_codes(TelephoneVisits, "CPT")
            | MNT_CPT_CODES
            | MNT_HCPCS_CODES
        )

        return ClaimLineItem.objects.filter(
            claim__note__patient=patient,
            status="active",
            from_date__gte=self.timeframe.start.date().isoformat(),
            from_date__lte=self.timeframe.end.date().isoformat(),
            proc_code__in=eligible_codes,
        ).exists()

    def _in_denominator(self, patient: Patient, age: int) -> bool:
        """
        Denominator: Equals Initial Population.

        Exclusions:
        1. Hospice care for any part of the measurement period
        2. Age 66+ living in nursing home
        3. Age 66+ with Advanced Illness AND Frailty
        4. Palliative care for any part of the measurement period
        """
        if self._has_hospice_care_in_period(patient):
            return False

        if self._is_age_66_plus_in_nursing_home(patient, age):
            return False

        if self._is_age_66_plus_with_frailty(
            patient, age
        ) and self._has_advanced_illness_or_dementia_meds(patient):
            return False

        return not self._has_palliative_care_in_period(patient)

    def _has_hospice_care_in_period(self, patient: Patient) -> bool:
        """
        Check for hospice care during measurement period.

        Checks:
        1. Hospice Diagnosis overlapping period
        2. Hospice Encounter overlapping period
        3. Inpatient encounter with discharge disposition to hospice
        4. Discharge to hospice via observations
        5. Hospice care assessment (LOINC 45755-6) with result "Yes"
        6. Hospice Care Ambulatory claims
        """
        start_date = self.timeframe.start.datetime
        end_date = self.timeframe.end.datetime

        has_hospice_diagnosis = (
            Condition.objects.for_patient(patient.id)
            .find(HospiceDiagnosis)
            .active()
            .filter(entered_in_error_id__isnull=True)
            .exists()
        )

        if has_hospice_diagnosis:
            return True

        hospice_encounter_codes = self._get_value_set_codes(HospiceEncounter, "SNOMEDCT", "ICD10CM")
        if hospice_encounter_codes:
            has_hospice_encounter = Encounter.objects.filter(
                note__patient=patient,
                note__note_type_version__code__in=hospice_encounter_codes,
                state__in=["CON", "STA"],
                start_time__gte=start_date,
                start_time__lte=end_date,
            ).exists()

            if has_hospice_encounter:
                return True

        inpatient_encounter_codes = self._get_value_set_codes(
            EncounterInpatient, "SNOMEDCT", "ICD10CM"
        )
        if inpatient_encounter_codes:
            inpatient_encounters = Encounter.objects.filter(
                note__patient=patient,
                note__note_type_version__code__in=inpatient_encounter_codes,
                state__in=["CON", "STA"],
                end_time__gte=start_date,
                end_time__lte=end_date,
            )

            if inpatient_encounters.exists():
                discharge_to_hospice_codes = {
                    DISCHARGE_TO_HOME_HOSPICE_SNOMED,
                    DISCHARGE_TO_FACILITY_HOSPICE_SNOMED,
                }

                inpatient_note_ids = list(inpatient_encounters.values_list("note__id", flat=True))

                has_inpatient_discharge_to_hospice = (
                    Observation.objects.for_patient(patient.id)
                    .filter(
                        note_id__in=inpatient_note_ids,
                        value_codings__code__in=discharge_to_hospice_codes,
                        value_codings__system__in=SNOMED_SYSTEM_IDENTIFIERS,
                    )
                    .exists()
                )

                if has_inpatient_discharge_to_hospice:
                    return True

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
                value_codings__system__in=SNOMED_SYSTEM_IDENTIFIERS,
            )
            .exists()
        )

        if has_discharge_to_hospice:
            return True

        has_hospice_assessment = (
            Observation.objects.for_patient(patient.id)
            .filter(
                effective_datetime__gte=start_date,
                effective_datetime__lte=end_date,
                codings__code=HOSPICE_MDS_LOINC,
                codings__system__in=LOINC_SYSTEM_IDENTIFIERS,
                value_codings__code=YES_QUALIFIER_SNOMED,
                value_codings__system__in=SNOMED_SYSTEM_IDENTIFIERS,
            )
            .exists()
        )

        if has_hospice_assessment:
            return True

        hospice_intervention_codes = self._get_value_set_codes(
            HospiceCareAmbulatory, "CPT", "HCPCSLEVELII", "SNOMEDCT"
        )

        if hospice_intervention_codes:
            has_hospice_claim = ClaimLineItem.objects.filter(
                claim__note__patient=patient,
                status="active",
                from_date__gte=self.timeframe.start.date().isoformat(),
                from_date__lte=self.timeframe.end.date().isoformat(),
                proc_code__in=hospice_intervention_codes,
            ).exists()

            if has_hospice_claim:
                return True

        return False

    def _is_age_66_plus_in_nursing_home(self, patient: Patient, age: int) -> bool:
        """
        Check if patient is 66+ and living in a nursing home.

        Per CMS122v14 CQL: Age >= 66 AND most recent Housing Status assessment
        result is "Lives in nursing home" OR has nursing facility encounter.

        Per spec: "any time on or before the end of the measurement period"
        """
        if age < 66:
            return False

        has_nursing_home_assessment = (
            Observation.objects.for_patient(patient.id)
            .filter(
                effective_datetime__lte=self.timeframe.end.datetime,
                codings__code=HOUSING_STATUS_LOINC,
                codings__system__in=LOINC_SYSTEM_IDENTIFIERS,
                value_codings__code=LIVES_IN_NURSING_HOME_SNOMED,
                value_codings__system__in=SNOMED_SYSTEM_IDENTIFIERS,
            )
            .order_by("-effective_datetime")
            .first()
        )

        if has_nursing_home_assessment:
            return True

        nursing_facility_cpt = self._get_value_set_codes(NursingFacilityVisit, "CPT")
        nursing_facility_snomed = self._get_value_set_codes(NursingFacilityVisit, "SNOMEDCT")
        long_term_care_snomed = self._get_value_set_codes(
            CareServicesInLongTermResidentialFacility, "SNOMEDCT"
        )

        if nursing_facility_cpt:
            has_nursing_claim = ClaimLineItem.objects.filter(
                claim__note__patient=patient,
                status="active",
                from_date__lte=self.timeframe.end.date().isoformat(),
                proc_code__in=nursing_facility_cpt,
            ).exists()

            if has_nursing_claim:
                return True

        all_snomed_codes = nursing_facility_snomed | long_term_care_snomed
        if all_snomed_codes:
            has_nursing_encounter = Encounter.objects.filter(
                note__patient=patient,
                note__note_type_version__code__in=all_snomed_codes,
                state__in=["CON", "STA"],
                start_time__lte=self.timeframe.end.datetime,
            ).exists()

            if has_nursing_encounter:
                return True

        return False

    def _is_age_66_plus_with_frailty(self, patient: Patient, age: int) -> bool:
        """
        Check if patient is 66+ with frailty indicators.

        Per CQL "Has Criteria Indicating Frailty", checks for:
        - Device orders for frailty devices
        - Assessment observations with frailty device results
        - Frailty diagnoses overlapping measurement period
        - Frailty encounters overlapping measurement period
        - Frailty symptoms overlapping measurement period
        """
        if age < 66:
            return False

        if self._has_frailty_device_orders(patient):
            return True

        if self._has_frailty_device_observations(patient):
            return True

        if self._has_frailty_diagnoses(patient):
            return True

        if self._has_frailty_encounters(patient):
            return True

        return self._has_frailty_symptoms(patient)

    def _has_frailty_device_orders(self, patient: Patient) -> bool:
        """
        Check for device orders with frailty device codes during measurement period.

        Per spec: Device, Order: "Frailty Device" - authorDatetime during measurement period.

        Checks:
        1. ClaimLineItem for DME codes (primary check - has codes and dates)
        2. Device model for ordered devices during measurement period (fallback)
           Note: Device model doesn't have coding fields, so we can't filter by
           frailty device codes. This relies on ClaimLineItem and observations
           for code-specific filtering.
        """
        frailty_device_hcpcs = self._get_value_set_codes(FrailtyDevice, "HCPCSLEVELII")

        if frailty_device_hcpcs:
            has_dme_claim = ClaimLineItem.objects.filter(
                claim__note__patient=patient,
                status="active",
                from_date__gte=self.timeframe.start.date().isoformat(),
                from_date__lte=self.timeframe.end.date().isoformat(),
                proc_code__in=frailty_device_hcpcs,
            ).exists()

            if has_dme_claim:
                return True

        notes_in_period = Note.objects.filter(
            patient=patient,
            datetime_of_service__gte=self.timeframe.start.datetime,
            datetime_of_service__lte=self.timeframe.end.datetime,
        ).values_list("id", flat=True)

        if notes_in_period:
            has_device_order = Device.objects.filter(
                patient=patient,
                status="ordered",
                note_id__in=notes_in_period,
            ).exists()

            if has_device_order:
                return True

        return False

    def _has_frailty_device_observations(self, patient: Patient) -> bool:
        """Check for observations with frailty device codes in value_codings."""
        frailty_device_snomed = self._get_value_set_codes(FrailtyDevice, "SNOMEDCT")

        if not frailty_device_snomed:
            return False

        return (
            Observation.objects.for_patient(patient.id)
            .filter(
                Q(effective_datetime__isnull=True)
                | Q(
                    effective_datetime__gte=self.timeframe.start.datetime,
                    effective_datetime__lte=self.timeframe.end.datetime,
                ),
                value_codings__code__in=frailty_device_snomed,
                value_codings__system__in=SNOMED_SYSTEM_IDENTIFIERS,
            )
            .exists()
        )

    def _has_frailty_diagnoses(self, patient: Patient) -> bool:
        """Check for frailty diagnoses overlapping measurement period."""
        measurement_start = self.timeframe.start.date()
        measurement_end = self.timeframe.end.date()

        overlap_query = self._build_period_overlap_query(measurement_start, measurement_end)

        return (
            Condition.objects.for_patient(patient.id)
            .find(FrailtyDiagnosis)
            .committed()
            .filter(entered_in_error_id__isnull=True)
            .filter(overlap_query)
            .exists()
        )

    def _has_frailty_encounters(self, patient: Patient) -> bool:
        """Check for frailty encounters during measurement period."""
        start_date = self.timeframe.start.datetime
        end_date = self.timeframe.end.datetime

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
                return True

        frailty_codes = self._get_value_set_codes(FrailtyEncounter, "CPT", "HCPCSLEVELII")
        if frailty_codes:
            has_claim = ClaimLineItem.objects.filter(
                claim__note__patient=patient,
                status="active",
                from_date__gte=self.timeframe.start.date().isoformat(),
                from_date__lte=self.timeframe.end.date().isoformat(),
                proc_code__in=frailty_codes,
            ).exists()

            if has_claim:
                return True

        return False

    def _has_frailty_symptoms(self, patient: Patient) -> bool:
        """Check for frailty symptoms overlapping measurement period."""
        measurement_start = self.timeframe.start.date()
        measurement_end = self.timeframe.end.date()

        overlap_query = self._build_period_overlap_query(measurement_start, measurement_end)

        return (
            Condition.objects.for_patient(patient.id)
            .find(FrailtySymptom)
            .committed()
            .filter(entered_in_error_id__isnull=True)
            .filter(overlap_query)
            .exists()
        )

    def _has_advanced_illness_or_dementia_meds(self, patient: Patient) -> bool:
        """
        Check for advanced illness or dementia medications.

        Lookback: measurement period + 1 year prior

        Per CMS122v14 CQL:
        - Advanced illness diagnosis that starts during the measurement period or the year prior
        - OR taking dementia medications during the measurement period or the year prior.
        """
        start_date = self.timeframe.start.shift(years=-1).date()
        end_date = self.timeframe.end.date()

        has_advanced_illness = (
            Condition.objects.for_patient(patient.id)
            .find(AdvancedIllness)
            .filter(
                Q(onset_date__isnull=True) | Q(onset_date__lte=end_date, onset_date__gte=start_date)
            )
            .filter(entered_in_error_id__isnull=True)
            .exists()
        )

        if has_advanced_illness:
            return True

        start_datetime = arrow.get(start_date).datetime
        end_datetime = (
            arrow.get(end_date).replace(hour=23, minute=59, second=59, microsecond=999999).datetime
        )

        return (
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

    def _has_palliative_care_in_period(self, patient: Patient) -> bool:
        """
        Check for palliative care during measurement period.

        Checks:
        1. FACIT-Pal assessment (LOINC 71007-9)
        2. Palliative Care Diagnosis
        3. Palliative Care Encounter
        4. Palliative Care Intervention claims
        """
        start_date = self.timeframe.start.datetime
        end_date = self.timeframe.end.datetime

        has_assessment = (
            Observation.objects.for_patient(patient.id)
            .filter(
                effective_datetime__gte=start_date,
                effective_datetime__lte=end_date,
                codings__code=PALLIATIVE_CARE_ASSESSMENT_LOINC,
                codings__system__in=LOINC_SYSTEM_IDENTIFIERS,
            )
            .exists()
        )

        if has_assessment:
            return True

        has_diagnosis = (
            Condition.objects.for_patient(patient.id)
            .find(PalliativeCareDiagnosis)
            .active()
            .filter(entered_in_error_id__isnull=True)
            .exists()
        )

        if has_diagnosis:
            return True

        palliative_codes = self._get_value_set_codes(PalliativeCareEncounter, "SNOMEDCT", "ICD10CM")
        if palliative_codes:
            has_encounter = Encounter.objects.filter(
                note__patient=patient,
                note__note_type_version__code__in=palliative_codes,
                state__in=["CON", "STA"],
                start_time__gte=start_date,
                start_time__lte=end_date,
            ).exists()

            if has_encounter:
                return True

        palliative_claim_codes = self._get_value_set_codes(
            PalliativeCareEncounter, "HCPCSLEVELII"
        ) | self._get_value_set_codes(PalliativeCareIntervention, "SNOMEDCT")

        if palliative_claim_codes:
            has_claim = ClaimLineItem.objects.filter(
                claim__note__patient=patient,
                status="active",
                from_date__gte=self.timeframe.start.date().isoformat(),
                from_date__lte=self.timeframe.end.date().isoformat(),
                proc_code__in=palliative_claim_codes,
            ).exists()

            if has_claim:
                return True

        return False

    def _in_numerator(self, patient: Patient) -> bool:
        """
        Numerator: Patients whose most recent glycemic status assessment
        (HbA1c or GMI) > 9.0% or is missing/no result.
        """
        glycemic_assessment = self._find_glycemic_status_assessment(patient)

        if not glycemic_assessment:
            return True

        glycemic_value = self._get_glycemic_value(glycemic_assessment)
        if glycemic_value is None:
            return True

        return glycemic_value > GLYCEMIC_THRESHOLD

    def _find_glycemic_status_assessment(self, patient: Patient) -> LabReport | None:
        """
        Find the lowest glycemic status assessment on the most recent date.
        If multiple tests on same day, return the one with lowest value.
        """
        glycemic_codes = set()

        if hasattr(Hba1cLaboratoryTest, "LOINC"):
            glycemic_codes.update(Hba1cLaboratoryTest.LOINC)

        glycemic_codes.add(GMI_LOINC_CODE)

        if not glycemic_codes:
            return None

        lab_reports = (
            LabReport.objects.filter(
                patient__id=patient.id,
                values__codings__code__in=glycemic_codes,
                original_date__gte=self.timeframe.start.datetime,
                original_date__lte=self.timeframe.end.datetime,
                junked=False,
            )
            .distinct()
            .order_by("-original_date")
        )

        if not lab_reports.exists():
            return None

        most_recent_report = lab_reports.first()
        most_recent_date = most_recent_report.original_date.date()

        same_day_reports = [r for r in lab_reports if r.original_date.date() == most_recent_date]

        if len(same_day_reports) == 1:
            return same_day_reports[0]

        lowest_report = None
        lowest_value = float("inf")

        for report in same_day_reports:
            value = self._get_glycemic_value(report)
            if value is not None and value < lowest_value:
                lowest_value = value
                lowest_report = report

        if lowest_report:
            return lowest_report

        return same_day_reports[0]

    def _get_glycemic_value(self, lab_report: LabReport) -> float | None:
        """Extract glycemic status value (HbA1c or GMI) from lab report."""
        lab_value = lab_report.values.first()
        if not lab_value:
            return None

        value = lab_value.value
        if value is None or value == "":
            return None

        try:
            if isinstance(value, str):
                return self.relative_float(value)
            return float(value)
        except (ValueError, TypeError):
            return None

    def _get_test_type(self, lab_report: LabReport) -> str:
        """Determine if lab report is HbA1c or GMI."""
        lab_value = lab_report.values.first()
        if lab_value:
            for coding in lab_value.codings.all():
                if coding.code == GMI_LOINC_CODE:
                    return TEST_TYPE_GMI
        return TEST_TYPE_HBA1C

    def _get_glycemic_date(self, lab_report: LabReport) -> str:
        """Get formatted date string for glycemic lab report."""
        if lab_report.original_date:
            return arrow.get(lab_report.original_date).format("MMMM D, YYYY")
        return ""

    def _create_not_applicable_card(self, patient: Patient) -> Effect:
        """Create a NOT APPLICABLE protocol card."""
        card = ProtocolCard(
            patient_id=patient.id,
            key=PROTOCOL_KEY,
            title=self.Meta.title,
            narrative="",
            status=ProtocolCard.Status.NOT_APPLICABLE,
        )

        return card.apply()

    def _create_satisfied_card(self, patient: Patient) -> Effect:
        """Create a SATISFIED protocol card for poor glycemic control."""
        glycemic_assessment = self._find_glycemic_status_assessment(patient)
        first_name = patient.first_name

        if glycemic_assessment:
            glycemic_value = self._get_glycemic_value(glycemic_assessment)
            glycemic_date = self._get_glycemic_date(glycemic_assessment)
            test_type = self._get_test_type(glycemic_assessment)

            if glycemic_value is not None:
                narrative = f"{first_name}'s last {test_type} done {glycemic_date} was {glycemic_value:.1f}%."
            else:
                narrative = f"{first_name}'s last {test_type} was done {glycemic_date}."
        else:
            narrative = f"{first_name} has no glycemic status assessment in the measurement period."

        card = ProtocolCard(
            patient_id=patient.id,
            key=PROTOCOL_KEY,
            title=self.Meta.title,
            narrative=narrative,
            status=ProtocolCard.Status.SATISFIED,
            due_in=-1,
            can_be_snoozed=True,
        )

        return card.apply()

    def _get_diabetes_diagnosis_codes(self, patient: Patient) -> list[str]:
        """Extract ICD-10 codes from patient's diabetes diagnoses."""
        diagnosis_codes = []

        diabetes_conditions = (
            Condition.objects.for_patient(patient.id)
            .find(Diabetes)
            .active()
            .filter(entered_in_error_id__isnull=True)
        )

        for condition in diabetes_conditions:
            for coding in condition.codings.all():
                diagnosis_codes.append(coding.code)

        return diagnosis_codes

    def _create_due_card(self, patient: Patient) -> Effect:
        """Create a DUE protocol card with recommendations."""
        glycemic_assessment = self._find_glycemic_status_assessment(patient)
        first_name = patient.first_name

        if glycemic_assessment:
            glycemic_value = self._get_glycemic_value(glycemic_assessment)
            glycemic_date = self._get_glycemic_date(glycemic_assessment)
            test_type = self._get_test_type(glycemic_assessment)

            if glycemic_value is not None:
                narrative = f"{first_name}'s last {test_type} done {glycemic_date} was {glycemic_value:.1f}%."
            else:
                narrative = f"{first_name}'s last {test_type} was done {glycemic_date}."
        else:
            narrative = (
                f"{first_name}'s last glycemic test was over "
                f"{self.now.shift(years=-1, months=-1).humanize(other=self.now, granularity='month', only_distance=True)}."
            ).replace(" ago", "")

        card = ProtocolCard(
            patient_id=patient.id,
            key=PROTOCOL_KEY,
            title=self.Meta.title,
            narrative=narrative,
            status=ProtocolCard.Status.DUE,
            due_in=-1,
            can_be_snoozed=True,
        )

        if not glycemic_assessment or self._get_glycemic_value(glycemic_assessment) is None:
            hba1c_codes = (
                list(Hba1cLaboratoryTest.LOINC) if hasattr(Hba1cLaboratoryTest, "LOINC") else []
            )
            if hba1c_codes:
                diabetes_codes = self._get_diabetes_diagnosis_codes(patient)
                lab_order_command = LabOrderCommand(
                    tests_order_codes=hba1c_codes,
                    diagnosis_codes=diabetes_codes,
                )
                card.recommendations.append(
                    lab_order_command.recommend(title=f"Order {TEST_TYPE_HBA1C}", button="Order")
                )
        else:
            dietary_codes = (
                list(DietaryRecommendations.SNOMEDCT)
                if hasattr(DietaryRecommendations, "SNOMEDCT")
                else []
            )
            if dietary_codes:
                instruct_command = InstructCommand(
                    coding={
                        "system": CodeSystems.SNOMED,
                        "code": dietary_codes[0],
                    },
                    comment=(
                        "Discuss lifestyle modification and medication adherence. "
                        "Consider diabetes education and medication intensification as appropriate."
                    ),
                )
                card.recommendations.append(
                    instruct_command.recommend(
                        title=(
                            "Discuss lifestyle modification and medication adherence. "
                            "Consider diabetes education and medication intensification as appropriate."
                        ),
                        button="Instruct",
                    )
                )

        return card.apply()
