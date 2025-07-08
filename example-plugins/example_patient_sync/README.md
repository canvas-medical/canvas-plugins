example_patient_sync
==========================

## Description

An example of bidirectional patient creation between Canvas and a 3rd party system.

At a high level, this plugin:
1. Adds an API endpoint to which the external system can POST a new patient object with a given system_id, which creates a patient in Canvas with an external_identifier.
2. Configures a webhook for the PATIENT_CREATED event to automatically synchronize patient data. When a patient is created in Canvas, the webhook triggers an update (or creation) in the external system via its patient GET/POST/PATCH API, ensuring the Canvas ID is always included.
