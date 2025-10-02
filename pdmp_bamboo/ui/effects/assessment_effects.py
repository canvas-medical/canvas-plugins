"""
Assessment Effects Service

Handles creation of structured assessment effects for PDMP requests.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import uuid4
from canvas_sdk.effects import Effect
from canvas_sdk.v1.data.note import Note
from canvas_sdk.v1.data.questionnaire import Questionnaire
from canvas_sdk.v1.data.staff import Staff
from canvas_sdk.commands import StructuredAssessmentCommand
from logger import log


class AssessmentEffectsService:
    """Service for creating structured assessment effects."""
    
    def create_assessment_effects(self, 
                                 patient_id: Optional[str],
                                 practitioner_id: Optional[str],
                                 result: Dict[str, Any]) -> List[Effect]:
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
            assessment_effects = self._create_pdmp_assessment(
                patient_id, practitioner_id, note_id
            )
            
            log.info(f"AssessmentEffectsService: Created {len(assessment_effects)} assessment effects")
            return assessment_effects
            
        except Exception as e:
            log.error(f"AssessmentEffectsService: Error creating assessment effects: {str(e)}")
            return []
    
    def _should_create_assessment(self, result: Dict[str, Any]) -> bool:
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

    def _create_pdmp_assessment(self,
                                patient_id: Optional[str],
                                practitioner_id: Optional[str],
                                note_id: str) -> List[Effect]:
        """Create structured assessment to document PDMP check."""
        log.info("AssessmentEffectsService: Creating structured assessment for PDMP check")

        try:
            # Get the note
            note = Note.objects.get(dbid=note_id)
            log.info(f"AssessmentEffectsService: Retrieved note UUID={note.id}")

            # Get the questionnaire
            questionnaire = Questionnaire.objects.get(
                name="PDMP Check",
                can_originate_in_charting=True
            )
            log.info(f"AssessmentEffectsService: Found questionnaire: ID={questionnaire.id}")

            # Get practitioner info for "checked by" field
            reviewed_by = self._get_practitioner_name(practitioner_id)
            current_date = datetime.now().strftime("%Y-%m-%d")

            log.info(f"AssessmentEffectsService: Assessment data:")
            log.info(f"  - Note UUID: {note.id}")
            log.info(f"  - Questionnaire ID: {questionnaire.id}")
            log.info(f"  - Practitioner: {reviewed_by}")
            log.info(f"  - Date: {current_date}")

            # Create structured assessment command
            assessment = StructuredAssessmentCommand(
                note_uuid=str(note.id),
                questionnaire_id=str(questionnaire.id),
                command_uuid=str(uuid4()),
            )
            log.info(f"AssessmentEffectsService: Created StructuredAssessmentCommand UUID={assessment.command_uuid}")

            # Populate responses
            log.info(f"AssessmentEffectsService: Found {len(assessment.questions)} questions in assessment")
            for i, question in enumerate(assessment.questions):
                log.info(
                    f"AssessmentEffectsService: Question {i + 1}: label='{question.label}', name='{question.name}'")
                try:
                    if "PDMP checked by" in question.label:
                        question.add_response(text=reviewed_by)
                        log.info(f"AssessmentEffectsService: Set 'PDMP checked by' = {reviewed_by}")
                    elif "Date checked" in question.label:
                        question.add_response(text=current_date)
                        log.info(f"AssessmentEffectsService: Set 'Date checked' = {current_date}")
                    else:
                        log.warning(f"AssessmentEffectsService: No match for question label: '{question.label}'")
                except Exception as e:
                    log.error(f"AssessmentEffectsService: Error setting response for '{question.label}': {e}")

            # Generate effects to finalize the assessment
            log.info("AssessmentEffectsService: Generating assessment effects...")
            originate_effect = assessment.originate()
            log.info(f"AssessmentEffectsService: Originate effect: {originate_effect}")
            edit_effect = assessment.edit()
            log.info(f"AssessmentEffectsService: Edit effect: {edit_effect}")
            commit_effect = assessment.commit()
            log.info(f"AssessmentEffectsService: Commit effect: {commit_effect}")

            effects = [originate_effect, edit_effect, commit_effect]

            log.info("AssessmentEffectsService: Generated structured assessment effects")
            # log.info(f"AssessmentEffectsService: Effect types: {[type(effect).__name__ for effect in effects]}")
            log.info(f"AssessmentEffectsService: Effect details:")
            for i, effect in enumerate(effects):
                # log.info(f"  Effect {i + 1}: {type(effect).__name__}")
                if hasattr(effect, 'command_uuid'):
                    log.info(f"    Command UUID: {effect.command_uuid}")
                if hasattr(effect, 'note_uuid'):
                    log.info(f"    Note UUID: {effect.note_uuid}")
                if hasattr(effect, 'questionnaire_id'):
                    log.info(f"    Questionnaire ID: {effect.questionnaire_id}")

            return effects

        except Note.DoesNotExist:
            log.error(f"AssessmentEffectsService: Note not found (dbid={note_id})")
            return []
        except Questionnaire.DoesNotExist:
            log.error("AssessmentEffectsService: PDMP Check questionnaire not found")
            return []
        except Exception as e:
            log.error(f"AssessmentEffectsService: Error creating structured assessment: {str(e)}")
            import traceback
            log.error(f"AssessmentEffectsService: Traceback: {traceback.format_exc()}")
            return []
    
    def _get_practitioner_name(self, practitioner_id: Optional[str]) -> str:
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
    
    def create_assessment_status_result(self, 
                                      assessment_effects: List[Effect],
                                      error: Optional[str] = None) -> Dict[str, Any]:
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
                "assessment_effects_count": 0
            }
        else:
            return {
                "assessment_created": len(assessment_effects) > 0,
                "assessment_error": None,
                "assessment_effects_count": len(assessment_effects)
            }

