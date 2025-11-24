example_patient_sync
==========================

## Description

An example of bidirectional patient creation between Canvas and a 3rd party system.

At a high level, this plugin:
1. Adds an API endpoint to which the external system can POST a new patient object with a given system_id, which creates a patient in Canvas with an external_identifier.
2. Configures a webhook for the PATIENT_CREATED event to automatically synchronize patient data. When a patient is created in Canvas, the webhook triggers an update (or creation) in the external system via its patient GET/POST/PATCH API, ensuring the Canvas ID is always included.

## Sample CURL request

Once the API endpoint POST action is created, test it is working with the following CURL command (or use a popular GUI like Postman or Bruno). Replace "training" with your Canvas instance name:

```
curl --request POST \
  --url https://training.canvasmedical.com/plugin-io/api/example_patient_sync/patients \
  --header 'content-type: application/json' \
  --header 'authorization: 97f2a0f033666d29ff09ee42b3afd7e4'
  --data '{
  "firstName": "Alice",
  "lastName": "Example",
  "sexAtBirth": "F",
  "dateOfBirth": "1980-02-22",
  "partnerId": "pat_12345678"
}'
```

## Defining and Setting Secrets

This example plugin defines four "secrets" in the manifest file:

```
    "secrets": [
        "PARTNER_URL_BASE",
        "PARTNER_API_BASE_URL",
        "PARTNER_SECRET_API_KEY",
        "simpleapi-api-key"
    ],
```
Once defined in the `MANIFEST.json`, set the secrets for your plugin in the Admin UI of your Canvas EMR. [Read more](https://docs.canvasmedical.com/sdk/secrets/)

### PARTNER_URL_BASE
This string value will be set as the "system" in the patient external identifier that is created. A patient can have many external identifiers, so make sure this is a unique value that is searchable to find their external ID in the future. [Read more](https://docs.canvasmedical.com/sdk/effect-create-patient-external-identifier/)

### PARTNER_API_BASE_URL
This string value will be used when making REST API calls to a partner system (to create or update a patient record, for example). It may or may not be the same as the PARTNER_URL_BASE.

### PARTNER_SECRET_API_KEY
If accessing a partner API requires authorization, this can define the auth secret to enable the API handshake.

### simpleapi-api-key
This is the authorization needed for Canvas when using APIKeyAuthMixin. [Read more](https://docs.canvasmedical.com/sdk/handlers-simple-api-http/#session)
