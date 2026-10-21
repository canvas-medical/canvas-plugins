from decimal import Decimal
from http import HTTPStatus
from typing import Any

from appointment_copay_collection.handlers.charge_response import channel_for
from appointment_copay_collection.services.copay import (
    COPAY_AMOUNTS_VARIABLE,
    CopayStatus,
    charge_idempotency_key,
    copay_rows,
    parse_copay_amounts,
    stored_cards,
)
from canvas_sdk.effects import Effect
from canvas_sdk.effects.payment import ChargeStoredCard
from canvas_sdk.effects.simple_api import HTMLResponse, JSONResponse, Response
from canvas_sdk.handlers.simple_api import PatientSessionAuthMixin, SimpleAPI, api
from canvas_sdk.templates import render_to_string


def _appointment_json(row: dict[str, Any]) -> dict[str, Any]:
    """Serialize one copay row for the page."""
    appointment = row["appointment"]
    provider = appointment.provider
    return {
        "id": str(appointment.id),
        "start_time": appointment.start_time.isoformat(),
        "duration_minutes": appointment.duration_minutes,
        "visit_type": appointment.note_type.name if appointment.note_type else None,
        "provider": f"{provider.first_name} {provider.last_name}" if provider else None,
        "location": appointment.location.full_name if appointment.location else None,
        "status": row["status"],
        "amount": str(row["amount"]) if row["amount"] is not None else None,
    }


class CopayAPI(PatientSessionAuthMixin, SimpleAPI):
    """Serve the copay page and charge a stored card for an appointment's copay.

    Every request is made by a logged-in patient, and every lookup is scoped to that patient,
    so a patient can only see and pay for their own appointments.
    """

    PREFIX = "/portal"

    @property
    def patient_id(self) -> str:
        """The id of the logged-in patient."""
        return self.request.headers["canvas-logged-in-user-id"]

    def _configured_amounts(self) -> dict[str, Decimal]:
        return parse_copay_amounts(self.secrets.get(COPAY_AMOUNTS_VARIABLE))

    @api.get("/page")
    def page(self) -> list[Response | Effect]:
        """Serve the copay page."""
        return [
            HTMLResponse(
                render_to_string("templates/copay.html", {"channel": channel_for(self.patient_id)}),
                status_code=HTTPStatus.OK,
            )
        ]

    @api.get("/copay.js")
    def script(self) -> list[Response | Effect]:
        """Serve the page's script."""
        return [
            Response(
                render_to_string("templates/copay.js").encode(),
                status_code=HTTPStatus.OK,
                content_type="text/javascript",
            )
        ]

    @api.get("/copay.css")
    def styles(self) -> list[Response | Effect]:
        """Serve the page's styles."""
        return [
            Response(
                render_to_string("templates/copay.css").encode(),
                status_code=HTTPStatus.OK,
                content_type="text/css",
            )
        ]

    @api.get("/appointments")
    def appointments(self) -> list[Response | Effect]:
        """List the patient's upcoming appointments with their copay, plus their stored cards."""
        rows = copay_rows(self.patient_id, self._configured_amounts())
        return [
            JSONResponse(
                {
                    "appointments": [_appointment_json(row) for row in rows],
                    "cards": stored_cards(self.patient_id),
                },
                status_code=HTTPStatus.OK,
            )
        ]

    @api.post("/appointments/<appointment_id>/pay")
    def pay(self) -> list[Response | Effect]:
        """Charge the chosen stored card for the appointment's copay.

        The amount and the claim are recomputed here rather than taken from the request, so the
        page cannot change what is charged or where it is posted. The charge result arrives
        later as a REVENUE__STORED_CARD__CHARGE_RESPONSE event.
        """
        appointment_id = self.request.path_params["appointment_id"]
        body = self.request.json()
        payment_card_id = body.get("payment_card_id") if isinstance(body, dict) else None

        rows = copay_rows(self.patient_id, self._configured_amounts())
        row = next((r for r in rows if str(r["appointment"].id) == appointment_id), None)
        if row is None:
            return [
                JSONResponse({"error": "Appointment not found."}, status_code=HTTPStatus.NOT_FOUND)
            ]
        if row["status"] != CopayStatus.DUE:
            return [
                JSONResponse(
                    {"error": "This appointment has no copay to pay.", "status": row["status"]},
                    status_code=HTTPStatus.CONFLICT,
                )
            ]
        if not isinstance(payment_card_id, str) or payment_card_id not in {
            card["id"] for card in stored_cards(self.patient_id)
        }:
            return [
                JSONResponse(
                    {"error": "Choose one of your saved cards."},
                    status_code=HTTPStatus.BAD_REQUEST,
                )
            ]

        amount = row["amount"]
        idempotency_key = charge_idempotency_key(appointment_id, payment_card_id, amount)
        return [
            JSONResponse(
                {"idempotency_key": str(idempotency_key), "amount": str(amount)},
                status_code=HTTPStatus.ACCEPTED,
            ),
            ChargeStoredCard(
                patient_id=self.patient_id,
                payment_card_id=payment_card_id,
                amount=amount,
                idempotency_key=idempotency_key,
                claim_id=str(row["claim"].id),
                copay=True,
                description="Appointment copay",
            ).apply(),
        ]
