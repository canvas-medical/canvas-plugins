import datetime

from dateutil.relativedelta import relativedelta

from canvas_sdk.effects.base import Effect
from canvas_sdk.effects.note import ScheduleEvent
from canvas_sdk.effects.note.appointment import Appointment
from canvas_sdk.events import EventType
from canvas_sdk.handlers.base import BaseHandler
from canvas_sdk.v1.data import Appointment as AppointmentModel
from canvas_sdk.v1.data import AppointmentMetadata
from canvas_sdk.v1.data.note import NoteTypeCategories
from recurring_appointments.utils.constants import (
    FIELD_RECURRENCE_INTERVAL_KEY,
    FIELD_RECURRENCE_STOP_AFTER_KEY,
    FIELD_RECURRENCE_TYPE_KEY,
    RecurrenceEnum,
)


class AppointmentRecurrence(BaseHandler):
    """Handler for creating recurring appointments based on appointment metadata."""

    _appointment: AppointmentModel | None = None
    _recurrence_type: str | None = None
    _recurrence_interval: int | None = None
    _recurrence_stops_after: int | None = None

    # Name the event type you wish to run in response to
    RESPONDS_TO = EventType.Name(EventType.APPOINTMENT_CREATED)

    @property
    def appointment(self) -> AppointmentModel:
        """Get the appointment from the event."""
        if self._appointment is None:
            self._appointment = AppointmentModel.objects.get(id=self.event.target.id)

        return self._appointment

    @property
    def recurrence_type(self) -> str:
        """Determine the recurrence type from the appointment metadata."""
        if self._recurrence_type is None:
            self._recurrence_type = (
                AppointmentMetadata.objects.filter(
                    appointment=self.appointment, key=FIELD_RECURRENCE_TYPE_KEY
                )
                .values_list("value", flat=True)
                .first()
                or RecurrenceEnum.NONE.value
            )

        return self._recurrence_type

    @property
    def recurrence_interval(self) -> int:
        """Determine the recurrence interval from the appointment metadata."""
        if self._recurrence_interval is None:
            try:
                self._recurrence_interval = int(
                    AppointmentMetadata.objects.filter(
                        appointment=self.appointment, key=FIELD_RECURRENCE_INTERVAL_KEY
                    )
                    .values_list("value", flat=True)
                    .first()
                )
            except Exception:
                self._recurrence_interval = 1

        return self._recurrence_interval

    @property
    def recurrence_stops_after(self) -> int:
        """Determine when recurrence should stop from the appointment metadata."""
        if self._recurrence_stops_after is None:
            try:
                self._recurrence_stops_after = int(
                    AppointmentMetadata.objects.filter(
                        appointment=self.appointment, key=FIELD_RECURRENCE_STOP_AFTER_KEY
                    )
                    .values_list("value", flat=True)
                    .first()
                )
            except Exception:
                self._recurrence_stops_after = 30

        return self._recurrence_stops_after

    def _calculate_recurrence_date(self, count: int) -> datetime.datetime:
        """Calculate the new date based on a recurrence type, count, and interval."""
        start_time = self.appointment.start_time
        if self.recurrence_type == RecurrenceEnum.DAYS.value:
            return start_time + datetime.timedelta(days=count * self.recurrence_interval)
        elif self.recurrence_type == RecurrenceEnum.WEEKS.value:
            return start_time + datetime.timedelta(weeks=count * self.recurrence_interval)
        elif self.recurrence_type == RecurrenceEnum.MONTHS.value:
            return start_time + relativedelta(months=count * self.recurrence_interval)
        else:
            return start_time

    def _create_child_appointment(self, count: int) -> Appointment:
        """Create a child appointment based on the appointment and recurrence type."""
        new_start_time = self._calculate_recurrence_date(count)

        return Appointment(
            patient_id=self.event.context["patient"]["id"],
            parent_appointment_id=self.appointment.id,
            start_time=new_start_time,
            duration_minutes=self.appointment.duration_minutes,
            provider_id=self.appointment.provider.id,
            practice_location_id=self.appointment.location.id,
            meeting_link=self.appointment.meeting_link,
            appointment_note_type_id=self.appointment.note_type.id,
        )

    def _create_child_event(self, count: int) -> ScheduleEvent:
        """Create a child schedule event based on the appointment and recurrence type."""
        new_start_time = self._calculate_recurrence_date(count)

        return ScheduleEvent(
            patient_id=self.event.context.get("patient", {}).get("id"),
            parent_appointment_id=self.appointment.id,
            description=self.appointment.description,
            start_time=new_start_time,
            duration_minutes=self.appointment.duration_minutes,
            practice_location_id=self.appointment.location.id,
            provider_id=self.appointment.provider.id,
            note_type_id=self.appointment.note_type.id,
        )

    def compute(self) -> list[Effect]:
        """Create recurring appointments based on recurrence configuration."""
        if not self.recurrence_type or self.recurrence_type == RecurrenceEnum.NONE.value:
            return []

        # appointment or schedule event
        is_schedule_event = self.appointment.note_type.category == NoteTypeCategories.SCHEDULE_EVENT
        effects = []

        # Create recurring appointments/events
        for count in range(1, self.recurrence_stops_after + 1):
            if is_schedule_event:
                effect = self._create_child_event(count)
            else:
                effect = self._create_child_appointment(count)
            effects.append(effect.create())

        return effects
