import arrow

from canvas_sdk.effects.patient_portal.form_result import FormResult
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler
from canvas_sdk.v1.data import Interview, Patient, Questionnaire
from canvas_sdk.v1.data.appointment import AppointmentProgressStatus
from logger import log

# 1
INTAKE_QUESTIONNAIRES = [
  "Insurance Details",
  "Preferred Pharmacy Details",
  "Social History",
]

class RefillFormHandler(BaseHandler):
  """Protocol for processing Patient Portal form requests and generating form effects."""

  RESPONDS_TO = EventType.Name(EventType.PATIENT_PORTAL__GET_FORMS)

  def _get_upcoming_appointment_note_id(self, appointments, note_type_names):
    """Retrieve the note_id for the first confirmed future appointment matching given note type names."""
    now = arrow.now().date()
    return appointments.filter(
      status=AppointmentProgressStatus.CONFIRMED,
      start_time__gt=now,
      note_type__name__in=note_type_names
    ).values_list("note__id", flat=True).first()

  def compute(self):
    """Compute and return a list of FormResult effects based on upcoming appointments."""


    # 2
    patient_id = self.target
    # medications = medication.Medication.objects.filter(patient__id=patient_id, status=medication.Status.ACTIVE)

    completed_forms = set(
    #   Interview.objects.filter(
    #     patient=patient,
    #     entered_in_error_id__isnull=True,
    #     questionnaires__name__in=INTAKE_QUESTIONNAIRES
    #   ).values_list("questionnaires__name", flat=True)
    )

    forms = []

    # Assign Intake Forms for new patients
    # if note_id := self._get_upcoming_appointment_note_id(patient_appointments, ["Telehealth", "Office visit"]):
    #   missing_intake_forms = [qname for qname in INTAKE_QUESTIONNAIRES if qname not in completed_forms]
    #   missing_intake_questionnaire_ids = Questionnaire.objects.filter(name__in=missing_intake_forms).values_list("id",
    #                                                                                                              flat=True)


    #   #3
    #   forms = [
    #     FormResult(questionnaire_id=qid, create_command=True, note_id=note_id).apply()
    #     for qid in missing_intake_questionnaire_ids
    #   ]

    log.info(f"Computed forms for patient {patient_id}: {forms}")

    return forms
