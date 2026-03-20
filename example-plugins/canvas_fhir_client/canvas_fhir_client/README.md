canvas_fhir_client
==============

## Description

Plugin that interacts with Canvas FHIR APIs.

## Configuration

This example plugin defines the following "secrets" in the manifest file:

```
    "secrets": [
        "CANVAS_FHIR_CLIENT_ID",
        "CANVAS_FHIR_CLIENT_SECRET"
    ],
```
Once defined in the `MANIFEST.json`, set the secrets for your plugin in the Admin UI of your Canvas EMR. [Read more](https://docs.canvasmedical.com/sdk/secrets/)

### CANVAS_FHIR_CLIENT_ID
[ClientId](https://docs.canvasmedical.com/api/customer-authentication/#client-credentials)
[ClientSecret](https://docs.canvasmedical.com/api/customer-authentication/#client-credentials)
