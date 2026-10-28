from appointment_copay_collection.handlers.charge_response import channel_for
from canvas_sdk.handlers.simple_api import PortalAccessLevel
from canvas_sdk.handlers.simple_api.websocket import WebSocketAPI


class CopayWebSocket(WebSocketAPI):
    """Let a session subscribe to the charge results of the chart it acts on, and no other.

    A family member acting on the chart needs the access the copay page needs.
    """

    PORTAL_ACCESS = {"appointments": PortalAccessLevel.VIEW, "billing": PortalAccessLevel.VIEW}

    def authenticate(self) -> bool:
        """Accept only a patient session connecting to the channel of the chart it acts on."""
        user = self.websocket.logged_in_user
        return (
            user is not None
            and user["type"] == "Patient"
            and self.websocket.channel == channel_for(user["id"])
        )
