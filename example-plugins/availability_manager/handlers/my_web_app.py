from http import HTTPStatus

from canvas_sdk.effects import Effect
from canvas_sdk.effects.calendar import CalendarType, EventRecurrence
from canvas_sdk.effects.simple_api import HTMLResponse, Response
from canvas_sdk.handlers.simple_api import SimpleAPI, api, StaffSessionAuthMixin
from canvas_sdk.templates import render_to_string
from canvas_sdk.v1.data import PracticeLocation, NoteType
from canvas_sdk.v1.data.calendar import Event
from canvas_sdk.v1.data.staff import Staff


class MyWebApp(StaffSessionAuthMixin, SimpleAPI):
    PREFIX = "/app"

    # Serve templated HTML
    @api.get("/availability-app")
    def index(self) -> list[Response | Effect]:
        # logged_in_user = Staff.objects.get(id=self.request.headers["canvas-logged-in-user-id"])

        providers = Staff.objects.filter(active=True)
        locations = PracticeLocation.objects.filter(active=True)
        note_types = NoteType.objects.filter(is_active=True, is_scheduleable=True)
        events = Event.objects.all()

        # for event in events:
        #     log.info("Event --------------------")
        #     log.info(event.id)
        #     log.info(event.title)
        #     log.info(event.calendar.title)
        #     log.info(event.starts_at)
        #     log.info(event.ends_at)
        #     log.info(event.recurrence)
        #     log.info(event.recurrence_ends_at)
        #     log.info(event.allowed_note_types)

        context = {
            "providers": [{"id": provider.id, "name": provider.credentialed_name, "full_name": provider.full_name} for provider in providers],
            "locations": [{"id": str(location.id), "name": location.full_name, "address": ""} for location in
                          locations],
            "noteTypes": [{"id": str(note_type.id), "name": note_type.name} for note_type in note_types],
            "calendarTypes": [{
                "value": CalendarType.Clinic.value, "label": "Clinic"
            }, {
                "value": CalendarType.Administrative.value, "label": "Administrative"
            }],
            "recurrence": [{
                "value": EventRecurrence.Daily.value, "label": "Daily"
            }, {
                "value": EventRecurrence.Weekly.value, "label": "Weekly"
            }],
            "events": [
                {
                    "id": str(event.id),
                    "title": event.title,
                    "location": str(next(
                        (location.id for location in locations if
                         event.calendar.title.split(": ", 2)[-1] == location.full_name),
                        ""
                    )),
                    "provider": next(provider.id for provider in providers if provider.full_name == event.calendar.title.split(":", 1)[0]),
                    "allowedNoteTypes": [str(note_type.id) for note_type in event.allowed_note_types.all()],
                    "calendar": event.calendar.title,
                    "calendarType": event.calendar.title.split(":", 2)[1].strip(),
                    "startTime": event.starts_at.strftime("%Y-%m-%dT%H:%M"),
                    "endTime": event.ends_at.strftime("%Y-%m-%dT%H:%M"),
                    "daysOfWeek": (
                        event.recurrence and "BYDAY=" in event.recurrence
                        and dict(part.split("=", 1) for part in event.recurrence.removeprefix("RRULE:").split(";")).get("BYDAY", "").split(",")
                    ) or [],
                    "recurrence": {
                        "type": (
                            event.recurrence and "FREQ=" in event.recurrence
                            and dict(part.split("=", 1) for part in event.recurrence.removeprefix("RRULE:").split(";")).get("FREQ", "")
                        ) or '',
                        "interval": (
                            event.recurrence and "INTERVAL=" in event.recurrence
                            and dict(part.split("=", 1) for part in event.recurrence.removeprefix("RRULE:").split(";")).get("INTERVAL", "")
                        ) or 0,
                        "endDate": event.recurrence_ends_at.strftime("%Y-%m-%dT%H:%M") if event.recurrence_ends_at else '',
                    }
                } for event in events
            ],
        }

        return [
            HTMLResponse(
                render_to_string("static/index.html", context),
                status_code=HTTPStatus.OK,
            )
        ]

    # Serve the contents of a js file
    @api.get("/main.js")
    def get_main_js(self) -> list[Response | Effect]:
        return [
            Response(
                render_to_string("static/main.js").encode(),
                status_code=HTTPStatus.OK,
                content_type="text/javascript",
            )
        ]

    # Serve the contents of a css file
    @api.get("/styles.css")
    def get_css(self) -> list[Response | Effect]:
        return [
            Response(
                render_to_string("static/styles.css").encode(),
                status_code=HTTPStatus.OK,
                content_type="text/css",
            )
        ]
