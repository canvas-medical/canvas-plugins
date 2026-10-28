import json
from base64 import b64encode
from decimal import Decimal
from http import HTTPStatus
from typing import Any
from unittest.mock import MagicMock

import pytest
from appointment_copay_collection.applications.copay_application import CopayApplication
from appointment_copay_collection.handlers.charge_response import ChargeResponseHandler
from appointment_copay_collection.handlers.copay_api import CopayAPI
from appointment_copay_collection.handlers.copay_websocket import CopayWebSocket
from appointment_copay_collection.services.copay import charge_idempotency_key

from canvas_sdk.effects import Effect, EffectType
from canvas_sdk.effects.simple_api import Response
from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.test_utils.factories import PatientFactory, PaymentCardFactory
from canvas_sdk.v1.data import Appointment, Claim, Patient

from .conftest import AppointmentMaker


def _call(
    endpoint: str,
    patient: Patient,
    *,
    method: str = "GET",
    path: str,
    body: dict[str, Any] | None = None,
    secrets: dict[str, str] | None = None,
) -> tuple[HTTPStatus, dict[str, Any], list[Effect]]:
    """Call a CopayAPI endpoint as the given logged-in patient."""
    event = Event(
        EventRequest(
            type=EventType.SIMPLE_API_REQUEST,
            context=json.dumps(
                {
                    "method": method,
                    "path": path,
                    "query_string": "",
                    "body": b64encode(json.dumps(body or {}).encode()).decode(),
                    "headers": {
                        "Content-Type": "application/json",
                        "canvas-logged-in-user-type": "Patient",
                        "canvas-logged-in-user-id": str(patient.id),
                    },
                }
            ),
        )
    )
    api = CopayAPI(event, secrets=secrets or {})
    result = getattr(api, endpoint)()
    response = result[0]
    assert isinstance(response, Response)
    effects = [effect for effect in result[1:] if isinstance(effect, Effect)]
    return HTTPStatus(response.status_code), json.loads(response.content or b"{}"), effects


def _pay(
    patient: Patient, appointment: Appointment, payment_card_id: str
) -> tuple[HTTPStatus, dict[str, Any], list[Effect]]:
    return _call(
        "pay",
        patient,
        method="POST",
        path=f"/portal/appointments/{appointment.id}/pay",
        body={"payment_card_id": payment_card_id},
        secrets={"COPAY_AMOUNTS": '{"office-visit": "25.00"}'},
    )


@pytest.mark.django_db
def test_appointments_lists_the_patients_copays_and_cards(
    patient: Patient, make_appointment: AppointmentMaker
) -> None:
    """The appointments endpoint returns the logged-in patient's appointments and saved cards."""
    appointment = make_appointment(patient)
    card = PaymentCardFactory.create(patient=patient)

    status, body, _ = _call(
        "appointments",
        patient,
        path="/portal/appointments",
        secrets={"COPAY_AMOUNTS": '{"office-visit": "25.00"}'},
    )

    assert status == HTTPStatus.OK
    assert [(a["id"], a["status"], a["amount"]) for a in body["appointments"]] == [
        (str(appointment.id), "due", "25.00")
    ]
    assert [c["id"] for c in body["cards"]] == [str(card.id)]


@pytest.mark.django_db
def test_pay_charges_the_copay_on_the_appointment_claim(
    patient: Patient, make_appointment: AppointmentMaker
) -> None:
    """Paying emits ChargeStoredCard for the configured amount, posted as a copay to the claim."""
    appointment = make_appointment(patient)
    card = PaymentCardFactory.create(patient=patient)
    claim = Claim.objects.get(note=appointment.note)

    status, body, effects = _pay(patient, appointment, str(card.id))

    key = str(charge_idempotency_key(str(appointment.id), str(card.id), Decimal("25.00")))
    assert status == HTTPStatus.ACCEPTED
    assert body == {"idempotency_key": key, "amount": "25.00"}
    [effect] = effects
    assert effect.type == EffectType.REVENUE__STORED_CARD__CHARGE
    assert json.loads(effect.payload)["data"] == {
        "patient_id": str(patient.id),
        "payment_card_id": str(card.id),
        "amount": "25.00",
        "idempotency_key": key,
        "claim_id": str(claim.id),
        "copay": True,
        "description": "Appointment copay",
    }


@pytest.mark.django_db
def test_pay_rejects_another_patients_appointment(
    patient: Patient, make_appointment: AppointmentMaker
) -> None:
    """A patient can't pay for an appointment that isn't theirs."""
    appointment = make_appointment(PatientFactory.create())
    card = PaymentCardFactory.create(patient=patient)

    status, _, effects = _pay(patient, appointment, str(card.id))

    assert (status, effects) == (HTTPStatus.NOT_FOUND, [])


@pytest.mark.django_db
def test_pay_rejects_an_appointment_with_no_copay_due(
    patient: Patient, make_appointment: AppointmentMaker
) -> None:
    """A non-billable appointment is never charged."""
    appointment = make_appointment(patient, billable=False, with_claim=False)
    card = PaymentCardFactory.create(patient=patient)

    status, body, effects = _pay(patient, appointment, str(card.id))

    assert (status, body["status"], effects) == (HTTPStatus.CONFLICT, "not_billable", [])


@pytest.mark.django_db
def test_pay_rejects_a_card_the_patient_does_not_own(
    patient: Patient, make_appointment: AppointmentMaker
) -> None:
    """Only one of the patient's own saved cards can be charged."""
    appointment = make_appointment(patient)
    card = PaymentCardFactory.create()

    status, _, effects = _pay(patient, appointment, str(card.id))

    assert (status, effects) == (HTTPStatus.BAD_REQUEST, [])


