==========================
test_runtime_legacy_plugin
==========================

## Description

A plugin that loads cleanly under the current sandbox rules but whose helper
function only works under the deprecated ones, used to exercise the static
pre-check that picks the rule set before anything runs.

### Important Note!

The CANVAS_MANIFEST.json is used when installing your plugin. Please ensure it
gets updated if you add, remove, or rename handlers.
