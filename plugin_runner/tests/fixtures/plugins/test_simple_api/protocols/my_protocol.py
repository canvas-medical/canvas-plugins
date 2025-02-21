from canvas_generated.messages.effects_pb2 import Effect
from canvas_sdk.effects.simple_api import Response
from canvas_sdk.handlers.simple_api import Credentials, SimpleAPIRoute


class NoAuth(SimpleAPIRoute):
    """SimpleAPIRoute base class to bypass authentication."""

    def authenticate(self, credentials: Credentials) -> bool:
        """Authenticate the request."""
        return True


class Route1(NoAuth):
    """Handler #1 for /route."""

    PATH = "/route"

    def get(self) -> list[Response | Effect]:
        """Handler method for GET."""
        return []


class Route2(NoAuth):
    """Handler #2 for /route."""

    PATH = "/route"

    def get(self) -> list[Response | Effect]:
        """Handler method for GET."""
        return []
