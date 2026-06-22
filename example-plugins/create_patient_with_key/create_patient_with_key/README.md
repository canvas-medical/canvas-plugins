Create Patient With Key
=======================

## Description

Demonstrates creating a `Patient` with a **plugin-defined key** instead of letting
the server generate one. The plugin generates a valid key with
`generate_patient_key()`, passes it as `Patient(patient_id=...)`, and returns the key
so you can look the patient up immediately — the key it chose is the patient's id.

This is the feature added in [KOALA-3383](https://canvasmedical.atlassian.net/browse/KOALA-3383):
the instance must be running a build that includes both the SDK change
(`canvas-plugins`) and the home-app interpreter change (`canvas`).

## Setup

Set the `pre-shared-key` plugin secret to a value of your choosing (UI plugin secrets
or [Console](https://docs.canvasmedical.com/sdk/canvas_cli/#canvas-config-set)).

## Try it

Create a patient (the response returns the key the plugin assigned):

```
curl --request POST \
  --url https://<your-instance>.canvasmedical.com/plugin-io/api/create_patient_with_key/create-test-patient \
  --header 'Authorization: <your value for pre-shared-key>'
```

Response:

```json
{"patient_key": "0caa...e1f", "message": "Patient created with this plugin-defined key."}
```

## Verify

The returned `patient_key` IS the patient's id. Confirm the patient exists at exactly
that key:

- FHIR: `GET /Patient/{patient_key}`
- Chart: open `https://<your-instance>.canvasmedical.com/patient/{patient_key}`

A 32-character hex key (a UUID4 without hyphens) is required; `generate_patient_key()`
produces one. An invalid key is rejected before any patient is created.
