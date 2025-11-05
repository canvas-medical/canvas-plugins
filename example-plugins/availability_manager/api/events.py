import arrow
from canvas_sdk.effects.calendar import CreateEvent, UpdateEvent, DeleteEvent, EventRecurrence, DaysOfWeek
from canvas_sdk.effects.simple_api import Response
from canvas_sdk.handlers.simple_api import SimpleAPIRoute, StaffSessionAuthMixin
from canvas_sdk.effects import Effect


class CalendarEventsAPI(StaffSessionAuthMixin, SimpleAPIRoute):
    PATH = "/events"

    def get(self) -> list[Response | Effect]:
        return []

    def post(self) -> list[Response | Effect]:
        body = self.request.json()

        calender_id = body.get("calendar")
        title = body.get("title")
        starts_at = arrow.get(body.get("startTime")).datetime
        ends_at = arrow.get(body.get("endTime")).datetime
        recurrence_frequency = body.get("recurrenceFrequency")
        recurrence_interval = body.get("recurrenceInterval")
        recurrence_days = body.get("recurrenceDays")
        recurrence_ends_at = arrow.get(body.get("recurrenceEndsAt")).datetime if body.get("recurrenceEndsAt") else None
        allowed_note_types = body.get("allowedNoteTypes", [])

        create_calendar_event = CreateEvent(
            calendar_id=calender_id,
            title=title,
            starts_at=starts_at,
            ends_at=ends_at,
            recurrence_frequency=EventRecurrence(recurrence_frequency) if recurrence_frequency else None,
            recurrence_interval=int(recurrence_interval) if recurrence_interval is not None else None,
            recurrence_days=[DaysOfWeek(day) for day in recurrence_days] if recurrence_days else None,
            recurrence_ends_at=recurrence_ends_at,
            allowed_note_types=allowed_note_types,
        )

        return [create_calendar_event.apply(), Response(status_code=201)]

    def patch(self) -> list[Response | Effect]:
        body = self.request.json()

        event_id = body.get("eventId")
        title = body.get("title")
        starts_at = arrow.get(body.get("startTime")).datetime
        ends_at = arrow.get(body.get("endTime")).datetime
        recurrence_frequency = body.get("recurrenceFrequency")
        recurrence_interval = body.get("recurrenceInterval")
        recurrence_days = body.get("recurrenceDays")
        recurrence_ends_at = arrow.get(body.get("recurrenceEndsAt")).datetime if body.get("recurrenceEndsAt") else None
        allowed_note_types = body.get("allowedNoteTypes", [])

        update_calendar_event = UpdateEvent(
            event_id=event_id,
            title=title,
            starts_at=starts_at,
            ends_at=ends_at,
            recurrence_frequency=EventRecurrence(recurrence_frequency) if recurrence_frequency else None,
            recurrence_interval=int(recurrence_interval) if recurrence_interval is not None else None,
            recurrence_days=[DaysOfWeek(day) for day in recurrence_days] if recurrence_days else None,
            recurrence_ends_at=recurrence_ends_at,
            allowed_note_types=allowed_note_types,
        )

        return [update_calendar_event.apply(), Response(status_code=200)]

    def delete(self) -> list[Response | Effect]:
        body = self.request.json()

        event_id = body.get("eventId")

        delete_calendar_event = DeleteEvent(event_id=event_id)

        return [delete_calendar_event.apply(), Response(status_code=200)]