example_patient_sync
==========================

## Description

An example of bidirectional patient creation between Canvas and a 3rd party system (Bridge, in this case).

At a high level, this plugin:
1. Adds an API endpoint that external system can POST a new patient object to, which creates a patient creation request.
2. Adds an event listener to the patient__creation event, which will ensure that when a patient is created in Canvas, that patient is also created and/or updated (with a Canvas ID) using the external system's API methods for patient GET/POST/PATCH.
