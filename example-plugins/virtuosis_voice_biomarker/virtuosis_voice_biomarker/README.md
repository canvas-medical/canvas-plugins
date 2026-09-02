# Virtuosis

This Canvas example integrates the Virtuosis API for consent-gated analysis of completed voice
recordings. It exposes staff-authenticated endpoints for starting selected analyses and retrieving
their current results.

The plugin does not record audio, create patient or speaker accounts, or write results to the chart.
Those steps depend on the customer's approved workflow, identity mapping, consent process,
retention policy and clinical governance.

## Configuration

Add `VIRTUOSIS_API_TOKEN` as a sensitive plugin variable. Never include the token, patient
identifiers, recordings or results in source control.

## Endpoints

`POST /plugin-io/api/virtuosis_voice_biomarker/analysis`

```json
{
  "account_id": "pseudonymous Virtuosis account UUID",
  "recorded_at": "2026-08-23T10:00:00Z",
  "analysis": ["wellbeing"],
  "audio_base64": "base64-encoded WAV, MP3, MP4 or OGG",
  "consent_confirmed": true,
  "isolate_oldest_speaker": false
}
```

`GET /plugin-io/api/virtuosis_voice_biomarker/analysis/<recording_id>?analysis=wellbeing`

Use only analyses enabled for the customer's contract and intended purpose. Virtuosis outputs are
decision-support information and must not be treated as standalone diagnoses. Validate the final
workflow and terminology mapping before writing any output to the medical record.
