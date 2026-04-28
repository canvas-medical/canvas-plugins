from canvas_sdk.handlers.simple_api.websocket import WebSocketAPI as WebSocketAPIBase


class WebsocketAPI(WebSocketAPIBase):
    """WebSocket API handler for managing WebSocket connections and authentication."""

    def authenticate(self) -> bool:
        """Authenticate the WebSocket connection."""
        return True


class SecondWebsocketAPI(WebSocketAPIBase):
    """Secondary handler that only accepts a specific channel, used to exercise the
    multi-handler error path in the plugin runner.
    """

    def accept_event(self) -> bool:
        """Only respond to the ``multi_handler`` channel."""
        return self.event.context.get("channel_name") == "multi_handler"

    def authenticate(self) -> bool:
        """Authenticate the WebSocket connection."""
        return True