def _websocket_event(channel: str, user_type: str, user_id: str) -> Event:
    return Event(
        EventRequest(
            type=EventType.SIMPLE_API_WEBSOCKET_AUTHENTICATE,
            context=json.dumps(
                {
                    "channel_name": channel,
                    "headers": {
                        "canvas-logged-in-user-type": user_type,
                        "canvas-logged-in-user-id": user_id,
                    },
                }
            ),
        )
    )


@pytest.mark.parametrize(
    ("channel", "user_type", "accepted"),
    [
        ("copay-abc", "Patient", True),
        ("copay-someone-else", "Patient", False),
        ("copay-abc", "Staff", False),
    ],
)
def test_websocket_accepts_only_a_patient_on_their_own_channel(
    channel: str, user_type: str, accepted: bool
) -> None:
    """A patient may listen on their own channel, and nobody may listen on another's."""
    [effect] = CopayWebSocket(_websocket_event(channel, user_type, "abc")).compute()

    expected = (
        EffectType.SIMPLE_API_WEBSOCKET_ACCEPT if accepted else EffectType.SIMPLE_API_WEBSOCKET_DENY
    )
    assert effect.type == expected


def _family_member(**levels: str) -> dict[str, str]:
    """Headers for a family member acting on patient abc's chart, with its access by area."""
    return {
        "canvas-logged-in-user-type": "Patient",
        "canvas-logged-in-user-id": "abc",
        "canvas-logged-in-acting-user-id": "42",
        **{f"canvas-logged-in-access-{area}": level for area, level in levels.items()},
    }


def _authenticate(method: str, path: str, headers: dict[str, str]) -> HTTPStatus:
    """Run CopayAPI's authentication for a request with these headers."""
    event = Event(
        EventRequest(
            type=EventType.SIMPLE_API_AUTHENTICATE,
            context=json.dumps(
                {"method": method, "path": path, "query_string": "", "body": "", "headers": headers}
            ),
        )
    )
    [effect] = CopayAPI(event).compute()
    return HTTPStatus(json.loads(effect.payload)["status_code"])


LIST = ("GET", "/portal/appointments")
PAY = ("POST", "/portal/appointments/1/pay")
OWN_CHART = {"canvas-logged-in-user-type": "Patient", "canvas-logged-in-user-id": "abc"}
CAN_VIEW = _family_member(appointments="view", billing="view")
CAN_PAY = _family_member(appointments="view", billing="act")


@pytest.mark.parametrize(
    ("route", "headers", "expected"),
    [
        (LIST, OWN_CHART, HTTPStatus.OK),
        (PAY, OWN_CHART, HTTPStatus.OK),
        (LIST, CAN_VIEW, HTTPStatus.OK),
        (PAY, CAN_VIEW, HTTPStatus.UNAUTHORIZED),
        (PAY, CAN_PAY, HTTPStatus.OK),
        (LIST, _family_member(billing="act"), HTTPStatus.UNAUTHORIZED),
        (LIST, _family_member(), HTTPStatus.UNAUTHORIZED),
    ],
    ids=[
        "patient lists",
        "patient pays",
        "view lists",
        "view can't pay",
        "act pays",
        "no appointments access",
        "no access",
    ],
)
def test_a_family_member_needs_view_access_to_list_and_act_access_to_pay(
    route: tuple[str, str], headers: dict[str, str], expected: HTTPStatus
) -> None:
    """A family member acting on the chart sees its copays with view access to appointments and
    billing, and pays with act access to billing.
    """
    method, path = route

    assert _authenticate(method, path, headers) == expected


@pytest.mark.parametrize(
    ("headers", "accepted"),
    [(CAN_VIEW, True), (_family_member(appointments="view"), False)],
    ids=["view", "no billing access"],
)
def test_websocket_holds_a_family_member_to_the_pages_access(
    headers: dict[str, str], accepted: bool
) -> None:
    """A family member listens on the chart's channel only with the access the page needs."""
    event = Event(
        EventRequest(
            type=EventType.SIMPLE_API_WEBSOCKET_AUTHENTICATE,
            context=json.dumps({"channel_name": "copay-abc", "headers": headers}),
        )
    )

    [effect] = CopayWebSocket(event).compute()

    expected = (
        EffectType.SIMPLE_API_WEBSOCKET_ACCEPT if accepted else EffectType.SIMPLE_API_WEBSOCKET_DENY
    )
    assert effect.type == expected


def test_charge_response_is_broadcast_to_the_patients_channel() -> None:
    """The charge result is pushed to the patient's channel, keyed by idempotency key."""
    event = MagicMock()
    event.context = {
        "patient_id": "abc",
        "idempotency_key": "key",
        "success": False,
        "amount": "25.00",
        "payment_intent_id": None,
        "error": {"code": "card_declined", "message": "Your card was declined."},
    }

    [effect] = ChargeResponseHandler(event).compute()

    assert effect.type == EffectType.SIMPLE_API_WEBSOCKET_BROADCAST
    assert json.loads(effect.payload)["data"] == {
        "channel": "copay-abc",
        "message": {
            "event_type": "charge_response",
            "idempotency_key": "key",
            "success": False,
            "amount": "25.00",
            "error_code": "card_declined",
        },
    }


def test_application_opens_the_copay_page() -> None:
    """The portal menu item opens the copay page as a full page."""
    effect = CopayApplication(MagicMock()).on_open()

    assert effect.type == EffectType.LAUNCH_MODAL
    payload = json.loads(effect.payload)["data"]
    assert payload["url"] == "/plugin-io/api/appointment_copay_collection/portal/page"
    assert payload["target"] == "page"
