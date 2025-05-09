from canvas_sdk.handlers.simple_api import WebSocketAPI as WebSocketAPIBase


class WebsocketAPI(WebSocketAPIBase):
    """WebSocket API handler for managing WebSocket connections and authentication."""

    def authenticate(self) -> bool:
        """Authenticate the WebSocket connection."""
        return True
