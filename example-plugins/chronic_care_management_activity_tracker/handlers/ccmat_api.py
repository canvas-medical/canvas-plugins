import datetime
from http import HTTPStatus
from uuid import uuid4

import arrow
from django.db.models import Q

from canvas_sdk.commands.commands.questionnaire import QuestionnaireCommand
from canvas_sdk.effects import Effect
from canvas_sdk.effects.note import Note as NoteEffect
from canvas_sdk.effects.simple_api import HTMLResponse, JSONResponse, Response
from canvas_sdk.handlers.simple_api import api
from canvas_sdk.handlers.simple_api.api import SimpleAPI
from canvas_sdk.handlers.simple_api.security import (
    StaffSessionAuthMixin,
)
from canvas_sdk.templates.utils import render_to_string
from canvas_sdk.v1.data.appointment import Appointment
from canvas_sdk.v1.data.note import Note, NoteStates, NoteType, NoteTypeCategories
from canvas_sdk.v1.data.patient import Patient
from canvas_sdk.v1.data.questionnaire import Questionnaire
from canvas_sdk.v1.data.staff import Staff
from logger import log


class CcmatApi(StaffSessionAuthMixin, SimpleAPI):
    """API for the Chronic Care Management Activity Tracker application."""

    BASE_PATH = "/plugin-io/api/chronic_care_management_activity_tracker"

    NOTE_TYPE_CODE = "chronic_care_management_note"

    QUESTIONNAIRE_CODE = "ccm_session_questionnaire"

    ACTIVITIES = (
        ("Medication review", "medication_review"),
        ("Care plan update", "care_plan_update"),
        ("Provider coordination", "provider_coordination"),
        ("Patient or caregiver contact", "patient_or_caregiver_contact"),
        ("Symptom or condition monitoring", "symptom_or_condition_monitoring"),
        ("Referral or transition management", "referral_or_transition_management"),
        ("Other care management", "other_care_management"),
    )

    # Serve templated HTML
    @api.get("/<patient_id>/app")
    def index(self) -> list[Response | Effect]:
        """Serve the main dashboard page."""
        logged_in_staff = Staff.objects.get(id=self.request.headers["canvas-logged-in-user-id"])

        patient = self._get_patient()

        context = {
            "staff_name": logged_in_staff.full_name,
            "patient_name": patient.preferred_full_name if patient else "N/A",
            "current_date": arrow.utcnow().format("YYYY-MM-DD"),
            "activities": list(self.ACTIVITIES),
        }

        return [
            HTMLResponse(
                render_to_string("assets/index.html", context),
                status_code=HTTPStatus.OK,
            )
        ]

    # Serve the contents of a css file
    @api.get("/<patient_id>/styles.css")
    def get_css(self) -> list[Response | Effect]:
        """Serve the contents of a CSS file."""
        return [
            Response(
                render_to_string("assets/styles.css").encode(),
                status_code=HTTPStatus.OK,
                content_type="text/css",
            )
        ]

    # Serve the contents of a js file
    @api.get("/<patient_id>/scripts.js")
    def get_scripts(self) -> list[Response | Effect]:
        """Serve the contents of a JavaScript file."""
        return [
            Response(
                render_to_string("assets/scripts.js", {"patient_id": self._patient_id}).encode(),
                status_code=HTTPStatus.OK,
                content_type="application/javascript",
            )
        ]

    @api.post("/<patient_id>/sessions")
    def save_session(self) -> list[Response | Effect]:
        """Handle saving a session (stub implementation)."""
        try:
            staff = self._get_staff()
            patient = self._get_patient()
            note_id = str(uuid4())
            now = datetime.datetime.now()

            note = NoteEffect(
                instance_id=note_id,
                note_type_id=self._get_chronic_note_type_id(),
                datetime_of_service=now,
                patient_id=patient.id,
                provider_id=staff.id,
                practice_location_id=self._get_practice_location_id(patient, staff).id,
                title="Chronic Care Management Note",
            )

            questionnaire = self._get_questionnaire()
            questionnaire_command = QuestionnaireCommand(
                note_uuid=note_id,
                command_uuid=str(uuid4()),
                questionnaire_id=str(questionnaire.id),
            )

            json_data = self.request.json()

            activity_codes = list(json_data["activities"])
            activities = [
                desc for desc, code in self.ACTIVITIES if code.strip().lower() in activity_codes
            ]

            time_logs = list(json_data["timeLogs"])
            session_logs = []
            time_spent = 0
            for i in range(0, len(time_logs) - 1, 2):
                start = time_logs[i]['timestamp']
                end = time_logs[i + 1]['timestamp']
                session_logs.append(f"{start} - {end}")
                time_spent += (arrow.get(end) - arrow.get(start)).seconds

            total_time_minutes = time_spent // 60
            if total_time_minutes == 0 and time_spent > 0:
                total_time_minutes = 1  # Round up to 1 minute if less than a minute but more than 0 seconds

            total_time = f"{str(total_time_minutes)} minute{'' if total_time_minutes == 1 else 's'}"
            if total_time_minutes > time_spent % 60:
                total_time += f" and {str(time_spent % 60)} seconds"

            notes = str(json_data["notes"]).strip()

            total_month_minutes = self._get_previous_month_minutes(patient) + total_time_minutes

            # Convert totalTime from seconds to minutes (rounded to nearest integer)

            for question in questionnaire_command.questions:
                if question.coding.get("code") == "ccm_session_pt_name_question":
                    question.add_response(text=patient.preferred_full_name)
                elif question.coding.get("code") == "ccm_session_staff_name_question":
                    question.add_response(text=staff.full_name)
                elif question.coding.get("code") == "ccm_session_date_question":
                    question.add_response(text=now.strftime("%Y-%m-%d"))
                elif question.coding.get("code") == "ccm_session_activities_question":
                    question.add_response(text=", ".join(activities))
                elif question.coding.get("code") == "ccm_session_notes_question":
                    question.add_response(text=notes)
                elif question.coding.get("code") == "ccm_session_time_log_question":
                    question.add_response(text=", ".join(session_logs))
                elif question.coding.get("code") == "ccm_session_duration_question":
                    question.add_response(text=total_time)
                elif question.coding.get("code") == "ccm_month_minutes_question":
                    question.add_response(text=f"{total_month_minutes} minute{'' if total_month_minutes == 1 else 's'}")

            return [
                JSONResponse(
                    {
                        "message": f"Creating Chronic Care Management Note for {patient.id}.",
                        "note_id": note_id,
                    },
                    status_code=HTTPStatus.OK,
                ),
                note.create(),
                questionnaire_command.originate(),
                questionnaire_command.edit(),
                questionnaire_command.commit(),
            ]
        except Patient.DoesNotExist:
            log.error("Patient does not exist.")
            return [
                JSONResponse(
                    {"error": "Patient does not exist."}, status_code=HTTPStatus.BAD_REQUEST
                )
            ]
        except Exception as e:
            log.error(f"Error saving session: {e}")
            return [
                JSONResponse(
                    {"error": "Failed to save session."},
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                )
            ]

    @property
    def _patient_id(self):
        return self.request.path_params["patient_id"]

    def _get_staff(self) -> Staff:
        return Staff.objects.get(id=self.request.headers["canvas-logged-in-user-id"])

    def _get_patient(self) -> Patient:
        log.info(f"Fetching patient with ID: {self._patient_id}")
        return Patient.objects.get(id=self._patient_id)

    def _get_chronic_note_type_id(self) -> str:
        return NoteType.objects.get(code=self.NOTE_TYPE_CODE).id

    def _get_last_visit(self, patient: Patient) -> Note | None:
        return (
            Note.objects.filter(
                patient=patient,
                note_type_version__category=NoteTypeCategories.ENCOUNTER,
            )
            .exclude(
                Q(current_state__state=NoteStates.DELETED)
                | Q(current_state__state=NoteStates.CANCELLED)
            )
            .order_by("-datetime_of_service")
            .first()
        )

    def _get_patient_most_recent_practice_location(self, patient: Patient, staff: Staff) -> str:
        last_visit = self._get_last_visit(patient)
        if last_visit:
            return last_visit.place_of_service.id
        return staff.primary_practice_location.id

    def _get_practice_location_id(self, patient: Patient, staff: Staff):
        appointment = (
            Appointment.objects.filter(
                patient=patient,
                provider=staff,
            )
            .order_by("-start_time")
            .first()
        )

        if appointment and appointment.location:
            return appointment.location
        return staff.primary_practice_location

    def _get_questionnaire(self) -> Questionnaire:
        return Questionnaire.objects.get(code=self.QUESTIONNAIRE_CODE)

    def _get_previous_month_minutes(self, patient: Patient) -> int:
        questionnaire = self._get_questionnaire()
        last_month = arrow.utcnow().shift(months=-1).month
        last_month_responses = (
            patient.interviews.filter(questionnaires=questionnaire)
            .filter(created__month=last_month)
            .order_by("-created")
        )

        if not last_month_responses.exists():
            return 0

        total_minutes = 0
        for interview in last_month_responses:
            for response in interview.interview_responses.filter(
                question__code="ccm_month_minutes_question"
            ):
                if response.response_option_value.isdigit():
                    total_minutes += int(response.response_option_value)

        return total_minutes
