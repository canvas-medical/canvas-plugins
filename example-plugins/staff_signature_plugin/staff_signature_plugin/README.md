# staff_signature_plugin

Adds a **My Signature** button to the chart patient header. When clicked, it
opens a modal that displays the logged-in staff member's signature image.

## How it works

- `handlers/signature_button.py` — an `ActionButton` on `CHART_PATIENT_HEADER`
  that returns a `LaunchModalEffect` pointing at this plugin's API route.
- `handlers/signature_api.py` — a `SimpleAPIRoute` (with
  `StaffSessionAuthMixin`) that looks up the logged-in `Staff` record and
  renders the signature image into an HTML template.
- `templates/signature_modal.html` — the modal body.

The signature itself is exposed via `Staff.signature_url`, which returns a
presigned S3 URL for the FileField stored on the home-app `Staff` model.

## Install

```sh
canvas install ./example-plugins/staff_signature_plugin
```

Open any patient chart in Canvas; the **My Signature** button will appear in
the chart's patient header.
