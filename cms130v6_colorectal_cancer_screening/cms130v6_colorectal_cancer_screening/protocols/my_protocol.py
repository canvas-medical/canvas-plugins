from typing import Any

from canvas_sdk.commands import LabOrderCommand, ImagingOrderCommand, ReferCommand
from canvas_sdk.commands.constants import ServiceProvider
from canvas_sdk.effects import Effect
from canvas_sdk.effects.protocol_card.protocol_card import ProtocolCard
from canvas_sdk.events import EventType
from canvas_sdk.protocols import ClinicalQualityMeasure
from canvas_sdk.v1.data import Patient
from canvas_sdk.v1.data.appointment import Appointment
from canvas_sdk.v1.data.condition import Condition, ConditionCoding
from canvas_sdk.v1.data.imaging import ImagingReport
from canvas_sdk.v1.data.lab import LabReport, LabTest
from canvas_sdk.v1.data.note import Note, NoteType, PracticeLocationPOS
from canvas_sdk.v1.data.referral import ReferralReport
# Import from v2022 (existing value sets)
# from canvas_sdk.value_set.v2022.condition import MalignantNeoplasmOfColon
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
        information = "https://ecqi.healthit.gov/sites/default/files/ecqm/measures/CMS130v6.html"
        identifiers = ["CMS130v6"]
        types = ["CQM"]
        authors = ["Centers for Medicare & Medicaid Services"]
        references = [
            "https://ecqi.healthit.gov/sites/default/files/ecqm/measures/CMS130v6.html"
        ]

    RESPONDS_TO = EventType.Name(EventType.APPOINTMENT_CREATED)

    # Age range constants
    AGE_RANGE_START = 50
    AGE_RANGE_END = 75

    def _get_patient_id(self) -> str | None:
        try:
            appointment_id = self.event.target.id
            appointment = Appointment.objects.select_related("patient").get(id=appointment_id)
            if appointment and appointment.patient:
                return appointment.patient.id
            log.warning(f"CMS130v6: Could not find patient for appointment {appointment_id}")
            return None
        except Exception as e:
            log.error(f"CMS130v6: Error getting patient ID: {str(e)}")
            return None

    def compute(self) -> list[Effect]:
        try:
            # patient_id = self._get_patient_id()
            patient_id = self.context.get("patient", {}).get("id")
            if not patient_id:
                log.warning("CMS130v6: Could not determine patient ID from event, skipping")
                return []

            log.info(f"CMS130v6: Processing event for patient_id={patient_id}")

            patient = Patient.objects.filter(id=patient_id).first()
            if not patient:
                log.warning(f"CMS130v6: Patient {patient_id} not found, skipping")
                return []

            if not self._in_initial_population(patient):
                log.info(f"CMS130v6: Patient {patient_id} not in initial population")
                return [self._create_not_applicable_card(patient)]

            if not self._in_denominator(patient):
                log.info(f"CMS130v6: Patient {patient_id} excluded from denominator")
                return [self._create_not_applicable_card(patient)]

            last_exam = self._get_most_recent_screening(patient)
            if self._in_numerator(patient):
                log.info(f"CMS130v6: Patient {patient_id} meets numerator criteria")
                return [self._create_satisfied_card(patient, last_exam)]
            else:
                log.info(f"CMS130v6: Patient {patient_id} does not meet numerator criteria")
                return [self._create_due_card(patient)]

        except Exception as e:
            log.error(f"CMS130v6: Error in protocol compute: {str(e)}")
            return []

    def _in_initial_population(self, patient: Patient) -> bool:
        if not self._check_age_50_to_75(patient):
            log.info(f"CMS130v6: Patient {patient.id} not in age 50-75 range")
            return False

        if not self._has_eligible_encounter_in_period(patient):
            log.info(f"CMS130v6: Patient {patient.id} does not have eligible encounter in period")
            return False

        return True

    def _in_denominator(self, patient: Patient) -> bool:
        if not self._in_initial_population(patient):
            log.info(f"CMS130v6: Patient {patient.id} not in initial population")
            return False

        if self._has_colon_exclusion(patient):
            log.info(f"CMS130v6: Patient {patient.id} has colon exclusion")
            return False

        if self._has_hospice_care_in_period(patient):
            log.info(f"CMS130v6: Patient {patient.id} in hospice care")
            return False

        return True

    def _in_numerator(self, patient: Patient) -> bool:
        # Check all screening types with appropriate lookback periods
        # FOBT: within measurement period
        fobt_period_start = self.timeframe.end.shift(years=-1)
        fobt_report = self._find_lab_report(patient, FecalOccultBloodTestFobt, fobt_period_start, self.timeframe.end)
        if fobt_report:
            return True

        # FIT-DNA: within 3 years prior (measurement period + 2 years prior)
        fit_dna_period_start = self.timeframe.end.shift(years=-3)
        fit_dna_report = self._find_lab_report(patient, FitDna, fit_dna_period_start, self.timeframe.end)
        if fit_dna_report:
            return True

        # Flexible Sigmoidoscopy: within 5 years prior
        sigmoid_period_start = self.timeframe.end.shift(years=-5)
        sigmoid_imaging = self._find_imaging_report(patient, FlexibleSigmoidoscopy, sigmoid_period_start, self.timeframe.end)
        if sigmoid_imaging:
            return True
        sigmoid_referral = self._find_referral_report(patient, FlexibleSigmoidoscopy, sigmoid_period_start, self.timeframe.end)
        if sigmoid_referral:
            return True

        # CT Colonography: within 5 years prior
        ct_period_start = self.timeframe.end.shift(years=-5)
        ct_imaging = self._find_imaging_report(patient, CtColonography, ct_period_start, self.timeframe.end)
        if ct_imaging:
            return True
        ct_imaging_v6 = self._find_imaging_report(patient, CMS130v6CtColonography, ct_period_start, self.timeframe.end)
        if ct_imaging_v6:
            return True
        ct_referral = self._find_referral_report(patient, CtColonography, ct_period_start, self.timeframe.end)
        if ct_referral:
            return True
        ct_referral_v6 = self._find_referral_report(patient, CMS130v6CtColonography, ct_period_start, self.timeframe.end)
        if ct_referral_v6:
            return True

        # Colonoscopy: within 10 years prior
        colon_period_start = self.timeframe.end.shift(years=-10)
        colon_imaging = self._find_imaging_report(patient, Colonoscopy, colon_period_start, self.timeframe.end)
        if colon_imaging:
            return True
        colon_referral = self._find_referral_report(patient, Colonoscopy, colon_period_start, self.timeframe.end)
        if colon_referral:
            return True

        return False

    def _check_age_50_to_75(self, patient: Patient) -> bool:
        try:
            if not getattr(patient, "birth_date", None):
                log.info("CMS130v6: Missing birth_date; patient fails age check")
                return False

            # Use arrow.get which is allowed
            import arrow
            birth_date = arrow.get(patient.birth_date)
            age_years = (self.now - birth_date).days // 365

            in_range = self.AGE_RANGE_START <= age_years <= self.AGE_RANGE_END
            log.info(
                f"CMS130v6: Patient {patient.id} age {age_years} in 50-75 range={in_range}"
            )
            return in_range
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

                # NoteType inherits from Coding, so it has code and system directly
                note_type = note.note_type_version
                for value_set_class in visit_value_sets:
                    if self._coding_in_value_set_for_note_type(note_type, value_set_class):
                        log.info(
                            f"CMS130v6: Found eligible encounter for patient {patient.id} on {note.datetime_of_service}"
                        )
                        return True

            # If no matches found, return True for now (similar to CMS131v14)
            # This can be refined later when NoteType coding structure is better understood
            log.info(f"CMS130v6: No matching visit types found, defaulting to True for patient {patient.id}")
            return True
        except Exception as e:
            log.error(f"CMS130v6: Error checking eligible encounters: {str(e)}")
            return True

    def _has_colon_exclusion(self, patient: Patient) -> bool:
        try:
            conditions = Condition.objects.for_patient(patient.id).active()

            for condition in conditions:
                # Check if condition overlaps with measurement period
                if condition.resolution_date and condition.resolution_date < self.timeframe.start.date():
                    continue
                if condition.onset_date and condition.onset_date > self.timeframe.end.date():
                    continue

                for coding in condition.codings.all():
                    if self._coding_in_value_set(coding, TotalColectomy):
                        log.info(
                            f"CMS130v6: Found TotalColectomy exclusion for patient {patient.id}"
                        )
                        return True
                    # TODO: fix importing
                    # if self._coding_in_value_set(coding, MalignantNeoplasmOfColon):
                    #     log.info(
                    #         f"CMS130v6: Found MalignantNeoplasmOfColon exclusion for patient {patient.id}"
                    #     )
                    #     return True

            return False
        except Exception as e:
            log.error(f"CMS130v6: Error checking colon exclusions: {str(e)}")
            return False

    def _has_hospice_care_in_period(self, patient: Patient) -> bool:
        try:
            hospice_notes = Note.objects.filter(
                patient__id=patient.id,
                place_of_service=PracticeLocationPOS.HOSPICE,
                datetime_of_service__range=(
                    self.timeframe.start.datetime,
                    self.timeframe.end.datetime,
                ),
            )

            if hospice_notes.exists():
                log.info(f"CMS130v6: Found hospice care for patient {patient.id}")
                return True

            return False
        except Exception as e:
            log.error(f"CMS130v6: Error checking hospice care: {str(e)}")
            return False

    def _find_lab_report(
        self, patient: Patient, value_set_class, period_start: Any, period_end: Any
    ) -> LabReport | None:
        try:
            # Get value set codes (LOINC codes for lab tests)
            value_set_codes = set()
            if hasattr(value_set_class, "LOINC"):
                value_set_codes.update(value_set_class.LOINC)

            if not value_set_codes:
                log.warning(f"CMS130v6: No LOINC codes found in value set {value_set_class.__name__}")
                return None

            # Query LabTest objects that match the value set codes and are within timeframe
            matching_tests = LabTest.objects.filter(
                report__patient__id=patient.id,
                report__original_date__range=(period_start.datetime, period_end.datetime),
                report__junked=False,
                ontology_test_code__in=value_set_codes,
            ).select_related("report").order_by("-report__original_date")

            if matching_tests.exists():
                test = matching_tests.first()
                if test.report:
                    log.info(
                        f"CMS130v6: Found matching lab report {test.report.id} with test code {test.ontology_test_code}"
                    )
                    return test.report

            return None
        except Exception as e:
            log.error(f"CMS130v6: Error finding lab report: {str(e)}")
            return None

    def _find_imaging_report(
        self, patient: Patient, value_set_class, period_start: Any, period_end: Any
    ) -> ImagingReport | None:
        try:
            # Use the find() method to match via codings
            reports = (
                ImagingReport.objects.for_patient(patient.id)
                .filter(
                    original_date__range=(period_start.date(), period_end.date()),
                    junked=False,
                )
                .find(value_set_class)
                .order_by("-original_date")
            )

            if reports.exists():
                report = reports.first()
                log.info(f"CMS130v6: Found matching imaging report {report.id}")
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
                report = reports.first()
                log.info(f"CMS130v6: Found matching referral report {report.id}")
                return report

            return None
        except Exception as e:
            log.error(f"CMS130v6: Error finding referral report: {str(e)}")
            return None

    def _get_most_recent_screening(self, patient: Patient) -> dict | None:
        """Get the most recent screening with its type and date."""
        most_recent = None
        most_recent_date = None

        # Check all screening types
        screenings = []

        # FOBT
        fobt_period_start = self.timeframe.end.shift(years=-1)
        fobt_report = self._find_lab_report(patient, FecalOccultBloodTestFobt, fobt_period_start, self.timeframe.end)
        if fobt_report:
            screenings.append(("FOBT", fobt_report.original_date))

        # FIT-DNA
        fit_dna_period_start = self.timeframe.end.shift(years=-3)
        fit_dna_report = self._find_lab_report(patient, FitDna, fit_dna_period_start, self.timeframe.end)
        if fit_dna_report:
            screenings.append(("FIT-DNA", fit_dna_report.original_date))

        # Flexible Sigmoidoscopy
        sigmoid_period_start = self.timeframe.end.shift(years=-5)
        sigmoid_imaging = self._find_imaging_report(patient, FlexibleSigmoidoscopy, sigmoid_period_start, self.timeframe.end)
        if sigmoid_imaging:
            screenings.append(("Flexible Sigmoidoscopy", sigmoid_imaging.original_date))
        sigmoid_referral = self._find_referral_report(patient, FlexibleSigmoidoscopy, sigmoid_period_start, self.timeframe.end)
        if sigmoid_referral:
            screenings.append(("Flexible Sigmoidoscopy", sigmoid_referral.original_date))

        # CT Colonography
        ct_period_start = self.timeframe.end.shift(years=-5)
        ct_imaging = self._find_imaging_report(patient, CtColonography, ct_period_start, self.timeframe.end)
        if ct_imaging:
            screenings.append(("CT Colonography", ct_imaging.original_date))
        ct_imaging_v6 = self._find_imaging_report(patient, CMS130v6CtColonography, ct_period_start, self.timeframe.end)
        if ct_imaging_v6:
            screenings.append(("CT Colonography", ct_imaging_v6.original_date))
        ct_referral = self._find_referral_report(patient, CtColonography, ct_period_start, self.timeframe.end)
        if ct_referral:
            screenings.append(("CT Colonography", ct_referral.original_date))
        ct_referral_v6 = self._find_referral_report(patient, CMS130v6CtColonography, ct_period_start, self.timeframe.end)
        if ct_referral_v6:
            screenings.append(("CT Colonography", ct_referral_v6.original_date))

        # Colonoscopy
        colon_period_start = self.timeframe.end.shift(years=-10)
        colon_imaging = self._find_imaging_report(patient, Colonoscopy, colon_period_start, self.timeframe.end)
        if colon_imaging:
            screenings.append(("Colonoscopy", colon_imaging.original_date))
        colon_referral = self._find_referral_report(patient, Colonoscopy, colon_period_start, self.timeframe.end)
        if colon_referral:
            screenings.append(("Colonoscopy", colon_referral.original_date))

        # Find most recent
        import arrow
        for screening_type, screening_date in screenings:
            # Convert to arrow for consistent comparison
            if screening_date:
                # Use arrow.get which is allowed (arrow.Arrow type is not allowed)
                date_arrow = arrow.get(screening_date) if screening_date else None
                
                if date_arrow and (most_recent_date is None or date_arrow > most_recent_date):
                    most_recent_date = date_arrow
                    most_recent = {"type": screening_type, "date": date_arrow}

        return most_recent

    def _create_not_applicable_card(self, patient: Patient) -> Effect:
        card = ProtocolCard(
            patient_id=patient.id,
            key="CMS130v6",
            title="Colorectal Cancer Screening",
            narrative="",
            status=ProtocolCard.Status.NOT_APPLICABLE,
        )

        return card.apply()

    def _create_satisfied_card(self, patient: Patient, last_exam: dict | None) -> Effect:
        if last_exam and last_exam.get("date"):
            import arrow
            exam_date = arrow.get(last_exam["date"]).format("MMMM D, YYYY")
            narrative = f"{patient.first_name} has had appropriate colorectal cancer screening ({last_exam.get('type', 'screening')} on {exam_date})."
        else:
            narrative = f"{patient.first_name} has had appropriate colorectal cancer screening."

        card = ProtocolCard(
            patient_id=patient.id,
            key="CMS130v6",
            title="Colorectal Cancer Screening",
            narrative=narrative,
            status=ProtocolCard.Status.SATISFIED,
            due_in=-1,
            can_be_snoozed=True,
        )

        return card.apply()

    def _create_due_card(self, patient: Patient) -> Effect:
        narrative = f"{patient.first_name} is due for colorectal cancer screening."

        card = ProtocolCard(
            patient_id=patient.id,
            key="CMS130v6",
            title="Colorectal Cancer Screening",
            narrative=narrative,
            status=ProtocolCard.Status.DUE,
            due_in=-1,
            can_be_snoozed=True,
        )

        # Add recommendations for all screening options
        # FOBT - LabOrderCommand
        fobt_codes = list(FecalOccultBloodTestFobt.LOINC)[:1] if hasattr(FecalOccultBloodTestFobt, "LOINC") else []
        if fobt_codes:
            fobt_command = LabOrderCommand(tests_order_codes=fobt_codes)
            card.recommendations.append(
                fobt_command.recommend(title="Order FOBT (Fecal Occult Blood Test)", button="Order Lab")
            )

        # FIT-DNA - LabOrderCommand
        fit_dna_codes = list(FitDna.LOINC)[:1] if hasattr(FitDna, "LOINC") else []
        if fit_dna_codes:
            fit_dna_command = LabOrderCommand(tests_order_codes=fit_dna_codes)
            card.recommendations.append(
                fit_dna_command.recommend(title="Order FIT-DNA", button="Order Lab")
            )

        # CT Colonography - ImagingOrderCommand
        # Use CPT codes from CMS130v6CtColonography value set
        ct_cpt_codes = list(CMS130v6CtColonography.CPT)[:1] if hasattr(CMS130v6CtColonography, "CPT") else []
        if ct_cpt_codes:
            ct_command = ImagingOrderCommand(image_code=ct_cpt_codes[0])
            card.recommendations.append(
                ct_command.recommend(title="Order CT Colonography", button="Order Imaging")
            )

        # Colonoscopy - ReferCommand
        colonoscopy_command = ReferCommand(
            service_provider=ServiceProvider(
                first_name="Referral",
                last_name="Gastroenterology",
                specialty="Gastroenterology",
                practice_name="Gastroenterology Referral Network",
                notes="For colonoscopy screening.",
            ),
            include_visit_note=False,
        )
        card.recommendations.append(
            colonoscopy_command.recommend(title="Refer for Colonoscopy", button="Refer")
        )

        # Flexible Sigmoidoscopy - ReferCommand
        sigmoid_command = ReferCommand(
            service_provider=ServiceProvider(
                first_name="Referral",
                last_name="Gastroenterology",
                specialty="Gastroenterology",
                practice_name="Gastroenterology Referral Network",
                notes="For flexible sigmoidoscopy screening.",
            ),
            include_visit_note=False,
        )
        card.recommendations.append(
            sigmoid_command.recommend(title="Refer for Flexible Sigmoidoscopy", button="Refer")
        )

        return card.apply()

    def _coding_in_value_set(self, coding: ConditionCoding, value_set_class) -> bool:
        """Check if a ConditionCoding belongs to a value set."""
        try:
            normalized_system = coding.system.replace("-", "").upper()
            normalized_code = coding.code.replace(".", "")

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
