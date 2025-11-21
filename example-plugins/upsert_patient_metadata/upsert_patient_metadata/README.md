upsert_patient_metadata
=======================

## Description

Extracts key-value pairs from plan update narratives and stores them as patient metadata.

Parses narrative text for patterns like "key=somekey*value=somevalue" where the separator
can be any non-alphanumeric character. If both key and value are found, creates or updates
the corresponding patient metadata entry.

Triggers on: PLAN_COMMAND__POST_UPDATE events
Effects: PatientMetadata upsert operations

### Important Note!

The CANVAS_MANIFEST.json is used when installing your plugin. Please ensure it
gets updated if you add, remove, or rename protocols.
