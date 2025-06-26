patient_portal_search_appointments_slots_plugin
=========================================

## Description

This plugin is triggered when a patient searches for available appointments slots for the care team
members, mutating the response to exclude any provider that has no slots available for the search criteria.

### Events

This plugin responds to the following events:

- `PATIENT_PORTAL__APPOINTMENTS__SLOTS__POST_SEARCH`

### Effects

This plugin has the following effects:

- `PATIENT_PORTAL__APPOINTMENTS__SLOTS__POST_SEARCH_RESULTS`


### Important Note!

The CANVAS_MANIFEST.json is used when installing your plugin. Please ensure it
gets updated if you add, remove, or rename protocols.
