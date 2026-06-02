# Note state transition buttons

A test/demo plugin that adds a note-footer button for every Note and
Appointment state transition exposed by the SDK:

| Button             | SDK call                      | Allowed for                                    |
|--------------------|-------------------------------|------------------------------------------------|
| Lock               | `Note.lock()`                 | encounter / inpatient / base / appointment     |
| Unlock             | `Note.unlock()`               | locked notes                                   |
| Sign               | `Note.sign()`                 | locked notes whose type requires a signature   |
| Push charges       | `Note.push_charges()`         | billable encounter notes                       |
| Check in           | `Note.check_in()`             | appointment notes                              |
| No show            | `Note.no_show()`              | appointment notes                              |
| Delete             | `Note.delete()`               | encounter / inpatient / base notes             |
| Restore            | `Note.undelete()`             | deleted notes                                  |
| Discharge          | `Note.discharge()`            | inpatient notes                                |
| Cancel appointment | `Appointment.cancel()`        | booked / checked-in / reverted appointments    |
| Revert appointment | `Appointment.revert()`        | booked / checked-in appointments               |

## How it works

Each button is an `ActionButton` subclass with `BUTTON_LOCATION = NOTE_FOOTER`.
When clicked, the handler resolves the note from the `note_id` (db pk) passed
in the action button context, then calls the matching SDK method.

- **If the transition is valid for the note's current state and type**, the
  transition effect is returned and a success message is written to the
  plugin-runner log.
- **If the SDK rejects the call** (e.g. discharging a non-inpatient note,
  signing a note that doesn't require a signature, a state-matrix violation,
  or — for the appointment buttons — no appointment is associated with the
  note), the error is caught and logged. No effect is emitted.

All log lines are prefixed with `[NSTL]` so you can filter for them, e.g.:

```bash
docker logs home-app-web 2>&1 | grep '\[NSTL\]'
```

Logging is used in place of a `CustomCommand` originator because commands
cannot be inserted in many note states (locked, signed, deleted, etc.), but
log statements are always available.

## Installing

```bash
canvas install /path/to/note_state_transition_buttons
```

## Using it

1. Open any note. Eleven `Test: …` buttons appear in the footer.
2. Click one to attempt that transition.
3. Tail the plugin-runner logs (filtering on `[NSTL]`) to see the outcome —
   useful for verifying that the `Lock` / `Unlock` / `Sign` / `Push charges` /
   `Check in` / `No show` / `Delete` / `Undelete` / `Discharge` /
   `Cancel appointment` / `Revert appointment` effects behave as expected.
