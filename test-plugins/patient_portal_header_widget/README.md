Patient Portal Header Widget
============================

## Description

The Patient Portal Header widget is a simple widget, often sitting at the top of the portal.
The widget will be available upon the `PATIENT_PORTAL__WIDGET_CONFIGURATION` event.

There is a configurable secret named `BACKGROUND_COLOR` that can change the widget color without the need to reinstall it.
It defaults to "rgb(12, 98, 72)".

In order to deal with `SECRETS` take a look at the[SDK documentation](https://docs.canvasmedical.com/sdk/secrets/).

### Important Note!

The CANVAS_MANIFEST.json is used when installing your plugin. Please ensure it
gets updated if you add, remove, or rename the handler.
