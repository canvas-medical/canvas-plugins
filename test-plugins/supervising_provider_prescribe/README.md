supervising_provider_prescribe
==============================

## Description

This protocol responds to the PRESCRIBE_COMMAND__POST_ORIGINATE event.

It is used to test whether the supervising provider field is automatically populated
when the Prescribe command is triggered. The protocol reacts to the command's creation
and sets the field accordingly.

The same logic can be tested for Refill and Adjust Prescription commands by updating
the RESPONDS_TO event and the command class.

### Important Note!

The CANVAS_MANIFEST.json is used when installing your plugin. Please ensure it
gets updated if you add, remove, or rename protocols.
