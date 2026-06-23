# note_header_assignee_options

Demonstrates controlling the note header **assignee** dropdown (the "Assigned to" control
in the top-right of a note header) from a plugin.

The handler responds to `PATIENT_NOTE_HEADER_ASSIGNEE__POST_SEARCH`, which fires with the
candidate assignees in `event.context["results"]` — a list of `{"id", "type", "label"}`
entries where `type` is `"staff"` or `"team"`. It returns a `NoteHeaderAssigneeOptions`
effect whose `options` list **replaces** the dropdown contents:

- **Reorder** — the dropdown shows the options in the order you return them. This example
  surfaces every team before any individual staff member.
- **Hide** — any candidate you omit from the returned list is removed from the dropdown.
  The built-in "Unassigned" options are always available regardless.

```python
return [
    NoteHeaderAssigneeOptions(
        options=[
            AssigneeOption(id=candidate["id"], type=AssigneeType(candidate["type"]))
            for candidate in reordered_and_filtered_candidates
        ]
    ).apply()
]
```
