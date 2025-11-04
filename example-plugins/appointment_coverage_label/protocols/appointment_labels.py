from canvas_sdk.effects import Effect
from canvas_sdk.effects.note import RemoveAppointmentLabel
from canvas_sdk.effects.note.appointment import AddAppointmentLabel
from canvas_sdk.events import EventType
from canvas_sdk.protocols import BaseProtocol
from canvas_sdk.v1.data import Appointment, Coverage, Patient
from logger import log


class AppointmentLabelsProtocol(BaseProtocol):
    """
    Manages the 'MISSING_COVERAGE' label on patient appointments based on insurance coverage status.

    This protocol automatically:
    1. Adds 'MISSING_COVERAGE' labels to all appointments for patients without insurance coverage
    2. Removes 'MISSING_COVERAGE' labels from all appointments when insurance coverage is added

    The protocol responds to two events:
    - APPOINTMENT_CREATED: Checks if the patient has coverage and adds labels if needed
    - COVERAGE_CREATED: Removes labels from all appointments when coverage is added

    This ensures appointments are consistently flagged for insurance verification across
    the patient's entire appointment history.
    """

    RESPONDS_TO = [
        EventType.Name(EventType.COVERAGE_CREATED),
        EventType.Name(EventType.APPOINTMENT_CREATED),
    ]

    def handle_coverage_created(self) -> list[Effect]:
        """
        Handle COVERAGE_CREATED event by removing 'MISSING_COVERAGE' labels.

        When coverage is added for a patient, this method:
        1. Retrieves all appointments for the patient that have the 'MISSING_COVERAGE' label
        2. Creates RemoveAppointmentLabel effects for each labeled appointment
        3. Returns the list of effects to be applied

        Returns:
            list[Effect]: List of RemoveAppointmentLabel effects, or empty list if no action needed
        """
        patient_id = self.context["patient"]["id"]
        log.info(f"Handling COVERAGE_CREATED event for patient {patient_id}")

        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            log.warning(f"Patient with ID {patient_id} not found during COVERAGE_CREATED event.")
            return []

        # Find all appointments with the MISSING_COVERAGE label
        appointments_to_update = Appointment.objects.filter(
            patient=patient, labels__name="MISSING_COVERAGE"
        ).prefetch_related("labels")

        if not appointments_to_update.exists():
            log.info(
                f"No appointments with 'MISSING_COVERAGE' label found for patient {patient_id}. "
                "No labels to remove."
            )
            return []

        log.info(
            f"Found {len(appointments_to_update)} appointment(s) with 'MISSING_COVERAGE' label "
            f"for patient {patient_id}. Removing labels."
        )

        effects = []
        for appt in appointments_to_update:
            log.info(
                f"Creating RemoveAppointmentLabel effect for appointment {appt.id} "
                f"(patient {patient_id})"
            )
            try:
                remove_label_effect = RemoveAppointmentLabel(
                    appointment_id=str(appt.id),
                    labels={"MISSING_COVERAGE"},
                ).apply()
                effects.append(remove_label_effect)
            except Exception as e:
                log.error(
                    f"Failed to create RemoveAppointmentLabel effect for appointment {appt.id}: {e}",
                    exc_info=True
                )

        log.info(
            f"Completed COVERAGE_CREATED processing for patient {patient_id}. "
            f"Generated {len(effects)} effect(s)."
        )
        return effects

    def handle_appointment_created(self) -> list[Effect]:
        """
        Handle APPOINTMENT_CREATED event by adding 'MISSING_COVERAGE' labels if needed.

        When an appointment is created, this method:
        1. Checks if the patient has any insurance coverage
        2. If no coverage exists, finds all appointments without the 'MISSING_COVERAGE' label
        3. Creates AddAppointmentLabel effects for each unlabeled appointment
        4. Returns the list of effects to be applied

        Note: This method labels ALL appointments for the patient, not just the newly created one,
        to ensure consistency across the patient's appointment history.

        Returns:
            list[Effect]: List of AddAppointmentLabel effects, or empty list if no action needed
        """
        patient_id = self.context["patient"]["id"]
        log.info(f"Handling APPOINTMENT_CREATED event for patient {patient_id}")

        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            log.warning(f"Patient with ID {patient_id} not found during APPOINTMENT_CREATED event.")
            return []

        # Check if patient has any insurance coverage
        has_coverage = Coverage.objects.filter(patient=patient).exists()

        if has_coverage:
            log.info(
                f"Patient {patient_id} has insurance coverage. "
                "No 'MISSING_COVERAGE' label needed."
            )
            return []

        log.info(
            f"Patient {patient_id} has no insurance coverage. "
            "Checking appointments for 'MISSING_COVERAGE' label."
        )

        # Find all appointments that don't already have the MISSING_COVERAGE label
        # Note: This ensures ALL of the patient's appointments are labeled consistently,
        # not just the newly created appointment
        appointments_to_label = (
            Appointment.objects.filter(patient=patient)
            .exclude(labels__name="MISSING_COVERAGE")
            .prefetch_related("labels")
        )

        if not appointments_to_label.exists():
            log.info(
                f"All appointments for patient {patient_id} already have 'MISSING_COVERAGE' label. "
                "No new labels to add."
            )
            return []

        log.info(
            f"Found {len(appointments_to_label)} appointment(s) needing 'MISSING_COVERAGE' label "
            f"for patient {patient_id}. Adding labels."
        )

        effects = []
        for appt in appointments_to_label:
            log.info(
                f"Creating AddAppointmentLabel effect for appointment {appt.id} "
                f"(patient {patient_id})"
            )
            try:
                add_label_effect = AddAppointmentLabel(
                    appointment_id=str(appt.id),
                    labels={"MISSING_COVERAGE"},
                ).apply()
                effects.append(add_label_effect)
            except Exception as e:
                log.error(
                    f"Failed to create AddAppointmentLabel effect for appointment {appt.id}: {e}",
                    exc_info=True
                )

        log.info(
            f"Completed APPOINTMENT_CREATED processing for patient {patient_id}. "
            f"Generated {len(effects)} effect(s)."
        )
        return effects

    def compute(self) -> list[Effect]:
        """
        Route events to the appropriate handler based on event type.

        This method is called by the Canvas SDK when any of the RESPONDS_TO events are fired.
        It examines the event type and delegates to the appropriate handler method.

        Returns:
            list[Effect]: List of effects from the appropriate handler, or empty list if
                         event type is not recognized
        """
        log.info(
            f"AppointmentLabelsProtocol.compute() called for event type: {self.event.type}"
        )

        if self.event.type == EventType.APPOINTMENT_CREATED:
            return self.handle_appointment_created()
        elif self.event.type == EventType.COVERAGE_CREATED:
            return self.handle_coverage_created()

        log.warning(
            f"Received unexpected event type '{self.event.type}' in AppointmentLabelsProtocol. "
            "No handler available."
        )
        return []

