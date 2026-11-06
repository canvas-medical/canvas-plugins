from http import HTTPStatus

from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import Response
from canvas_sdk.handlers.simple_api import Credentials, SimpleAPIRoute


class NoAuth(SimpleAPIRoute):
    """SimpleAPIRoute base class to bypass authentication."""

    def authenticate(self, credentials: Credentials) -> bool:
        """Authenticate the request."""
        return True


class Route(NoAuth):
    """Handler for /route."""

    PATH = "/route"

    def get(self) -> list[Response | Effect]:
        """Handler method for GET."""
        return [Response(status_code=HTTPStatus.OK)]


class PatternRoute(NoAuth):
    """Handler for /items/<item_id>, which claims a different route than it matched."""

    PATH = "/items/<item_id>"

    @property
    def matched_route(self) -> tuple[str, str] | None:
        """Claim a route that names the request's own path."""
        return ("GET", self.event.context["path"])

    def get(self) -> list[Response | Effect]:
        """Handler method for GET."""
        return [Response(status_code=HTTPStatus.OK)]


class ErrorRoute1(NoAuth):
    """Handler #1 for /error."""

    PATH = "/error"

    def get(self) -> list[Response | Effect]:
        """Handler method for GET."""
        return [Response(status_code=HTTPStatus.OK)]


class ErrorRoute2(NoAuth):
    """Handler #2 for /error."""

    PATH = "/error"

    def get(self) -> list[Response | Effect]:
        """Handler method for GET."""
        return [Response(status_code=HTTPStatus.OK)]
