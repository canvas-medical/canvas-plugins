==============================
Note Body Automation Plugin
==============================

A Canvas plugin that adds two plugin automations to the note body. The
automations show when the user types ``/`` in the note body, next to the native
commands. A plug icon marks them as plugin automations.

## Structure

```
note_body_automation_plugin/
├── handlers/
├── CANVAS_MANIFEST.json
└── README.md
```

## Features

- **Patient summary** — opens a modal in the right chart pane.
- **Follow-up plan** — adds a Plan command with a follow-up narrative. This
  automation shows in encounter notes only, to show how ``visible`` scopes an
  automation by note type.

## How it works

Canvas asks each plugin for its automation list one time per note load, then
filters the list in the browser as the user types. Canvas does not call the
plugin for each keystroke.

Canvas calls ``handle`` when the user selects the automation. ``handle`` can
return any effect.

## Line position

A command from ``handle`` lands on the line that the user typed on, and takes
that line over. The typed text becomes the command, the way a native command
does. Call ``originate`` with no ``line_number`` to get this.

The line is on the handler as ``self.line_number``. Give it to ``originate`` to
put the command somewhere else, and Canvas keeps the line you ask for:

```python
def handle(self) -> list[Effect]:
    return [
        PlanCommand(note_uuid=..., narrative="...").originate(
            line_number=self.line_number + 1
        )
    ]
```
