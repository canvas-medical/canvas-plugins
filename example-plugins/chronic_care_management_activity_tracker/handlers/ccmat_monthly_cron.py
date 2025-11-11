from datetime import datetime
from uuid import uuid4

import arrow
from django.db.models import Q

from canvas_sdk.commands.commands.diagnose import DiagnoseCommand
from canvas_sdk.effects import Effect
from canvas_sdk.effects.billing_line_item import AddBillingLineItem
from canvas_sdk.effects.note import Note as NoteEffect
from canvas_sdk.handlers.cron_task import CronTask
from canvas_sdk.v1.data.care_team import CareTeamMembership, CareTeamMembershipStatus
from canvas_sdk.v1.data.note import Note, NoteStates, NoteType
from canvas_sdk.v1.data.patient import Patient
from canvas_sdk.v1.data.questionnaire import Questionnaire
from logger import log


class CcmatMonthlyCron(CronTask):
    """A cron task that runs monthly for Chronic Care Management Activity Tracker."""
    # A cron string.
    #           ┌───────────── minute (0 - 59)
    #           │ ┌───────────── hour (0 - 23)
    #           │ │ ┌───────────── day of the month (1 - 31)
    #           │ │ │ ┌───────────── month (1 - 12)
    #           │ │ │ │ ┌───────────── day of the week (0 - 6) (Sunday to Saturday)
    #           │ │ │ │ │
    #           │ │ │ │ │
    #           │ │ │ │ │
    SCHEDULE = "0 0 1 * *"  # Run at midnight on the 1st of every month.

    QUESTIONNAIRE_CODE = "ccm_session_questionnaire"
    NOTE_TYPE_CODE = "monthly_summary"
    CCM_PROVIDER_ROLE_CODE = "chronic_care_management_provider"
    CCM_DIAGNOSIS_KEY = "ccm_diagnosis"
    MINUTES_THRESHOLD = 20

    @staticmethod
    def _parse_time_to_minutes(time_str: str) -> int:
        """
        Convert HH:mm:ss format to total minutes.

        Args:
            time_str: Time string in HH:mm:ss format (e.g., "01:25:30")

        Returns:
            Total minutes as an integer (rounds up if seconds >= 30)
        """
        time_parts = time_str.strip().split(':')
        if len(time_parts) != 3:
            raise ValueError(f"Invalid time format: {time_str}. Expected HH:mm:ss")

        hours = int(time_parts[0])
        minutes = int(time_parts[1])
        seconds = int(time_parts[2])

        # Convert to total minutes (round up if seconds >= 30)
        total_minutes = hours * 60 + minutes + (1 if seconds >= 30 else 0)
        return total_minutes

    def execute(self) -> list[Effect]:
        """The logic to be executed on the defined schedule."""
        log.info(f"Running CCM monthly cron at {self.target}")

        effects = []

        # Get the questionnaire
        questionnaire = Questionnaire.objects.filter(code=self.QUESTIONNAIRE_CODE).first()
        if not questionnaire:
            log.warning(f"Questionnaire with code {self.QUESTIONNAIRE_CODE} not found")
            return []

        # Calculate last month's date range
        now = arrow.get(self.target)
        last_month_start = now.shift(months=-1).replace(day=1, hour=0, minute=0, second=0)
        last_month_end = now.replace(day=1, hour=0, minute=0, second=0).shift(seconds=-1)

        log.info(f"Processing questionnaires from {last_month_start} to {last_month_end}")

        # Get all patients with CCM diagnosis metadata
        ccm_patients = Patient.objects.filter(
            metadata__key=self.CCM_DIAGNOSIS_KEY
        ).distinct()

        log.info(f"Found {ccm_patients.count()} patients with CCM diagnoses")

        for patient in ccm_patients:
            # Get the most recent completed questionnaire from last calendar month
            last_month_interviews = (
                patient.interviews.filter(questionnaires=questionnaire)
                .filter(
                    created__gte=last_month_start.datetime,
                    created__lte=last_month_end.datetime
                )
                .order_by("-created")
            )

            if not last_month_interviews.exists():
                log.info(f"No questionnaire found for patient {patient.id} in last month")
                continue

            # Get the most recent interview
            most_recent_interview = last_month_interviews.first()

            # Find the "Total Time Logged this Month Including this Session" response
            total_time_response = most_recent_interview.interview_responses.filter(
                question__code="ccm_month_minutes_question"
            ).first()

            if not total_time_response or not total_time_response.response_option_value:
                log.info(f"No total time response found for patient {patient.id}")
                continue

            # Extract value from the response
            response_text = total_time_response.response_option_value

            log.info(f"Patient {patient.id} logged {response_text} last month")

            total_minutes = self._parse_time_to_minutes(response_text)

            log.info(f"Patient {patient.id} total minutes: {total_minutes}")

            # Check if >= 20 minutes
            if total_minutes < self.MINUTES_THRESHOLD:
                log.info(f"Patient {patient.id} did not meet {self.MINUTES_THRESHOLD} minute threshold")
                continue

            # Create note, add diagnoses, and add billing line items
            patient_effects = self._create_ccm_note_and_billing(
                patient, response_text, most_recent_interview
            )
            effects.extend(patient_effects)

        log.info(f"Created {len(effects)} effects for CCM monthly processing")
        return effects

    def _create_ccm_note_and_billing(
            self, patient: Patient, total_time: str, _interview=None
    ) -> list[Effect]:
        """Create a note with diagnoses and billing line items for a patient."""
        effects = []

        # Get note type
        note_type = NoteType.objects.filter(code=self.NOTE_TYPE_CODE).first()
        if not note_type:
            log.error(f"Note type {self.NOTE_TYPE_CODE} not found")
            return []

        # Get CCM provider from care team with chronic_care_management_provider role
        ccm_membership = (
            CareTeamMembership.objects.filter(
                patient=patient,
                role__code=self.CCM_PROVIDER_ROLE_CODE,
                role__system="INTERNAL",
                status=CareTeamMembershipStatus.ACTIVE,
            )
            .select_related("staff")
            .first()
        )

        if not ccm_membership or not ccm_membership.staff:
            log.error(f"No CCM provider found for patient {patient.id}")
            return []

        staff = ccm_membership.staff

        # Get practice location from patient's most recent note
        most_recent_note = (
            Note.objects.filter(patient=patient)
            .exclude(
                Q(current_state__state=NoteStates.DELETED)
                | Q(current_state__state=NoteStates.CANCELLED)
            )
            .order_by("-datetime_of_service")
            .first()
        )

        practice_location_id = str(
            most_recent_note.location.id) if most_recent_note and most_recent_note.location else str(
            staff.primary_practice_location.id)

        # Create the note
        note_id = str(uuid4())
        now = datetime.now()

        log.info(
            f"Note ID {note_id} for patient {patient.id}, provider {staff.id} practice location {practice_location_id}")
        note = NoteEffect(
            instance_id=note_id,
            note_type_id=str(note_type.id),
            datetime_of_service=now,
            patient_id=str(patient.id),
            provider_id=str(staff.id),
            practice_location_id=practice_location_id,
            title=f"Chronic Care Management - Monthly Summary ({total_time})",
        )

        effects.append(note.create())

        # Get CCM diagnoses from patient metadata
        ccm_diagnoses_metadata = patient.metadata.filter(
            key=self.CCM_DIAGNOSIS_KEY
        ).first()

        if not ccm_diagnoses_metadata or not ccm_diagnoses_metadata.value:
            log.warning(f"No CCM diagnoses found for patient {patient.id}")
            icd10_codes = []
        else:
            # Parse comma-separated ICD-10 codes
            icd10_codes = [
                code.strip()
                for code in ccm_diagnoses_metadata.value.split(",")
                if code.strip()
            ]

        # Add DIAGNOSE commands for each ICD-10 code
        condition_ids = []
        for icd10_code in icd10_codes:
            diagnose_cmd = DiagnoseCommand(
                note_uuid=note_id,
                command_uuid=str(uuid4()),
                icd10_code=icd10_code,
                background=f"Chronic Care Management services provided ({total_time})",
            )
            effects.append(diagnose_cmd.originate())
            effects.append(diagnose_cmd.commit())
            # Note: We'd need the condition IDs for billing, but since we're using
            # DIAGNOSE commands which create new conditions, we can't easily get them here.
            # The billing line items will need to be added without assessment_ids initially.

        # Add billing line items based on time
        log.info(f"Adding billing line items for patient {patient.id} with total time {total_time}")
        billing_effects = self._add_billing_line_items(note_id, total_time, condition_ids)
        effects.extend(billing_effects)

        log.info(
            f"Created note and billing for patient {patient.id} with {len(icd10_codes)} diagnoses"
        )

        return effects

    def _add_billing_line_items(
            self, note_id: str, total_time: str, condition_ids: list[str]
    ) -> list[Effect]:
        """
        Add billing line items based on time logged.

        Billing logic:
        - If 20-39 minutes: Add CPT 99490 x1
        - If >= 40 minutes: Add CPT 99490 x1, plus CPT 99439 x floor((minutes - 20) / 20)

        Example: 63 minutes → 99490 x1, 99439 x2
        """
        effects = []

        # Convert HH:mm:ss format to total minutes
        total_minutes = self._parse_time_to_minutes(total_time)

        if total_minutes < self.MINUTES_THRESHOLD:
            return effects

        # Always add CPT 99490 for the first 20 minutes
        billing_99490 = AddBillingLineItem(
            note_id=note_id,
            cpt="99490",
            units=1,
            assessment_ids=condition_ids,
        )
        effects.append(billing_99490.apply())

        # If 40+ minutes, add CPT 99439 for each additional 20-minute increment
        if total_minutes >= 40:
            additional_units = (total_minutes - 20) // 20
            billing_99439 = AddBillingLineItem(
                note_id=note_id,
                cpt="99439",
                units=additional_units,
                assessment_ids=condition_ids,
            )
            effects.append(billing_99439.apply())

        return effects
