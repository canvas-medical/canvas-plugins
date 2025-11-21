from http import HTTPStatus

from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import HTMLResponse, Response
from canvas_sdk.handlers.simple_api import SimpleAPI, api, StaffSessionAuthMixin
from canvas_sdk.templates import render_to_string
from logger import log


class MyWebApp(StaffSessionAuthMixin, SimpleAPI):
    """Web app handler for serving Fullscript frontend files."""
    PREFIX = "/app"

    # Serve templated HTML
    @api.get("/fullscript-app")
    def index(self) -> list[Response | Effect]:
        log.info(f"Fullscript app requested")
        log.info(f"--------------------------------")

        log.info(f"query_string: {self.request.query_string}")

        query_params = dict(param.split('=', 1) for param in self.request.query_string.split('&') if '=' in param)

        log.info(f"params: {query_params}")

        context = {
            "oauthCode": query_params.get("code", ""),
            "patientKey": query_params.get("patient", ""),
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
        return [
            Response(
                render_to_string("static/main.js").encode(),
                status_code=HTTPStatus.OK,
                content_type="text/javascript",
            )
        ]
