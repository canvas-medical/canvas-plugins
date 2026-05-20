from http import HTTPStatus

from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import HTMLResponse, Response
from canvas_sdk.handlers.simple_api import SessionCredentials, SimpleAPI, api
from canvas_sdk.templates import render_to_string


class MyWebApp(SimpleAPI):
    """Serves the clipboard regression test page."""

    PREFIX = "/app"

    def authenticate(self, credentials: SessionCredentials) -> bool:
        return credentials.logged_in_user is not None

    @api.get("/clipboard-demo")
    def index(self) -> list[Response | Effect]:
        return [
            HTMLResponse(
                render_to_string("templates/clipboard-demo.html", {}),
                status_code=HTTPStatus.OK,
            )
        ]
