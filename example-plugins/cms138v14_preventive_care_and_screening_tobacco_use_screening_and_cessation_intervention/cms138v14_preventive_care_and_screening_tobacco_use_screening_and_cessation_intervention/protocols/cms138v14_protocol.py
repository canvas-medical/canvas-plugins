"""CMS138v14 Preventive Care and Screening: Tobacco Use Screening and Cessation Intervention."""

import datetime
from typing import Any

import arrow
from django.db.models import Q

from canvas_sdk.commands import InstructCommand, PrescribeCommand, QuestionnaireCommand
from canvas_sdk.commands.constants import CodeSystems
from canvas_sdk.effects import Effect
from canvas_sdk.effects.protocol_card import ProtocolCard
from canvas_sdk.events import EventType
from canvas_sdk.protocols import ClinicalQualityMeasure
from canvas_sdk.v1.data import (
    ClaimLineItem,
    Condition,
    Encounter,
    Instruction,
    Interview,
    InterviewQuestionResponse,
    Medication,
    Observation,
    Patient,
)
from canvas_sdk.value_set.v2026.assessment import TobaccoUseScreening
from canvas_sdk.value_set.v2026.condition import HospiceDiagnosis
from canvas_sdk.value_set.v2026.encounter import (
    AnnualWellnessVisit,
    EncounterInpatient,
    HomeHealthcareServices,
    HospiceEncounter,
    NutritionServices,
    OccupationalTherapyEvaluation,
    OfficeVisit,
    OphthalmologicalServices,
    PhysicalTherapyEvaluation,
    PreventiveCareEstablishedOfficeVisit0To17,
    PreventiveCareServicesEstablishedOfficeVisit18AndUp,
    PreventiveCareServicesGroupCounseling,
    PreventiveCareServicesIndividualCounseling,
    PreventiveCareServicesInitialOfficeVisit0To17,
    PreventiveCareServicesInitialOfficeVisit18AndUp,
    Psychoanalysis,
    PsychVisitDiagnosticEvaluation,
    PsychVisitPsychotherapy,
    SpeechAndHearingEvaluation,
    TelephoneVisits,
    VirtualEncounter,
)
from canvas_sdk.value_set.v2026.intervention import (
    HospiceCareAmbulatory,
    TobaccoUseCessationCounseling,
)
from canvas_sdk.value_set.v2026.medication import TobaccoUseCessationPharmacotherapy
from canvas_sdk.value_set.v2026.no_qdm_category_assigned import TobaccoNonUser, TobaccoUser
from logger import log

AGE_MINIMUM = 12
CESSATION_INTERVENTION_LOOKBACK_MONTHS = 6

DISCHARGE_TO_HOME_HOSPICE_SNOMED = "428361000124107"
DISCHARGE_TO_FACILITY_HOSPICE_SNOMED = "428371000124100"
HOSPICE_CARE_MDS_LOINC = "45755-6"
YES_QUALIFIER_SNOMED = "373066001"
Z71_6_TOBACCO_COUNSELING_CODES = {"Z71.6", "Z716", "Z71.60", "Z7160"}
HEALTH_BEHAVIOR_ASSESSMENT_CPT = "96156"
HEALTH_BEHAVIOR_INTERVENTION_CPT = "96158"
UNLISTED_PREVENTIVE_SERVICE_CPT = "99429"
POSTOPERATIVE_FOLLOWUP_CPT = "99024"


class ScreeningData:
    """Holds tobacco screening and intervention data."""

    most_recent_user: "arrow.Arrow | None"
    most_recent_non_user: "arrow.Arrow | None"
    counseling_date: "arrow.Arrow | None"
    pharmacotherapy_date: "arrow.Arrow | None"

    def __init__(self) -> None:
        self.most_recent_user = None
        self.most_recent_non_user = None
        self.counseling_date = None
        self.pharmacotherapy_date = None

    def has_screening(self) -> bool:
        """Return True if any screening exists."""
        return self.most_recent_user is not None or self.most_recent_non_user is not None

    def is_tobacco_user(self) -> bool:
        """Return True if most recent screening indicates tobacco user."""
        if self.most_recent_user is None and self.most_recent_non_user is None:
            return False
        if self.most_recent_user is None:
            return False
        if self.most_recent_non_user is None:
            return True
        return self.most_recent_user > self.most_recent_non_user

    def is_tobacco_non_user(self) -> bool:
        """Return True if most recent screening indicates non-user."""
        return self.has_screening() and not self.is_tobacco_user()

    def has_intervention(self) -> bool:
        """Return True if any cessation intervention exists."""
        return self.counseling_date is not None or self.pharmacotherapy_date is not None


