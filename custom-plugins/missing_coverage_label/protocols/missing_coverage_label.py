from canvas_sdk.effects import Effect
from canvas_sdk.effects.note import RemoveAppointmentLabel
from canvas_sdk.effects.note.appointment import AddAppointmentLabel
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from canvas_sdk.v1.data import Appointment, Patient, Coverage
from logger import log


class AppointmentLabelsProtocol(BaseProtocol):
    """
    Manages the 'MISSING_COVERAGE' label on patient appointments.

    This protocol has two main functions:
    1.  On APPOINTMENT_CREATED: If the patient associated with the new
        appointment does not have any coverage, this protocol will add the
        'MISSING_COVERAGE' label to all of that patient's appointments
        that do not already have it.
    2.  On COVERAGE_CREATED: When coverage is added for a patient, this
        protocol finds all of that patient's appointments that have the
        'MISSING_COVERAGE' label and removes it.
    """

    RESPONDS_TO = [
        EventType.Name(EventType.COVERAGE_CREATED),
        EventType.Name(EventType.APPOINTMENT_CREATED),
    ]

    def handle_coverage_created(self) -> list[Effect]:
        """
        When coverage is added, find all appointments for the patient
        that have the 'MISSING_COVERAGE' label and create effects to remove it.
        """
        patient_id = self.context["patient"]["id"]
        log.info(f"Handling COVERAGE_CREATED for patient {patient_id}")

        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            log.warning(f"Patient with ID {patient_id} not found.")
            return []

        appointments_to_update = Appointment.objects.filter(
            patient = patient, appointment_labels__name = "MISSING_COVERAGE"
        ).prefetch_related("appointment_labels")

        if not appointments_to_update.exists():
            log.info(
                f"No appointments with 'MISSING_COVERAGE' label found for patient {patient_id}."
            )
            return []

        log.info(
            f"Found {len(appointments_to_update)} appointments to update for patient {patient_id}."
        )

        effects = []
        for appt in appointments_to_update:
            log.info(f"Creating RemoveAppointmentLabel effect for appointment {appt.id}")
            try:
                remove_label_effect = RemoveAppointmentLabel(
                    appointment_id=str(appt.id),
                    labels=["MISSING_COVERAGE"],
                ).apply()
                effects.append(remove_label_effect)
            except Exception as e:
                log.error(
                    f"Failed to create RemoveAppointmentLabel effect for appointment {appt.id}: {e}",
                    exc_info=True,
                )

        return effects

    def handle_appointment_created(self) -> list[Effect]:
        """
        When an appointment is created, adds the 'MISSING_COVERAGE' label if the
        patient has no coverage.
        """
        patient_id = self.context["patient"]["id"]
        log.info(f"Handling APPOINTMENT_CREATED for patient {patient_id}")

        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            log.warning(f"Patient with ID {patient_id} not found.")
            return []

        has_coverage = Coverage.objects.filter(patient=patient).exists()

        if has_coverage:
            log.info(f"Patient {patient_id} has coverage. No action needed.")
            return []

        log.info(f"Patient {patient_id} has no coverage. Checking appointments for labeling.")

        # Note: This logic will apply the label to ALL of the patient's
        # appointments that do not currently have it, not just the newly
        # created one.
        appointments_to_label = (
            Appointment.objects.filter(patient=patient)
            .exclude(appointment_labels__name="MISSING_COVERAGE")
            .prefetch_related("appointment_labels")
        )

        if not appointments_to_label.exists():
            log.info(
                f"No appointments needing 'MISSING_COVERAGE' label for patient {patient_id}."
            )
            return []

        log.info(
            f"Found {len(appointments_to_label)} appointments to label for patient {patient_id}."
        )

        effects = []
        for appt in appointments_to_label:
            log.info(f"Creating AddAppointmentLabel effect for appointment {appt.id}")
            try:
                add_label_effect = AddAppointmentLabel(
                    appointment_id=str(appt.id),
                    labels=["MISSING_COVERAGE"],
                ).apply()
                effects.append(add_label_effect)
            except Exception as e:
                log.error(
                    f"Failed to create AddAppointmentLabel effect for appointment {appt.id}: {e}",
                    exc_info=True,
                )
        return effects

    def compute(self) -> list[Effect]:
        """Routes the event to the appropriate handler."""
        if self.event.type == EventType.APPOINTMENT_CREATED:
            return self.handle_appointment_created()  # Add Labels
        elif self.event.type == EventType.COVERAGE_CREATED:
            return self.handle_coverage_created()  # Remove Labels

        return []
