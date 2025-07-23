patient_portal_portal_plugin
============================

## Description

The Patient Portal Plugin is a simple plugin that provides various widgets for the patient portal.
The plugin listens to the `PATIENT_PORTAL__WIDGET_CONFIGURATION` event.


## Widgets

### Header Widget

The Header Widget displays the patient's preferred name and has quick links for messaging and scheduling.

For more, visit the [Canvas SDK documentation](https://docs.canvasmedical.com/sdk/data-patient/)


### Care Team Widget

It is used to display a compact widget in the Patient Portal that lists the
active care team members for a patient.

It renders a scrollable list in a compact plugin format of all active members. 

For more information, visit the [Canvas SDK documentation](https://docs.canvasmedical.com/sdk/data-care-team/).


### Footer Widget

The Footer Widget displays the support contact information for the patient.


## Secrets

The Patient Portal Plugin uses the following secrets:

- `BACKGROUND_COLOR`: The background color for the widgets. Defaults to `#17634d`.
- `EMERGENCY_CONTACT`: The emergency contact information. Defaults to `1-888-555-5555`.


In order to deal with `SECRETS` take a look at the
[SDK documentation](https://docs.canvasmedical.com/sdk/secrets/).


## Important Note!

The CANVAS_MANIFEST.json is used when installing your plugin. Please ensure it
gets updated if you add, remove, or rename protocols.
