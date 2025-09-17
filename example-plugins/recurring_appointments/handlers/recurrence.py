import datetime
from dateutil.relativedelta import relativedelta

from canvas_sdk.effects.note import ScheduleEvent
from canvas_sdk.events import EventType
from canvas_sdk.effects.note.appointment import Appointment
from canvas_sdk.v1.data import Appointment as AppointmentModel, AppointmentMetadata
from canvas_sdk.handlers.base import BaseHandler
from canvas_sdk.v1.data.note import NoteTypeCategories
from recurring_appointments.utils.constants import RecurrenceEnum, FIELD_RECURRENCE_KEY
from logger import log




class AppointmentRecurrence(BaseHandler):

    # Name the event type you wish to run in response to
    RESPONDS_TO = EventType.Name(EventType.APPOINTMENT_CREATED)

    def _get_recurrence_from_appointment_metadata(self, appointment: AppointmentModel) -> RecurrenceEnum:
        """Determine the recurrence type from the appointment metadata."""

        recurrence = AppointmentMetadata.objects.filter(
            appointment=appointment, key="recurrence"
        ).values_list("value", flat=True).first()

        return recurrence or RecurrenceEnum.NONE.value

    def _calculate_recurrence_date(self, start_time: datetime.datetime, count: int, recurrence: RecurrenceEnum) -> datetime.datetime:
        """Calculate the new date based on recurrence type and count."""
        if recurrence == RecurrenceEnum.DAILY.value:
            return start_time + datetime.timedelta(days=count)
        elif recurrence == RecurrenceEnum.WEEKLY.value:
            return start_time + datetime.timedelta(weeks=count)
        elif recurrence == RecurrenceEnum.MONTHLY.value:
            return start_time + relativedelta(months=count)
        else:
            return start_time

    def _create_child_appointment(self, appointment: AppointmentModel, count: int, recurrence: RecurrenceEnum) -> Appointment:
        new_start_time = self._calculate_recurrence_date(appointment.start_time, count, recurrence)

        return Appointment(
            patient_id=self.event.context["patient"]["id"],
            parent_appointment_id=appointment.id,
            start_time=new_start_time,
            duration_minutes=appointment.duration_minutes,
            provider_id=appointment.provider.id,
            practice_location_id=appointment.location.id,
            meeting_link=appointment.meeting_link,
            appointment_note_type_id=appointment.note_type.id
        )

    def _create_child_event(self, appointment: AppointmentModel, count: int, recurrence: RecurrenceEnum) -> ScheduleEvent:
        new_start_time = self._calculate_recurrence_date(appointment.start_time, count, recurrence)

        return ScheduleEvent(
            patient_id=self.event.context.get("patient", {}).get("id"),
            parent_appointment_id=appointment.id,
            description=appointment.description,
            start_time=new_start_time,
            duration_minutes=appointment.duration_minutes,
            practice_location_id=appointment.location.id,
            provider_id=appointment.provider.id,
            note_type_id=appointment.note_type.id,
        )


    def compute(self):
        parent_appointment: AppointmentModel = AppointmentModel.objects.get(id=self.event.target.id)

        recurrence = self._get_recurrence_from_appointment_metadata(parent_appointment)
        log.info(f"####################### recurrence {recurrence}")
        if not recurrence:
            return []

        # appointment or schedule event
        is_schedule_event = parent_appointment.note_type.category == NoteTypeCategories.SCHEDULE_EVENT

        effects = []
        if recurrence == RecurrenceEnum.WEEKLY.value:
            # create some weekly appointments for the next 2 months - 8 weeks
            for i in range(1, 9):
                effect: Appointment | ScheduleEvent =  self._create_child_event(parent_appointment, i, recurrence) if is_schedule_event else self._create_child_appointment(parent_appointment, i, recurrence)
                effects.append(effect.create())

        if recurrence == RecurrenceEnum.DAILY.value:
            # create some daily appointments for the next 2 months - 60days
            for i in range(1, 61):
                effect: Appointment | ScheduleEvent =  self._create_child_event(parent_appointment, i, recurrence) if is_schedule_event else self._create_child_appointment(parent_appointment, i, recurrence)
                effects.append(effect.create())

        if recurrence == RecurrenceEnum.MONTHLY.value:
            # create some daily appointments for the next 2 months - 2
            for i in range(1, 3):
                effect: Appointment | ScheduleEvent =  self._create_child_event(parent_appointment, i, recurrence) if is_schedule_event else self._create_child_appointment(parent_appointment, i, recurrence)
                effects.append(effect.create())

        return effects
