from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import Broadcast
from canvas_sdk.events import EventType
from canvas_sdk.handlers import BaseHandler


def channel_for(patient_id: str) -> str:
    """Return the WebSocket channel a patient's copay page listens on."""
    return f"copay-{patient_id}"


class ChargeResponseHandler(BaseHandler):
    """Push the result of a stored-card charge to the patient's open copay page.

    The page matches the result to its pending payment by idempotency key.
    """

    RESPONDS_TO = EventType.Name(EventType.REVENUE__STORED_CARD__CHARGE_RESPONSE)

    def compute(self) -> list[Effect]:
        """Broadcast the charge result on the patient's channel."""
        context = self.event.context
        patient_id = context.get("patient_id")
        if not patient_id:
            return []

        error = context.get("error") or {}
        return [
            Broadcast(
                channel=channel_for(patient_id),
                message={
                    "event_type": "charge_response",
                    "idempotency_key": context.get("idempotency_key"),
                    "success": bool(context.get("success")),
                    "amount": context.get("amount"),
                    "error_code": error.get("code"),
                },
            ).apply()
        ]
