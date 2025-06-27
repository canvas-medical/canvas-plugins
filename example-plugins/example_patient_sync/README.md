example_patient_sync
==========================

## Description

An example of bidirectional patient creation between Canvas and a 3rd party system.

At a high level, this plugin:
1. Adds an API endpoint to which the external system can POST a new patient object, which returns a patient creation request.
2. Adds an event listener on the PATIENT_CREATED event, which will ensure that when a patient is created in Canvas, that patient is also created and/or updated (with a Canvas ID) using the external system's API methods for patient GET/POST/PATCH.

## Patient Sync Flowchart

```mermaid
flowchart TD
    A["Start: compute() called"] --> B["Get canvas_patient_id from self.target"]
    B --> C["Get Patient object from DB"]
    C --> D["Check for existing_partner_id in Canvas"]
    D -->|Exists| E["No update needed, skip to API payload"]
    D -->|Does NOT exist| F["Call get_patient_from_system_api()"]
    F --> G["If system_patient_id found in response"]
    G -->|Yes| H["Set update_patient_external_identifier = True"]
    G -->|No| I["Set update_patient_external_identifier = False"]
    E & H & I --> J["Build partner_payload with patient info"]
    J --> K["POST to partner API /patients/v2 or /patients/v2/{system_patient_id}"]
    K --> L["Check response: status_code == 409?"]
    L -->|Yes| M["Log: Patient already exists, return []"]
    L -->|No, but update_patient_external_identifier| N["CreatePatientExternalIdentifier effect, return [effect]"]
    L -->|No and no update needed| O["Return []"]
```