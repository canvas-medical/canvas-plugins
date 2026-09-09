click_to_dial
=============

## Description

Demonstrates `PhoneDialConfiguration`, the effect that decides which chart phone
numbers are clickable and who dials them, and `PHONE_NUMBER_CLICKED`, the event a
click emits.

Two handlers:

- `ClickToDialConfiguration` responds to `PHONE_DIAL__GET_CONFIGURATION` and
  returns two effects. The first makes the patient's own numbers and their
  contacts clickable with `PLUGIN` handling; the second makes external care team
  numbers clickable with `DEVICE` handling.
- `PlaceCall` responds to `PHONE_NUMBER_CLICKED`. It dials a contact through Zoom
  with a `RedirectEffect`, and records a click on the patient's own numbers
  without dialing anything.

## The two handling modes

- `DEVICE` renders a `tel:` link, so a click reaches whatever the device registers
  as its phone app. The plugin is not involved.
- `PLUGIN` renders a link that opens nothing locally, so the click reaches the
  plugin and the handler decides what happens.

`PHONE_NUMBER_CLICKED` fires under **both** modes, carrying `phone_number` and the
`source` section. `PlaceCall` dials every click it receives, so the external care
team numbers left to the device are dialed twice: once by the phone app and once
by Zoom. A plugin that wants to dial only some sections reads `source` and returns
nothing for the rest.

## Dialing through a softphone

A `PLUGIN` section is dialed by returning a `RedirectEffect` whose URL is the
softphone's own scheme:

```python
RedirectEffect(
    url="zoomus://zoom.us/call?number=3471111234",
    target=RedirectEffect.TargetType.SAME_TAB,
).apply()
```

Two things to know about that:

- **`SAME_TAB` is the only usable target.** The redirect arrives over a
  subscription rather than inside the click, so opening a new tab would be
  popup-blocked. `SAME_TAB` hands the scheme to the OS and leaves the chart in
  place.
- **The URL must be allowlisted.** Every redirect is checked server-side against
  the plugin's `REDIRECT_ALLOWLIST_EXTERNAL` secret. An unset allowlist denies
  everything, and a blocked redirect logs a warning naming the key rather than
  failing visibly, so the click appears to do nothing.

This only works for URL-like schemes, meaning ones with a `//` authority:
`zoomus://`, `msteams://`, `rcmobile://`, `https://`. The allowlist requires both
a scheme and a host, so a scheme-only URI is rejected before it is even checked.
That rules out the standard telephony URIs, which are identifiers rather than
URLs and carry no authority: `sip:`, `callto:`, `skype:`, `sms:`. `tel:` is
unaffected, since `DEVICE` handles it without a redirect.

## Setup

```sh
canvas install click_to_dial --secret REDIRECT_ALLOWLIST_EXTERNAL='zoomus://zoom.us/call'
```

The allowlist is newline-delimited, one entry per line, and matches at a path
boundary: `zoomus://zoom.us/call` covers
`zoomus://zoom.us/call?number=3471111234`.

## What the configuration governs

Click-to-dial is plugin-driven, and Canvas ships no setting for it, so a section
no plugin lists renders its phone numbers as plain text. That is also the behavior
of an instance with this plugin uninstalled.

The three sections are `PATIENT` (the patient header and their telecom entries),
`CONTACT` (patient contacts), and `EXTERNAL_CARE_TEAM` (external care team members
in the chart and on the profile). Fax numbers are always plain text.

Where several installed plugins respond, a section is clickable when any of them
lists it, and it is plugin-driven when any of them asks for `PLUGIN` handling,
since opening the device's phone app alongside a plugin that places the call
itself would dial the number twice.

## Trying it out

Open a patient's chart. Every phone number is clickable and any fax number stays
plain text. Clicking the patient's own number hands the call to Zoom; so does a
contact, through its "Dial number with Zoom" button. An external care team number
opens the device's phone app and hands the call to Zoom as well, because this
plugin dials every click it receives.

Uninstall to confirm the control case: every number renders as plain text again.

### Important Note!

The CANVAS_MANIFEST.json is used when installing your plugin. Please ensure it
gets updated if you add, remove, or rename handlers.
