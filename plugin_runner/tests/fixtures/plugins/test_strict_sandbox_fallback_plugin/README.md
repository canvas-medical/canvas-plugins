==========================
test_strict_sandbox_fallback_plugin
==========================

## Description

A plugin whose module-level code the strict sandbox rejects and the
legacy-permissive sandbox accepts, used to exercise the plugin runner's fallback
path and its Sentry reporting.

### Important Note!

The CANVAS_MANIFEST.json is used when installing your plugin. Please ensure it
gets updated if you add, remove, or rename handlers.
