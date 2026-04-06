# PayTheory Payment Processor

A Canvas plugin that integrates [Pay Theory](https://paytheory.com) as a credit card payment processor, enabling payment collection directly within the Canvas clinical workflow.

## Features

- Credit card payment processing via Pay Theory's tokenized SDK
- Saved payment methods (add, list, remove) per patient
- Environment-aware configuration (production, sandbox, lab)
- Automatic patient-to-payor mapping in Pay Theory
- Guest payments without requiring a saved payment method

## Configuration

### Secrets

| Secret | Required | Description |
|---|---|---|
| `paytheory_merchant_id` | Yes | The merchant's Pay Theory UID |
| `paytheory_public_key` | Yes | The merchant's public SDK key (used to initialize the JS SDK) |
| `paytheory_secret_key` | Yes | API secret key for backend GraphQL calls |
| `paytheory_partner` | Yes | Partner prefix for URL construction (e.g. `canvas`) |
| `paytheory_environment` | Yes | One of `production`, `sandbox`, or `lab` |

### Environment URLs

The plugin dynamically constructs Pay Theory URLs based on the `paytheory_partner` and `paytheory_environment` secrets:

| Environment | SDK URL | API URL |
|---|---|---|
| production | `{partner}.sdk.paytheory.com` | `api.{partner}.paytheory.com` |
| sandbox | `{partner}.sdk.paytheorystudy.com` | `api.{partner}.paytheorystudy.com` |
| lab | `{partner}.sdk.paytheorylab.com` | `api.{partner}.paytheorylab.com` |

## How It Works

1. **Payment form** -- When a payment is initiated, the plugin renders a Pay Theory JS SDK form inside an iframe. The SDK handles PCI-compliant card input and tokenization.
2. **Tokenization** -- Card details are tokenized client-side by Pay Theory. The plugin never sees raw card numbers.
3. **Charge** -- The tokenized payment method ID is passed to the backend, which calls Pay Theory's GraphQL API to create a transaction.
4. **Saved cards** -- Patients are mapped to Pay Theory payors via metadata (`canvas_patient_id`). Payment methods can be saved, listed, and removed per patient.

## Testing

In the sandbox environment, use these amounts (in dollars) to trigger specific failure scenarios:

| Amount | Error |
|---|---|
| $1.02 | GENERIC_DECLINE |
| $1.93 | INSUFFICIENT_FUNDS |
| $1.94 | INVALID_ACCOUNT_NUMBER |
| $8,899.86 | ADDRESS_VERIFICATION_FAILED_RISK_RULES |
| $8,899.87 | CVV_FAILED_RISK_RULES |
| $8,888.88 | DISPUTE |

## Pending Enhancements

### Transaction Status Webhook (requires new SDK effect)

Pay Theory transactions initially return a `PENDING` status, which the plugin currently treats as successful. Transactions can later transition to `SUCCEEDED`, `FAILED`, `VOIDED`, `SETTLED`, `REFUNDED`, or `DISPUTED`.

Pay Theory supports [webhooks](https://docs.paytheory.com/docs/api/webhooks) that notify an endpoint when transaction statuses change. The plugin could receive these via a `SimpleAPIRoute` handler, but there is currently **no Canvas SDK effect to update a payment transaction status after it has been recorded**.

**What's needed:** A new SDK effect (e.g. `UpdatePaymentTransaction`) that allows a plugin to retroactively update the status of a previously recorded payment. This would enable:

- Marking a `PENDING` payment as `FAILED` or `VOIDED` if Pay Theory reports a failure after the initial charge
- Recording when a payment has `SETTLED` (funds transferred to merchant)
- Handling `REFUNDED` / `PARTIALLY_REFUNDED` status changes
- Flagging `DISPUTED` transactions

Once this effect is available, the implementation would be:
1. Add a `SimpleAPIRoute` endpoint to receive Pay Theory webhook POSTs
2. Register the webhook with Pay Theory via the `createWebhook` GraphQL mutation
3. On webhook receipt, use the new effect to update the transaction status in Canvas

