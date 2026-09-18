# patient_portal_link

Mints a patient's portal link and delivers it over the practice's own provider instead of Canvas's built-in Twilio and SendGrid.

Canvas's own "Send invite" sends over Canvas's Twilio or SendGrid. `patient_portal_http.get_login_url()` returns the same link without sending anything, so a plugin can put it in a message from the practice's own number or address.

> **⚠️ This endpoint mints a patient credential**
>
> Canvas forwards every `/plugin-io/api/...` request to the plugin without authenticating it, so `authenticate()` is the only thing between the internet and a portal login link. This route is exactly as protected as `my-api-key` is: give it the strength of a password, and never widen `authenticate()` to admit an unauthenticated caller. Anyone who gets past it can mint a link for any patient whose id they can guess or enumerate.

## Endpoint

```
POST /plugin-io/api/patient_portal_link/send
Authorization: <your value for my-api-key>
Content-Type: application/json

{"patient_id": "<32-character patient id>"}
```

## Secrets

| Name | Purpose |
| --- | --- |
| `my-api-key` | Authenticates callers of this endpoint |
| `sms-provider-url` | Where to POST the outbound message |
| `sms-provider-token` | Bearer token for that provider |

The endpoint is protected with [API key authentication](https://docs.canvasmedical.com/sdk/handlers-simple-api-http/#api-key-1). Set these values on the plugin's configuration page in your EHR once it is installed.

## The link

A first invite and a forgotten-password reset are the same link. The portal decides whether to show account activation or a password reset when the link is opened, from the recipient's `CanvasUser.is_portal_registered`, so passing `link_type="invite"` or `"reset"` does not change the URL. Read `is_portal_registered` to choose your own message copy, which is what this plugin does.

The link carries an opaque access token that Canvas validates by lookup. Nothing in it is signed, so there is no signature for a plugin to verify. Appending `?action=activate` does nothing either: that parameter is only read on the portal's self-service form, which is the page a patient reaches without a token.

`get_login_url` raises `PatientPortalLinkError` if the link could not be minted.

## Swapping the transport

`deliver()` stands in for a real provider call. Replace the URL and payload with RingCentral, a customer-owned Twilio account, or anything else that speaks HTTP. `Http` is the SDK's general-purpose outbound client.
