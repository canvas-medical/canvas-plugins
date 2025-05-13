supervising_provider_prescribe_protocol
=======================================

## Description

This protocol responds to the NOTE_STATE_CHANGE_EVENT_CREATED event.

It inserts a ProtocolCard containing a recommended Prescribe command. When the user triggers
this command, the supervising provider field will be automatically populated.

This plugin is primarily used to test and validate that the supervising provider is correctly
set during command initialization from a protocol.

### Important Note!

The CANVAS_MANIFEST.json is used when installing your plugin. Please ensure it
gets updated if you add, remove, or rename protocols.
