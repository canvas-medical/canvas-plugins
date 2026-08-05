example_provider_menu_configuration
===================================

## Description

Demonstrates `ProviderMenuConfiguration`, the effect that decides which items
render in the provider (hamburger) menu.

Three handlers work together to remove the native scheduling entry points:

- `HideScheduleMenuItem` responds to `GET_PROVIDER_MENU_CONFIGURATION` and returns an
  allow-list containing every menu item **except** `SCHEDULE`, so the Schedule
  item stops rendering.
- `HideAppointmentsPanelFilter` responds to `PANEL_SECTIONS_CONFIGURATION` and
  returns every global panel section **except** `APPOINTMENT`, hiding the
  Appointments filter from the panel's preset filter bar.
- `LandOnPatientsInsteadOfSchedule` responds to `GET_HOMEPAGE_CONFIGURATION` and
  points the default landing page at `/patients`.

The last handler matters. Hiding the Schedule menu item does not change where
providers land after logging in — that still defaults to the schedule page. A
plugin that hides the item should also claim the homepage, or providers arrive on
a page they can no longer navigate back to.

The panel handler uses a different, already-released effect:
[`PanelConfiguration`](https://docs.canvasmedical.com/sdk/layout-effect/#panel-configuration).
`ProviderMenuConfiguration` governs the hamburger menu only. Note that the same
`PANEL_SECTIONS_CONFIGURATION` event fires for both the global panel and a
patient's panel — the patient one carries a target, and has no Appointments
section — so the handler returns no effect there rather than replacing a
patient's panel with global sections.

## How the allow-list behaves

The effect **replaces** the default set of menu items, so anything that should
stay visible has to be listed. Anything omitted disappears. Passing an empty list
is allowed and hides every native item, for a plugin that replaces the menu
entirely with its own items.

If no installed plugin emits the effect, the menu renders unchanged — the effect
is purely opt-in, and an instance without it sees no difference.

Two things the allow-list does not do:

- **It does not reorder the menu.** Items render in Canvas's native order and
  grouping regardless of the order you list them in.
- **It does not grant access.** Permissions still apply on top, so an item you
  allow-list will still render disabled for a user who lacks the permission for
  it.

Plugin-provided menu items (applications with the `provider_menu_item` scope) are
independent and unaffected by the allow-list.

Take care with `SETTINGS` and `MULTI_FACTOR_AUTHENTICATION`: omitting them hides
the links to `/admin` and to MFA enrollment.

## Available items

| Item                          | Menu label                 |
| ----------------------------- | -------------------------- |
| `SCHEDULE`                    | Schedule                   |
| `PATIENTS`                    | Patients                   |
| `REVENUE`                     | Revenue                    |
| `POPULATIONS`                 | Populations                |
| `CAMPAIGNS`                   | Campaigns                  |
| `DATA_INTEGRATION`            | Data integration           |
| `QUESTIONNAIRE_BUILDER`       | Questionnaire Builder      |
| `SETTINGS`                    | Settings                   |
| `MULTI_FACTOR_AUTHENTICATION` | Multi-Factor Authentication |
| `CHANGELOG`                   | Changelog                  |
| `HELP_CENTER`                 | Help center                |

The avatar and Sign out are always rendered and cannot be hidden.

## Trying it out

```sh
canvas install example_provider_menu_configuration
```

Open the hamburger menu: Schedule is gone, every other item is still there. On the
panel, the Appointments preset filter is gone and the rest are still there. Open a
patient's chart and confirm that patient's panel filters are untouched. Log out and
back in to land on the patients page instead of the schedule page. The `/schedule`
route still resolves if visited directly.

Uninstall to confirm the control case — the menu and the panel filters return to
their default shape, with Schedule and Appointments present.

### Important Note!

The CANVAS_MANIFEST.json is used when installing your plugin. Please ensure it
gets updated if you add, remove, or rename handlers.
