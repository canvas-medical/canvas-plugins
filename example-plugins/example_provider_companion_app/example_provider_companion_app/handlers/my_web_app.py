from http import HTTPStatus

from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import HTMLResponse, Response
from canvas_sdk.handlers.simple_api import SessionCredentials, SimpleAPI, api
from canvas_sdk.templates import render_to_string
from canvas_sdk.v1.data.staff import Staff

#
# Check out https://docs.canvasmedical.com/sdk/handlers-simple-api-http


class MyWebApp(SimpleAPI):
    """Web application serving pages for each companion scope level."""

    PREFIX = "/app"

    def authenticate(self, credentials: SessionCredentials) -> bool:
        """Authenticate using session credentials."""
        return credentials.logged_in_user is not None

    @api.get("/global")
    def global_app(self) -> list[Response | Effect]:
        """Serve the global companion application page."""
        logged_in_user = Staff.objects.get(id=self.request.headers["canvas-logged-in-user-id"])

        context = {
            "scope": "Global",
            "first_name": logged_in_user.first_name,
            "last_name": logged_in_user.last_name,
            "detail": "This app is not tied to any patient or note.",
        }

        return [
            HTMLResponse(
                render_to_string("static/app.html", context),
                status_code=HTTPStatus.OK,
            )
        ]

    @api.get("/patient")
    def patient_app(self) -> list[Response | Effect]:
        """Serve the patient-specific companion application page."""
        logged_in_user = Staff.objects.get(id=self.request.headers["canvas-logged-in-user-id"])
        patient_id = self.request.query_params.get("patient_id", "unknown")

        context = {
            "scope": "Patient-Specific",
            "first_name": logged_in_user.first_name,
            "last_name": logged_in_user.last_name,
            "detail": f"Viewing patient: {patient_id}",
        }

        return [
            HTMLResponse(
                render_to_string("static/app.html", context),
                status_code=HTTPStatus.OK,
            )
        ]

    @api.get("/note")
    def note_app(self) -> list[Response | Effect]:
        """Serve the note-specific companion application page."""
        logged_in_user = Staff.objects.get(id=self.request.headers["canvas-logged-in-user-id"])
        patient_id = self.request.query_params.get("patient_id", "unknown")
        note_id = self.request.query_params.get("note_id", "unknown")

        context = {
            "scope": "Note-Specific",
            "first_name": logged_in_user.first_name,
            "last_name": logged_in_user.last_name,
            "detail": f"Viewing note: {note_id} for patient: {patient_id}",
        }

        return [
            HTMLResponse(
                render_to_string("static/app.html", context),
                status_code=HTTPStatus.OK,
            )
        ]

    @api.get("/main.js")
    def get_main_js(self) -> list[Response | Effect]:
        """Serve the main JavaScript file."""
        return [
            Response(
                render_to_string("static/main.js").encode(),
                status_code=HTTPStatus.OK,
                content_type="text/javascript",
            )
        ]

    @api.get("/styles.css")
    def get_css(self) -> list[Response | Effect]:
        """Serve the CSS styles file."""
        return [
            Response(
                render_to_string("static/styles.css").encode(),
                status_code=HTTPStatus.OK,
                content_type="text/css",
            )
        ]
