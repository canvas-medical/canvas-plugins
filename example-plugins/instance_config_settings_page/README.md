# instance_config_settings_page

Example plugin demonstrating the `SettingsPageHandler`, the new
handler type that lets a plugin register a native section under
home-app's `/set-up/` instance-configuration UI.

The plugin defines a single section, **Fasting Program**, under the
**Clinical** category. The section shows off the new widget primitives
introduced alongside the handler:

- `CHECKLIST_PICKER` for the prescriber sign-off roles
- `TOGGLE_CARDS` for which responsibilities are enabled
- `COLOR_PICKER` for the patient-facing accent color
- `NUMBER` with `min_value` / `max_value` for the fasting window
- `STATUS_BADGE` for the current rollout phase

Running locally (after `canvas install`):

    canvas install example-plugins/instance_config_settings_page

then open `/set-up/fasting_program/` in your Canvas instance.
