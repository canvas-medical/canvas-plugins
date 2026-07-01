autocomplete_annotation_demo
============================

## Description

Attaches demo annotations to every **Diagnose** and **Assess Condition** search result, so
the command autocomplete annotation chips render on every result without needing any
specific data on the instance.

Use it to exercise the search-result annotation styling: open a note, add a **Diagnose**
(or **Assess**) command, and type a common term (e.g. `diabetes`) — each result shows the
demo annotation chips. Add or remove entries in the handler's `ANNOTATIONS` list to render
one chip or several.

### Important Note!

The CANVAS_MANIFEST.json is used when installing your plugin. Please ensure it
gets updated if you add, remove, or rename protocols.
