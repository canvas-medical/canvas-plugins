patient_portal_portal_plugin
============================

## Description

The Patient Portal Plugin is a simple plugin that provides various widgets for the patient portal.
The plugin listens to the `PATIENT_PORTAL__WIDGET_CONFIGURATION` event.

## Widgets

### Header Widget

The Header Widget displays the patient's preferred name and has quick links for messaging and scheduling.

There is a configurable secret named `BACKGROUND_COLOR` that can change the
widget color without the need to reinstall it.
It defaults to "#17634d".

In order to deal with `SECRETS` take a look at the
[SDK documentation](https://docs.canvasmedical.com/sdk/secrets/).

For more, visit the [Canvas SDK documentation](https://docs.canvasmedical.com/sdk/data-patient/)

### Important Note!

The CANVAS_MANIFEST.json is used when installing your plugin. Please ensure it
gets updated if you add, remove, or rename protocols.
