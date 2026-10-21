from appointment_copay_collection.handlers.charge_response import channel_for
from canvas_sdk.handlers.simple_api.websocket import WebSocketAPI


class CopayWebSocket(WebSocketAPI):
    """Let a logged-in patient subscribe to their own charge-result channel, and no other."""

    def authenticate(self) -> bool:
        """Accept only a patient connecting to the channel named after them."""
        user = self.websocket.logged_in_user
        return (
            user is not None
            and user["type"] == "Patient"
            and self.websocket.channel == channel_for(user["id"])
        )