class PopulationResult:
    """
    Track population membership for CMS measure rates.

    CMS138v14 has three performance rates:
    - Population 1: Screening rate (screened / eligible)
    - Population 2: Intervention rate (intervention / tobacco users)
    - Population 3: Overall rate (non-users + users with intervention / eligible)

    Attributes:
        in_initial_population: True if patient meets initial population criteria.
        in_denominator: True if patient is in the rate's denominator.
        in_numerator: True if patient meets the rate's numerator criteria.
    """

    in_initial_population: bool = False
    in_denominator: bool = False
    in_numerator: bool = False


class CMS138v14TobaccoScreening(ClinicalQualityMeasure):
    """CMS138v14 Tobacco Use Screening and Cessation Intervention measure."""

    class Meta:
        title = "Preventive Care and Screening: Tobacco Use: Screening and Cessation Intervention"
        description = (
            "Percentage of patients aged 12 years and older who were screened for tobacco use "
            "and who received tobacco cessation intervention if identified as a tobacco user."
        )
        version = "v14.0.0"
        information = "https://ecqi.healthit.gov/ecqm/ec/2026/cms0138v14"
        identifiers = ["CMS138v14"]
        types = ["CQM"]
        authors = ["National Committee for Quality Assurance"]
        references = [
            "US Department of Health and Human Services. (2008). 6, Evidence and Recommendations. Treating Tobacco Use and Dependence: 2008 Update. Retrieved from https://www.ncbi.nlm.nih.gov/books/NBK63943/",
            "US Preventive Services Task Force. (2021). Interventions for Tobacco Smoking Cessation in Adults, Including Pregnant Persons. US Preventive Services Task Force Recommendation Statement. JAMA, 325(3), 265-279. doi:10.1001/jama.2020.25019",
            "US Preventive Services Task Force. (2020). Primary Care Interventions for Prevention and Cessation of Tobacco Use in Children and Adolescents. US Preventive Services Task Force Recommendation Statement. JAMA, 2020;323(16):1590-1598. doi:10.1001/jama.2020.4679",
        ]

    RESPONDS_TO = [
        EventType.Name(EventType.CONDITION_CREATED),
        EventType.Name(EventType.CONDITION_UPDATED),
        EventType.Name(EventType.CONDITION_RESOLVED),
        EventType.Name(EventType.MEDICATION_LIST_ITEM_CREATED),
        EventType.Name(EventType.MEDICATION_LIST_ITEM_UPDATED),
        EventType.Name(EventType.PATIENT_CREATED),
        EventType.Name(EventType.PATIENT_UPDATED),
        EventType.Name(EventType.OBSERVATION_CREATED),
        EventType.Name(EventType.OBSERVATION_UPDATED),
        EventType.Name(EventType.CLAIM_CREATED),
        EventType.Name(EventType.CLAIM_UPDATED),
        EventType.Name(EventType.ENCOUNTER_CREATED),
        EventType.Name(EventType.ENCOUNTER_UPDATED),
        EventType.Name(EventType.INSTRUCTION_CREATED),
        EventType.Name(EventType.INSTRUCTION_UPDATED),
        EventType.Name(EventType.INTERVIEW_CREATED),
        EventType.Name(EventType.INTERVIEW_UPDATED),
        EventType.Name(EventType.PROTOCOL_OVERRIDE_CREATED),
        EventType.Name(EventType.PROTOCOL_OVERRIDE_UPDATED),
        EventType.Name(EventType.PROTOCOL_OVERRIDE_DELETED),
    ]
    POPULATION_1 = "population_1"
    POPULATION_2 = "population_2"
    POPULATION_3 = "population_3"

    # Value sets for qualifying visits (need >= 2)
    QUALIFYING_VISIT_VALUE_SETS = (
        OfficeVisit,
        HomeHealthcareServices,
        OccupationalTherapyEvaluation,
        PhysicalTherapyEvaluation,
        OphthalmologicalServices,
        PsychVisitDiagnosticEvaluation,
        PsychVisitPsychotherapy,
        Psychoanalysis,
        SpeechAndHearingEvaluation,
        TelephoneVisits,
        VirtualEncounter,
    )

    # Value sets for preventive visits (need >= 1)
    PREVENTIVE_VISIT_VALUE_SETS = (
        AnnualWellnessVisit,
        PreventiveCareServicesEstablishedOfficeVisit18AndUp,
        PreventiveCareServicesInitialOfficeVisit18AndUp,
        PreventiveCareEstablishedOfficeVisit0To17,
        PreventiveCareServicesInitialOfficeVisit0To17,
        PreventiveCareServicesGroupCounseling,
        PreventiveCareServicesIndividualCounseling,
        NutritionServices,
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._populations = {
            self.POPULATION_1: PopulationResult(),
            self.POPULATION_2: PopulationResult(),
            self.POPULATION_3: PopulationResult(),
        }

    def _get_patient(self) -> Patient | None:
        """Get patient from event context or by querying the database."""
        try:
            target_id = self.event.target.id

            # Condition events - get patient from condition
            if self.event.type in [
                EventType.CONDITION_CREATED,
                EventType.CONDITION_UPDATED,
                EventType.CONDITION_RESOLVED,
            ]:
                condition = Condition.objects.filter(id=target_id).select_related("patient").first()
                if condition and condition.patient:
                    return condition.patient
                log.warning(f"CMS138v14: Could not find patient for condition {target_id}")
                return None

            # Interview events - get patient from interview
            if self.event.type in [EventType.INTERVIEW_CREATED, EventType.INTERVIEW_UPDATED]:
                interview = Interview.objects.filter(id=target_id).select_related("patient").first()
                if interview and interview.patient:
                    return interview.patient
                log.warning(f"CMS138v14: Could not find patient for interview {target_id}")
                return None

            # Try to get patient_id from context
            patient_id = self.event.context.get("patient", {}).get("id")
            if patient_id:
                return Patient.objects.filter(id=patient_id).first()

            # Fallback: try patient_id_from_target for supported event types
            try:
                patient_id = self.patient_id_from_target()
                if patient_id:
                    return Patient.objects.filter(id=patient_id).first()
            except ValueError:
                log.debug(
                    f"CMS138v14: Event type {self.event.type} not supported by patient_id_from_target()"
                )

            return None

        except Exception as e:
            log.error(f"CMS138v14: Error getting patient: {str(e)}")
            return None

    def compute(self) -> list[Effect]:
        """Main compute method for CMS138v14 Tobacco Screening measure."""
        log.info(f"CMS138v14: compute() called for event type {self.event.type}")

        try:
            patient = self._get_patient()
            if not patient:
                log.warning(f"CMS138v14: Could not get patient from event {self.event.type}")
                return []

            if not self._in_initial_population(patient):
                log.debug(f"CMS138v14: Patient {patient.id} not in initial population")
                return [self._create_not_applicable_card(patient)]

            if self._has_hospice_care_in_period(patient):
                log.debug(f"CMS138v14: Patient {patient.id} excluded (hospice care)")
                return [self._create_not_applicable_card(patient)]

            screening_data = self._get_screening_data(patient)
            log.debug(
                f"CMS138v14: Screening data - user: {screening_data.most_recent_user}, "
                f"non_user: {screening_data.most_recent_non_user}, "
                f"counseling: {screening_data.counseling_date}, "
                f"pharmacotherapy: {screening_data.pharmacotherapy_date}"
            )

            self._compute_populations(screening_data)

            if self._populations[self.POPULATION_3].in_numerator:
                log.debug(f"CMS138v14: Patient {patient.id} in numerator - SATISFIED")
                return [self._create_satisfied_card(patient, screening_data)]
            else:
                log.debug(f"CMS138v14: Patient {patient.id} not in numerator - DUE")
                return [self._create_due_card(patient, screening_data)]

        except Exception:
            log.error("CMS138v14: Error in compute")
            return []

    def _in_initial_population(self, patient: Patient) -> bool:
        """Check if patient is in initial population for CMS138v14."""
        if not patient.birth_date:
            return False

        age = patient.age_at(self.timeframe.start)
        if age < AGE_MINIMUM:
            return False

        if self._is_chart_context():
            log.debug(
                f"CMS138v14: Bypassing encounter requirement for patient {patient.id} "
                "(chart/guidance context)"
            )
            return True

        qualifying_count = self._count_qualifying_visits(patient)
        preventive_count = self._count_preventive_visits(patient)

        log.debug(
            f"CMS138v14: Patient {patient.id} has {qualifying_count} qualifying visits, "
            f"{preventive_count} preventive visits"
        )

        return qualifying_count >= 2 or preventive_count >= 1

    def _is_chart_context(self) -> bool:
        """Check if protocol is being evaluated in chart/guidance context."""
        if self.event.type in [EventType.PATIENT_CREATED, EventType.PATIENT_UPDATED]:
            return True
        return bool(self.event.context.get("patient"))

    def _count_qualifying_visits(self, patient: Patient) -> int:
        """Count qualifying visits (need >= 2) during measurement period."""
        try:
            start_date = self.timeframe.start.datetime
            end_date = self.timeframe.end.datetime
            qualifying_note_ids: set[str] = set()

            # Get SNOMED codes from qualifying visit value sets
            qualifying_snomed_codes = self._get_value_set_codes(
                self.QUALIFYING_VISIT_VALUE_SETS, "SNOMEDCT"
            )

            if qualifying_snomed_codes:
                encounters = Encounter.objects.filter(
                    note__patient=patient,
                    note__note_type_version__code__in=qualifying_snomed_codes,
                    state__in=["CON", "STA"],
                    start_time__gte=start_date,
                    start_time__lte=end_date,
                ).values_list("note_id", flat=True)
                qualifying_note_ids.update(str(nid) for nid in encounters if nid)

            # Get CPT codes from qualifying visit value sets + direct CPT codes
            qualifying_cpt_codes = self._get_value_set_codes(
                self.QUALIFYING_VISIT_VALUE_SETS, "CPT"
            ) | {HEALTH_BEHAVIOR_ASSESSMENT_CPT, HEALTH_BEHAVIOR_INTERVENTION_CPT}

            if qualifying_cpt_codes:
                claims = ClaimLineItem.objects.filter(
                    claim__note__patient=patient,
                    status="active",
                    from_date__gte=self.timeframe.start.date().isoformat(),
                    from_date__lte=self.timeframe.end.date().isoformat(),
                    proc_code__in=qualifying_cpt_codes,
                ).values_list("claim__note_id", flat=True)
                qualifying_note_ids.update(str(nid) for nid in claims if nid)

            return len(qualifying_note_ids)

        except Exception:
            log.error("CMS138v14: Error counting qualifying visits")
            return 0

    def _count_preventive_visits(self, patient: Patient) -> int:
        """Count preventive visits (need >= 1) during measurement period."""
        try:
            start_date = self.timeframe.start.datetime
            end_date = self.timeframe.end.datetime
            preventive_note_ids: set[str] = set()

            # Get SNOMED codes from preventive visit value sets
            preventive_snomed_codes = self._get_value_set_codes(
                self.PREVENTIVE_VISIT_VALUE_SETS, "SNOMEDCT"
            )

            if preventive_snomed_codes:
                encounters = Encounter.objects.filter(
                    note__patient=patient,
                    note__note_type_version__code__in=preventive_snomed_codes,
                    state__in=["CON", "STA"],
                    start_time__gte=start_date,
                    start_time__lte=end_date,
                ).values_list("note_id", flat=True)
                preventive_note_ids.update(str(nid) for nid in encounters if nid)

            # Get CPT/HCPCS codes from preventive visit value sets + direct codes
            preventive_cpt_codes = (
                self._get_value_set_codes(self.PREVENTIVE_VISIT_VALUE_SETS, "CPT")
                | self._get_value_set_codes(self.PREVENTIVE_VISIT_VALUE_SETS, "HCPCSLEVELII")
                | {UNLISTED_PREVENTIVE_SERVICE_CPT, POSTOPERATIVE_FOLLOWUP_CPT}
            )

            if preventive_cpt_codes:
                claims = ClaimLineItem.objects.filter(
                    claim__note__patient=patient,
                    status="active",
                    from_date__gte=self.timeframe.start.date().isoformat(),
                    from_date__lte=self.timeframe.end.date().isoformat(),
                    proc_code__in=preventive_cpt_codes,
                ).values_list("claim__note_id", flat=True)
                preventive_note_ids.update(str(nid) for nid in claims if nid)

            return len(preventive_note_ids)

        except Exception:
            log.error("CMS138v14: Error counting preventive visits")
            return 0

    def _build_period_overlap_query(self, start_date: datetime.date, end_date: datetime.date) -> Q:
        """Build query for conditions whose prevalencePeriod overlaps given period."""
        return Q(onset_date__isnull=True) | (
            Q(onset_date__lte=end_date)
            & (Q(resolution_date__isnull=True) | Q(resolution_date__gte=start_date))
        )

    def _has_hospice_care_in_period(self, patient: Patient) -> bool:
        """Check if patient is in hospice care during measurement period (exclusion)."""
        try:
            start_date = self.timeframe.start.datetime
            end_date = self.timeframe.end.datetime
            measurement_start = self.timeframe.start.date()
            measurement_end = self.timeframe.end.date()

            overlap_query = self._build_period_overlap_query(measurement_start, measurement_end)

            has_hospice_diagnosis = (
                Condition.objects.for_patient(patient.id)
                .find(HospiceDiagnosis)
                .committed()
                .filter(entered_in_error_id__isnull=True)
                .filter(overlap_query)
                .exists()
            )

            if has_hospice_diagnosis:
                log.debug(f"CMS138v14: Found hospice diagnosis for patient {patient.id}")
                return True

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
                    log.debug(f"CMS138v14: Found hospice encounter for patient {patient.id}")
                    return True

            discharge_to_hospice_codes = {
                DISCHARGE_TO_HOME_HOSPICE_SNOMED,
                DISCHARGE_TO_FACILITY_HOSPICE_SNOMED,
            }

            inpatient_codes = self._get_value_set_codes(
                EncounterInpatient, "SNOMEDCT", "ICD10CM", "CPT"
            )

            if inpatient_codes:
                inpatient_encounters = Encounter.objects.filter(
                    note__patient=patient,
                    note__note_type_version__code__in=inpatient_codes,
                    state__in=["CON", "STA"],
                    end_time__gte=start_date,
                    end_time__lte=end_date,
                ).values_list("note_id", flat=True)

                if inpatient_encounters:
                    has_inpatient_discharge = (
                        Observation.objects.for_patient(patient.id)
                        .committed()
                        .filter(
                            note_id__in=inpatient_encounters,
                            value_codings__code__in=discharge_to_hospice_codes,
                        )
                        .exists()
                    )

                    if has_inpatient_discharge:
                        log.debug(
                            f"CMS138v14: Found inpatient discharge to hospice for patient "
                            f"{patient.id}"
                        )
                        return True

            has_discharge_to_hospice = (
                Observation.objects.for_patient(patient.id)
                .committed()
                .filter(
                    effective_datetime__gte=start_date,
                    effective_datetime__lte=end_date,
                    value_codings__code__in=discharge_to_hospice_codes,
                )
                .exists()
            )

            if has_discharge_to_hospice:
                log.debug(f"CMS138v14: Found discharge to hospice for patient {patient.id}")
                return True

            has_hospice_assessment = (
                Observation.objects.for_patient(patient.id)
                .committed()
                .filter(
                    effective_datetime__gte=start_date,
                    effective_datetime__lte=end_date,
                    codings__code=HOSPICE_CARE_MDS_LOINC,
                    value_codings__code=YES_QUALIFIER_SNOMED,
                )
                .exists()
            )

            if has_hospice_assessment:
                log.debug(f"CMS138v14: Found hospice care assessment for patient {patient.id}")
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
                    log.debug(f"CMS138v14: Found hospice care claim for patient {patient.id}")
                    return True

            has_hospice_order = (
                Instruction.objects.for_patient(patient.id)
                .committed()
                .find(HospiceCareAmbulatory)
                .filter(
                    note__datetime_of_service__gte=start_date,
                    note__datetime_of_service__lte=end_date,
                )
                .exists()
            )

            if has_hospice_order:
                log.debug(f"CMS138v14: Found hospice care order for patient {patient.id}")
                return True

            return False

        except Exception:
            log.error("CMS138v14: Error checking hospice status")
            return False

    def _get_screening_data(self, patient: Patient) -> ScreeningData:
        """Get tobacco screening and intervention data for the patient."""
        result = ScreeningData()

        tobacco_user_codes = self._get_value_set_codes(TobaccoUser, "SNOMEDCT")
        tobacco_non_user_codes = self._get_value_set_codes(TobaccoNonUser, "SNOMEDCT")
        screening_codes = self._get_value_set_codes(TobaccoUseScreening, "LOINC")

        log.debug(
            f"CMS138v14: TobaccoUser codes: {len(tobacco_user_codes)}, "
            f"TobaccoNonUser codes: {len(tobacco_non_user_codes)}"
        )

        if tobacco_user_codes or tobacco_non_user_codes:
            self._check_interview_responses(
                patient, result, tobacco_user_codes, tobacco_non_user_codes
            )

        if not result.has_screening() and screening_codes:
            self._check_observation_screening(
                patient, result, screening_codes, tobacco_user_codes, tobacco_non_user_codes
            )

        if result.is_tobacco_user():
            intervention_start = self.timeframe.start.shift(
                months=-CESSATION_INTERVENTION_LOOKBACK_MONTHS
            )
            intervention_end = self.timeframe.end

            result.counseling_date = self._get_counseling_date(
                patient, intervention_start, intervention_end
            )
            result.pharmacotherapy_date = self._get_pharmacotherapy_date(
                patient, intervention_start, intervention_end
            )

        return result

    def _check_interview_responses(
        self,
        patient: Patient,
        result: ScreeningData,
        tobacco_user_codes: set[str],
        tobacco_non_user_codes: set[str],
    ) -> None:
        """Check InterviewQuestionResponse for tobacco screening results.

        Searches for interview responses with response codes in TobaccoUser or TobaccoNonUser
        value sets. This matches legacy behavior which finds interviews by looking for responses
        with SNOMED codes, regardless of the question code (which may be INTERNAL).
        """
        try:
            all_response_codes = tobacco_user_codes | tobacco_non_user_codes
            if not all_response_codes:
                return

            most_recent_response = (
                InterviewQuestionResponse.objects.filter(
                    interview__patient=patient,
                    interview__deleted=False,
                    interview__entered_in_error__isnull=True,
                    interview__committer_id__isnull=False,
                    interview__created__gte=self.timeframe.start.datetime,
                    interview__created__lte=self.timeframe.end.datetime,
                    response_option__code__in=all_response_codes,
                )
                .select_related("interview", "response_option")
                .order_by("-interview__created")
                .first()
            )

            if most_recent_response:
                screening_date = arrow.get(most_recent_response.interview.created)
                response_code = most_recent_response.response_option.code

                if response_code in tobacco_user_codes:
                    result.most_recent_user = screening_date
                    log.debug(
                        f"CMS138v14: Most recent screening indicates TOBACCO USER on {screening_date}"
                    )
                elif response_code in tobacco_non_user_codes:
                    result.most_recent_non_user = screening_date
                    log.debug(
                        f"CMS138v14: Most recent screening indicates NON-USER on {screening_date}"
                    )

        except Exception:
            log.error("CMS138v14: Error checking interview responses")

    def _check_observation_screening(
        self,
        patient: Patient,
        result: ScreeningData,
        screening_codes: set[str],
        tobacco_user_codes: set[str],
        tobacco_non_user_codes: set[str],
    ) -> None:
        """Check Observation model for tobacco screening results (fallback)."""
        try:
            screening_obs = (
                Observation.objects.for_patient(patient.id)
                .committed()
                .filter(
                    effective_datetime__gte=self.timeframe.start.datetime,
                    effective_datetime__lte=self.timeframe.end.datetime,
                    codings__code__in=screening_codes,
                )
                .order_by("-effective_datetime")
                .first()
            )

            if screening_obs:
                obs_date = arrow.get(screening_obs.effective_datetime)

                if hasattr(screening_obs, "value_codings"):
                    for coding in screening_obs.value_codings.all():
                        if coding.code in tobacco_user_codes:
                            result.most_recent_user = obs_date
                            log.debug(
                                f"CMS138v14: Found tobacco USER via observation on {obs_date}"
                            )
                            return
                        if coding.code in tobacco_non_user_codes:
                            result.most_recent_non_user = obs_date
                            log.debug(
                                f"CMS138v14: Found tobacco NON-USER via observation on {obs_date}"
                            )
                            return

        except Exception:
            log.error("CMS138v14: Error checking observation screening")

    def _get_counseling_date(
        self, patient: Patient, start: "arrow.Arrow", end: "arrow.Arrow"
    ) -> "arrow.Arrow | None":
        """Get date of most recent tobacco cessation counseling."""
        try:
            most_recent = None

            most_recent = self._get_instruction_counseling_date(patient, start, end, most_recent)

            counseling_cpt = self._get_value_set_codes(TobaccoUseCessationCounseling, "CPT")

            if counseling_cpt:
                claim = (
                    ClaimLineItem.objects.filter(
                        claim__note__patient=patient,
                        status="active",
                        from_date__gte=start.date().isoformat(),
                        from_date__lte=end.date().isoformat(),
                        proc_code__in=counseling_cpt,
                    )
                    .order_by("-from_date")
                    .first()
                )

                if claim and claim.from_date:
                    claim_date = arrow.get(claim.from_date)
                    if most_recent is None or claim_date > most_recent:
                        most_recent = claim_date
                        log.debug(f"CMS138v14: Found counseling CPT claim on {most_recent}")

            counseling_snomed = self._get_value_set_codes(TobaccoUseCessationCounseling, "SNOMEDCT")
            if counseling_snomed:
                obs = (
                    Observation.objects.for_patient(patient.id)
                    .committed()
                    .filter(
                        effective_datetime__gte=start.datetime,
                        effective_datetime__lte=end.datetime,
                        codings__code__in=counseling_snomed,
                    )
                    .order_by("-effective_datetime")
                    .first()
                )

                if obs and obs.effective_datetime:
                    obs_date = arrow.get(obs.effective_datetime)
                    if most_recent is None or obs_date > most_recent:
                        most_recent = obs_date
                        log.debug(f"CMS138v14: Found counseling observation on {most_recent}")

            most_recent = self._get_z71_6_counseling_date(patient, start, end, most_recent)

            return most_recent

        except Exception:
            log.error("CMS138v14: Error getting counseling date")
            return None

    def _get_z71_6_counseling_date(
        self,
        patient: Patient,
        start: "arrow.Arrow",
        end: "arrow.Arrow",
        current_most_recent: "arrow.Arrow | None",
    ) -> "arrow.Arrow | None":
        """Get counseling date from Z71.6 diagnosis (Tobacco abuse counseling)."""
        most_recent = current_most_recent

        try:
            log.debug(
                f"CMS138v14: Checking Z71.6 for patient {patient.id}, "
                f"codes={Z71_6_TOBACCO_COUNSELING_CODES}, start={start.date()}, end={end.date()}"
            )

            z71_6_condition = (
                Condition.objects.for_patient(patient.id)
                .committed()
                .filter(
                    entered_in_error_id__isnull=True,
                    codings__code__in=Z71_6_TOBACCO_COUNSELING_CODES,
                    onset_date__gte=start.date(),
                    onset_date__lte=end.date(),
                )
                .order_by("-onset_date")
                .first()
            )

            log.debug(f"CMS138v14: Z71.6 condition result: {z71_6_condition}")

            if z71_6_condition and z71_6_condition.onset_date:
                z71_date = arrow.get(z71_6_condition.onset_date)

                if most_recent is None or z71_date > most_recent:
                    most_recent = z71_date
                    log.debug(f"CMS138v14: Found Z71.6 diagnosis on {most_recent}")

        except Exception:
            log.error("CMS138v14: Error checking Z71.6 diagnosis")

        return most_recent

    def _get_instruction_counseling_date(
        self,
        patient: Patient,
        start: "arrow.Arrow",
        end: "arrow.Arrow",
        current_most_recent: "arrow.Arrow | None",
    ) -> "arrow.Arrow | None":
        """Get counseling date from Instruction model."""
        most_recent = current_most_recent

        try:
            instruction = (
                Instruction.objects.for_patient(patient.id)
                .committed()
                .find(TobaccoUseCessationCounseling)
                .filter(
                    note__datetime_of_service__gte=start.datetime,
                    note__datetime_of_service__lte=end.datetime,
                )
                .order_by("-note__datetime_of_service")
                .first()
            )

            if instruction and instruction.note and instruction.note.datetime_of_service:
                instruction_date = arrow.get(instruction.note.datetime_of_service)
                if most_recent is None or instruction_date > most_recent:
                    most_recent = instruction_date
                    log.debug(f"CMS138v14: Found counseling instruction on {most_recent}")

        except Exception:
            log.error("CMS138v14: Error checking instruction counseling")

        return most_recent

    def _get_pharmacotherapy_date(
        self, patient: Patient, start: "arrow.Arrow", end: "arrow.Arrow"
    ) -> "arrow.Arrow | None":
        """Get date of most recent tobacco cessation pharmacotherapy."""
        try:
            start_datetime = start.datetime
            end_datetime = end.datetime
            start_date = start.date()
            end_date = end.date()

            most_recent = None

            ordered_med = (
                Medication.objects.for_patient(patient.id)
                .committed()
                .find(TobaccoUseCessationPharmacotherapy)
                .filter(
                    entered_in_error__isnull=True,
                    start_date__gte=start_datetime,
                    start_date__lte=end_datetime,
                )
                .order_by("-start_date")
                .first()
            )

            if ordered_med and ordered_med.start_date:
                most_recent = arrow.get(ordered_med.start_date)
                log.debug(f"CMS138v14: Found pharmacotherapy order on {most_recent}")

            active_med = (
                Medication.objects.for_patient(patient.id)
                .committed()
                .find(TobaccoUseCessationPharmacotherapy)
                .filter(entered_in_error__isnull=True)
                .filter(
                    Q(
                        start_date__lte=end_date,
                        end_date__gte=start_date,
                        end_date__isnull=False,
                    )
                    | Q(start_date__lte=end_date, end_date__isnull=True)
                )
                .order_by("-start_date")
                .first()
            )

            if active_med and active_med.start_date:
                active_date = arrow.get(active_med.start_date)
                if most_recent is None or active_date > most_recent:
                    most_recent = active_date
                    log.debug(f"CMS138v14: Found active pharmacotherapy on {most_recent}")

            return most_recent

        except Exception:
            log.error("CMS138v14: Error getting pharmacotherapy date")
            return None

    def _compute_populations(self, screening_data: ScreeningData) -> None:
        """Compute population membership for all three CMS138v14 performance rates."""
        # Population 1 - Screening rate (all patients in initial population)
        self._populations[self.POPULATION_1].in_initial_population = True
        self._populations[self.POPULATION_1].in_denominator = True
        self._populations[self.POPULATION_1].in_numerator = screening_data.has_screening()

        # Population 2 - Intervention rate (only screened tobacco users in denominator)
        self._populations[self.POPULATION_2].in_initial_population = True
        is_screened_tobacco_user = (
            screening_data.has_screening() and screening_data.is_tobacco_user()
        )
        self._populations[self.POPULATION_2].in_denominator = is_screened_tobacco_user
        self._populations[self.POPULATION_2].in_numerator = (
            is_screened_tobacco_user and screening_data.has_intervention()
        )

        # Population 3 - Overall rate (MIPS accountability - all in IP in denominator)
        self._populations[self.POPULATION_3].in_initial_population = True
        self._populations[self.POPULATION_3].in_denominator = True
        if screening_data.is_tobacco_non_user():
            self._populations[self.POPULATION_3].in_numerator = True
        elif screening_data.is_tobacco_user():
            self._populations[self.POPULATION_3].in_numerator = screening_data.has_intervention()
        else:
            self._populations[self.POPULATION_3].in_numerator = False

    def _get_value_set_codes(self, value_sets: Any, *attributes: str) -> set[str]:
        """Get codes from one or more value sets for specified code systems."""
        if not isinstance(value_sets, tuple):
            value_sets = (value_sets,)
        return {
            code
            for vs in value_sets
            for attr in attributes
            for code in (getattr(vs, attr, None) or [])
        }

    def _create_not_applicable_card(self, patient: Patient) -> Effect:
        """Create a NOT_APPLICABLE protocol card."""
        card = ProtocolCard(
            patient_id=patient.id,
            key=self.protocol_key(),
            title=self.Meta.title,
            narrative="",
            status=ProtocolCard.Status.NOT_APPLICABLE,
        )
        return card.apply()

    def _create_satisfied_card(self, patient: Patient, screening_data: ScreeningData) -> Effect:
        """Create a SATISFIED protocol card for patient in numerator."""
        narrative_parts: list[str] = []
        patient_name = patient.first_name or "Patient"

        if screening_data.is_tobacco_user() and screening_data.most_recent_user:
            screening_date_str = screening_data.most_recent_user.format("M/D/YY")
            narrative_parts.append(
                f"{patient_name} was screened for tobacco use on {screening_date_str} "
                "and identified as a tobacco user."
            )

            if screening_data.counseling_date:
                counseling_date_str = screening_data.counseling_date.format("M/D/YY")
                narrative_parts.append(f"Received cessation counseling on {counseling_date_str}.")

            if screening_data.pharmacotherapy_date:
                pharma_date_str = screening_data.pharmacotherapy_date.format("M/D/YY")
                narrative_parts.append(f"Cessation pharmacotherapy started {pharma_date_str}.")

        elif screening_data.is_tobacco_non_user() and screening_data.most_recent_non_user:
            screening_date_str = screening_data.most_recent_non_user.format("M/D/YY")
            narrative_parts.append(
                f"{patient_name} was screened for tobacco use on {screening_date_str} "
                "and identified as a non-tobacco user."
            )

        if not narrative_parts:
            narrative_parts.append(f"{patient_name} has completed tobacco use screening.")

        narrative = " ".join(narrative_parts)

        card = ProtocolCard(
            patient_id=patient.id,
            key=self.protocol_key(),
            title=self.Meta.title,
            narrative=narrative,
            status=ProtocolCard.Status.SATISFIED,
            due_in=-1,
            can_be_snoozed=True,
        )
        return card.apply()

    def _create_due_card(self, patient: Patient, screening_data: ScreeningData) -> Effect:
        """Create a DUE protocol card with actionable recommendations."""
        patient_name = patient.first_name or "Patient"

        if screening_data.is_tobacco_user():
            narrative = f"{patient_name} is a current tobacco user, intervention is indicated."
        else:
            narrative = f"{patient_name} should be screened for tobacco use."

        card = ProtocolCard(
            patient_id=patient.id,
            key=self.protocol_key(),
            title=self.Meta.title,
            narrative=narrative,
            status=ProtocolCard.Status.DUE,
            due_in=-1,
            can_be_snoozed=True,
        )

        if not screening_data.has_screening():
            self._add_screening_recommendation(card)
        elif screening_data.is_tobacco_user():
            self._add_counseling_recommendation(card)
            self._add_pharmacotherapy_recommendation(card)

        return card.apply()

    def _add_screening_recommendation(self, card: ProtocolCard) -> None:
        """Add tobacco screening questionnaire recommendation."""
        command = QuestionnaireCommand()
        recommendation = command.recommend(
            title="Complete tobacco use questionnaire",
            button="Plan",
        )
        card.recommendations.append(recommendation)

    def _add_counseling_recommendation(self, card: ProtocolCard) -> None:
        """Add tobacco cessation counseling recommendation."""
        counseling_codes = self._get_value_set_codes(TobaccoUseCessationCounseling, "SNOMEDCT")

        if counseling_codes:
            code = next(iter(counseling_codes))
            command = InstructCommand(
                coding={
                    "system": CodeSystems.SNOMED,
                    "code": code,
                },
            )
        else:
            command = InstructCommand()

        recommendation = command.recommend(
            title="Tobacco cessation counseling",
            button="Plan",
        )
        card.recommendations.append(recommendation)

    def _add_pharmacotherapy_recommendation(self, card: ProtocolCard) -> None:
        """Add tobacco cessation pharmacotherapy recommendation."""
        command = PrescribeCommand()
        recommendation = command.recommend(
            title="Cessation support medication",
            button="Plan",
        )
        card.recommendations.append(recommendation)
