missing_coverage_label
======================

## Description

This plugin provides a reference implementation for managing appointment labels within the Canvas SDK. It demonstrates an end-to-end workflow for automatically adding and removing a "MISSING_COVERAGE" label based on a patient's insurance coverage status.

The core logic is contained within the `AppointmentLabelsProtocol`, which listens for two key events:
- **`APPOINTMENT_CREATED`**: When an appointment is created, the protocol checks if the patient has insurance coverage. If not, it uses the `AddAppointmentLabel` effect to add the "MISSING_COVERAGE" label.
- **`COVERAGE_CREATED`**: When insurance coverage is added for a patient, the protocol uses the `RemoveAppointmentLabel` effect to clean up and remove the "MISSING_COVERAGE" label, ensuring it's no longer present.

This plugin serves as a practical example for developers looking to implement their own event-driven logic using the SDK's label management effects.

### Important Note!
# ... existing code ...

### Important Note!

The CANVAS_MANIFEST.json is used when installing your plugin. Please ensure it
gets updated if you add, remove, or rename protocols.
