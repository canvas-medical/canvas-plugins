"""
Assessment Effects Service.

Handles creation of structured assessment effects for PDMP requests.
"""

from typing import Dict, Any, List, Optional
from uuid import uuid4

import arrow

from canvas_sdk.commands import StructuredAssessmentCommand
from canvas_sdk.effects import Effect
from canvas_sdk.v1.data.note import Note
from canvas_sdk.v1.data.questionnaire import Questionnaire
from canvas_sdk.v1.data.staff import Staff
from logger import log


class AssessmentEffectsService:
    """Service for creating structured assessment effects."""

    def create_assessment_effects(
        self, patient_id: str | None, practitioner_id: str | None, result: dict[str, Any]
    ) -> list[Effect]:
        """
        Create structured assessment effects for a successful PDMP request.

        Args:
            patient_id: Patient ID for context
            practitioner_id: Practitioner ID for context
            result: PDMP request result data

        Returns:
            List of Effects for structured assessment creation
        """
        log.info("AssessmentEffectsService: Creating structured assessment effects")

        try:
            # Check if assessment should be created
            if not self._should_create_assessment(result):
                log.info("AssessmentEffectsService: Skipping assessment creation")
                return []

            # Get the note from context
            note_id = result.get("note_id")
            if not note_id:
                log.error("AssessmentEffectsService: No note_id found in result")
                return []

            # Create the assessment
            assessment_effects = self._create_pdmp_assessment(patient_id, practitioner_id, note_id)

            log.info(
                f"AssessmentEffectsService: Created {len(assessment_effects)} assessment effects"
            )
            return assessment_effects

        except Exception as e:
            log.error(f"AssessmentEffectsService: Error creating assessment effects: {str(e)}")
            return []

    def _should_create_assessment(self, result: dict[str, Any]) -> bool:
        """Determine if a structured assessment should be created."""
        # Only create assessment if PDMP request was successful
        if result.get("status") != "success":
            log.info("AssessmentEffectsService: Skipping assessment due to failed PDMP request")
            return False

        # Check if assessment creation was already attempted and failed
        if result.get("assessment_error"):
            log.info("AssessmentEffectsService: Skipping assessment due to previous error")
            return False

        # Check if assessment was already created
        if result.get("assessment_created"):
            log.info("AssessmentEffectsService: Assessment already created")
            return False

        return True

    def _create_pdmp_assessment(
        self, patient_id: str | None, practitioner_id: str | None, note_id: str
    ) -> list[Effect]:
        """Create structured assessment command for PDMP check."""
        try:
            # Get the note and questionnaire
            note = Note.objects.get(dbid=note_id)
            questionnaire = Questionnaire.objects.get(
                name="PDMP Check", can_originate_in_charting=True
            )

            # Get practitioner info and current date
            reviewed_by = self._get_practitioner_name(practitioner_id)
            current_date_timezone = self._get_current_date_timezone()

            # Create structured assessment command
            assessment = StructuredAssessmentCommand(
                note_uuid=str(note.id),
                questionnaire_id=str(questionnaire.id),
                command_uuid=str(uuid4()),
                result=f"Reviewed by: {reviewed_by}\nDate: {current_date_timezone}",
            )

            # Add responses to questions
            for question in assessment.questions:
                question_code = question.coding.get("code", "")

                if question_code == "STRUCTURED_ASSESSMENT_PDMP_001":  # "Reviewed by"
                    question.add_response(text=reviewed_by)
                elif question_code == "STRUCTURED_ASSESSMENT_PDMP_003":  # "Date"
                    question.add_response(text=current_date_timezone)

            # Generate and return effects
            return [assessment.originate(), assessment.edit(), assessment.commit()]

        except Exception as e:
            log.error(f"AssessmentEffectsService: Error creating structured assessment: {str(e)}")
            return []

    def _get_current_date_timezone(self) -> str:
        # Get current time in America/Chicago timezone
        now_cdt = arrow.utcnow().to("America/Chicago")

        # Format like "4/22/19 12:30 PM CDT"
        formatted_date = now_cdt.datetime.strftime("%-m/%-d/%y %-I:%M %p %Z")

        log.info(f"AssessmentEffectsService: Generated timezone date: {formatted_date}")
        return formatted_date

    def _get_practitioner_name(self, practitioner_id: str | None) -> str:
        """Get practitioner name for assessment."""
        if not practitioner_id:
            return "Unknown Practitioner"

        try:
            staff = Staff.objects.get(id=practitioner_id)
            first_name = staff.first_name or ""
            last_name = staff.last_name or ""
            name = f"{first_name} {last_name}".strip()
            log.info(f"AssessmentEffectsService: Practitioner name: {name}")
            return name if name else f"User {practitioner_id}"
        except Exception as e:
            log.error(f"AssessmentEffectsService: Error getting practitioner name: {str(e)}")
            return f"User {practitioner_id}"

    def create_assessment_status_result(
        self, assessment_effects: list[Effect], error: str | None = None
    ) -> dict[str, Any]:
        """
        Create assessment status result for inclusion in PDMP result.

        Args:
            assessment_effects: List of assessment effects created
            error: Error message if assessment creation failed

        Returns:
            Dictionary with assessment status information
        """
        if error:
            return {
                "assessment_created": False,
                "assessment_error": error,
                "assessment_effects_count": 0,
            }
        else:
            return {
                "assessment_created": len(assessment_effects) > 0,
                "assessment_error": None,
                "assessment_effects_count": len(assessment_effects),
            }
