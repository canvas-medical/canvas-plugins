example_provider_companion_app
=====================

## Description

This plugin demonstrates how to build provider companion applications at each
of the three supported scope levels:

- **Global** (`provider_companion_global`) — Apps on the companion main page,
  not tied to any patient. Use for multi-patient workflows, dashboards, or
  administrative tools.

- **Patient-specific** (`provider_companion_patient_specific`) — Apps on the
  patient detail page. Receives the patient's ID in the event context. Use for
  per-patient tools like vitals viewers, chart summaries, or risk scoring.

- **Note-specific** (`provider_companion_note_specific`) — Apps within an
  expanded note. Receives both patient and note information in the event
  context. Use for encounter-level tools like documentation assistants.

Each application class in `applications/my_application.py` shows how to read
the relevant context from `self.event.context` and pass it to the launched page.

The web handler in `handlers/my_web_app.py` serves a page for each scope level,
demonstrating how to use session authentication and template rendering.

### Important Note!

The CANVAS_MANIFEST.json is used when installing your plugin. Please ensure it
gets updated if you add, remove, or rename protocols.
