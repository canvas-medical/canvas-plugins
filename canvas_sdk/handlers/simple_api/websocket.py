import traceback
from abc import ABC
from functools import cached_property
from typing import ClassVar

import sentry_sdk

from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import AcceptConnection, DenyConnection
from canvas_sdk.events import Event, EventType
from canvas_sdk.handlers.base import BaseHandler
from logger import log

from .exceptions import AuthenticationError, InvalidCredentialsError
from .tools import CaseInsensitiveMultiDict, separate_headers


class WebSocket:
    """WebSocket class for incoming requests to the WebSocketAPI."""

    def __init__(self, event: Event) -> None:
        self.channel = event.context["channel_name"]
        self.headers = CaseInsensitiveMultiDict(separate_headers(event.context["headers"]))
        self.api_key = self.headers.get("authorization")
        self.logged_in_user = (
            {
                "id": self.headers.get("canvas-logged-in-user-id", ""),
                "type": self.headers.get("canvas-logged-in-user-type", ""),
            }
            if "canvas-logged-in-user-id" in self.headers
            else None
        )


class WebSocketAPI(BaseHandler, ABC):
    """Abstract base class for WebSocket APIs."""

    RESPONDS_TO: ClassVar[list[str]] = [
        EventType.Name(EventType.SIMPLE_API_WEBSOCKET_AUTHENTICATE),
    ]

    @cached_property
    def websocket(self) -> WebSocket:
        """Return the WebSocket object for the event."""
        return WebSocket(self.event)

    def compute(self) -> list[Effect]:
        """Handle WebSocket authenticate event."""
        try:
            if self.event.type == EventType.SIMPLE_API_WEBSOCKET_AUTHENTICATE:
                return self._authenticate()
            else:
                raise AssertionError(f"Cannot handle event type {EventType.Name(self.event.type)}")
        except Exception as exception:
            for error_line_with_newlines in traceback.format_exception(exception):
                for error_line in error_line_with_newlines.split("\n"):
                    log.error(error_line)

            sentry_sdk.capture_exception(exception)

            return [DenyConnection(message="Internal server error").apply()]

    def _authenticate(self) -> list[Effect]:
        """Authenticate the WebSocket request."""
        try:
            if self.authenticate():
                return [AcceptConnection().apply()]
            else:
                raise InvalidCredentialsError

        except AuthenticationError:
            return [DenyConnection(message="Unauthorized").apply()]

    def authenticate(self) -> bool:
        """Override to implement authentication."""
        return False


__exports__ = ("WebSocketAPI", "WebSocket")
