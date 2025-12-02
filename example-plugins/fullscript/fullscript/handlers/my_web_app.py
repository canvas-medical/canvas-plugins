from http import HTTPStatus

from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import HTMLResponse, Response
from canvas_sdk.handlers.simple_api import SimpleAPI, StaffSessionAuthMixin, api
from canvas_sdk.templates import render_to_string
from logger import log


class MyWebApp(StaffSessionAuthMixin, SimpleAPI):
    """Web app handler for serving Fullscript frontend files."""

    PREFIX = "/app"

    # Serve templated HTML
    @api.get("/fullscript-app")
    def index(self) -> list[Response | Effect]:
        """Serve the Fullscript web app HTML page with templated context."""
        log.info("Fullscript app requested")
        log.info(f"params: {self.request.query_params}")

        context = {
            "oauthCode": self.request.query_params.get("code", ""),
            "patientKey": self.request.query_params.get("patient", ""),
            "noteId": self.request.query_params.get("noteId", ""),
            "fullscriptClientId": self.secrets["FULLSCRIPT_CLIENT_ID"],
            "applicationId": self.secrets["FULLSCRIPT_APPLICATION_ID"],
        }

        log.info(f"context: {context}")

        return [
            HTMLResponse(
                render_to_string("static/index.html", context),
                status_code=HTTPStatus.OK,
            )
        ]

    # Serve the contents of a js file
    @api.get("/main.js")
    def get_main_js(self) -> list[Response | Effect]:
        """Serve the Fullscript web app main.js file."""
        return [
            Response(
                render_to_string("static/main.js").encode(),
                status_code=HTTPStatus.OK,
                content_type="text/javascript",
            )
        ]
