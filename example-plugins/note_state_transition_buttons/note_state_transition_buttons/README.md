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
When clicked, the handler calls the matching SDK method on the current note.

- **If the transition is valid for the note's current state and type**, the
  transition effect is returned alongside a `CustomCommand` originated on the
  same note with content like `Lock transition applied.`.
- **If the SDK rejects the call** (e.g. discharging a non-inpatient note,
  signing a note that doesn't require a signature, a state-matrix violation),
  the `pydantic.ValidationError` is caught and the error text is logged to the
  note via the same `CustomCommand` originator instead. The transition effect
  itself is dropped.

The logging command uses `schema_key = "note_state_transition_log"` and is
committed on origination so the message is immediately visible in the note
body. The schema key is plugin-local — it doesn't need to be registered
anywhere in Canvas.

## Installing

```bash
canvas install /path/to/note_state_transition_buttons
```

## Using it

1. Open any note. Eleven `Test: …` buttons appear in the footer.
2. Click one to attempt that transition. The note will gain a custom command
   with the outcome (success or validation error) — useful for verifying that
   the new `Delete` / `Undelete` / `Discharge` / `Revert` effects added in the
   parent PR behave as expected, and that the existing transitions still
   work.
