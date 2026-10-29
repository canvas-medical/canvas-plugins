# Appointment Copay Collection

A patient portal page where a patient pays the copay for an upcoming appointment with a card saved to their account. The payment is posted to the appointment claim's COPAY line item, the same way a copay collected by staff in "Collect payment" is recorded.

## How it works

1. The **Appointment Copays** portal menu item opens the page.
2. The page lists the patient's upcoming appointments that aren't canceled or no-showed.
3. A billable appointment has a claim from the moment it is booked (appointment → note → claim), so its copay can be paid right away.
4. The patient picks a saved card and pays. The plugin emits `ChargeStoredCard` with the appointment's `claim_id` and `copay=True`.
5. The result arrives as a `REVENUE__STORED_CARD__CHARGE_RESPONSE` event, which is pushed to the open page over a WebSocket.

## Copay amount

1. The amount configured for the appointment's note type in `COPAY_AMOUNTS`.
2. Otherwise, the copay on the patient's primary active coverage (`EligibilitySummary.copay_cents`).

`COPAY_AMOUNTS` is a JSON object of note type code to dollar amount:

```json
{"office-visit": "25.00", "telehealth": "15.00"}
```

## Appointment states

| State | Shown when |
| --- | --- |
| Due | Billable, the claim exists, no copay posted yet, and an amount is known |
| Copay paid | The claim already has a copay payment |
| No payment needed | The note type is not billable, so there is no claim to charge |
| Payment isn't available yet | Billable, but the claim doesn't exist |
| No copay on file | Neither `COPAY_AMOUNTS` nor the primary coverage has an amount |

## Safeguards

- Every lookup is scoped to the patient whose chart the request acts on, and the WebSocket only accepts a session on that chart's channel.
- A family member acting on the patient's chart needs view access to its appointments and billing to open the page or listen for results, and act access to its billing to pay.
- The amount and claim are recomputed on the server for every payment; the page only sends the appointment and the card.
- The idempotency key is derived from the appointment, card and amount, so a repeated submission reaches Stripe as a retry of the same charge.

## Components

| File | Responsibility |
| --- | --- |
| `applications/copay_application.py` | Portal menu item that opens the page |
| `handlers/copay_api.py` | Serves the page, lists appointments, and emits `ChargeStoredCard` |
| `handlers/charge_response.py` | Broadcasts the charge result to the patient's channel |
| `handlers/copay_websocket.py` | Authenticates the patient's WebSocket connection |
| `services/copay.py` | Copay amount, claim lookup, status, and idempotency key |
