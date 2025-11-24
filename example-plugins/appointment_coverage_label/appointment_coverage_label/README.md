# Appointment Coverage Label Plugin

This Canvas EMR plugin automatically manages appointment labels based on patient insurance coverage status, ensuring that appointments for patients without coverage are clearly flagged for staff attention.

## What This Plugin Does

This plugin monitors patient insurance coverage and automatically:

1. **Adds "MISSING_COVERAGE" labels** - When an appointment is created for a patient without insurance coverage, all of that patient's appointments receive the "MISSING_COVERAGE" label
2. **Removes "MISSING_COVERAGE" labels** - When insurance coverage is added for a patient, the "MISSING_COVERAGE" label is automatically removed from all of that patient's appointments

## Why Use This Plugin

- **Proactive Coverage Management** - Immediately flags appointments that need insurance verification
- **Automated Workflow** - No manual label management required
- **Consistent Flagging** - Ensures all appointments for a patient reflect their current coverage status
- **Better Patient Care** - Helps staff identify and resolve coverage issues before appointments
- **Financial Risk Reduction** - Reduces risk of uncompensated care by highlighting coverage gaps

## How It Works

### Event-Driven Architecture

The plugin responds to two key Canvas events:

1. **APPOINTMENT_CREATED** - Triggered whenever a new appointment is scheduled
2. **COVERAGE_CREATED** - Triggered when insurance coverage is added for a patient

### Workflow: Adding Labels

When an appointment is created:

```
1. New appointment created for Patient X
2. Plugin checks: Does Patient X have insurance coverage?
3. If NO coverage found:
   → Query all appointments for Patient X
   → Filter to appointments without "MISSING_COVERAGE" label
   → Add "MISSING_COVERAGE" label to all matching appointments
4. If coverage exists:
   → No action taken
```

### Workflow: Removing Labels

When coverage is added:

```
1. Insurance coverage added for Patient Y
2. Plugin queries all appointments for Patient Y
3. Filter to appointments WITH "MISSING_COVERAGE" label
4. Remove "MISSING_COVERAGE" label from all matching appointments
```

## Example Scenarios

### Scenario 1: New Patient Without Insurance

**Initial State:**
- Patient John Doe has no insurance coverage
- Appointment scheduled for 2025-11-15

**Plugin Action:**
- Detects appointment creation
- Checks coverage → None found
- Adds "MISSING_COVERAGE" label to appointment

**Result:**
- Appointment now flagged for insurance verification
- Staff can proactively contact patient before appointment

### Scenario 2: Insurance Added Later

**Initial State:**
- Patient Jane Smith has 3 appointments with "MISSING_COVERAGE" labels
- Coverage was just added to her account

**Plugin Action:**
- Detects coverage creation
- Queries all Jane's appointments with "MISSING_COVERAGE" label
- Removes label from all 3 appointments

**Result:**
- Appointments no longer flagged
- Clean patient record reflects current coverage status

### Scenario 3: Multiple Appointments

**Initial State:**
- Patient has no coverage
- First appointment created on 2025-11-01

**Plugin Action (First Appointment):**
- Adds "MISSING_COVERAGE" label to first appointment

**Later:**
- Second appointment created on 2025-11-10 for same patient

**Plugin Action (Second Appointment):**
- Detects no coverage still
- Adds "MISSING_COVERAGE" label to BOTH appointments

**Result:**
- All appointments consistently flagged until coverage is added

## Technical Details

### Events Monitored
- **APPOINTMENT_CREATED** - New appointment scheduling
- **COVERAGE_CREATED** - Insurance coverage addition

### Effects Generated
- **AddAppointmentLabel** - Adds "MISSING_COVERAGE" label to appointments
- **RemoveAppointmentLabel** - Removes "MISSING_COVERAGE" label from appointments

### Data Access
- **Read:** Patient, Coverage, Appointment models
- **Write:** Appointment labels

### Label Used
- **MISSING_COVERAGE** - Standard label applied to appointments without patient coverage

### Error Handling

The plugin includes comprehensive error handling:
- Gracefully handles missing patient records
- Logs warnings when patients are not found
- Catches and logs exceptions during effect creation
- Returns empty effect list on errors to prevent workflow interruption

### Performance Considerations

- Uses Django ORM `prefetch_related` for efficient label queries
- Filters appointments efficiently using database indexes
- Processes only relevant appointments (not entire database)
- Minimal overhead on appointment creation workflow

## Integration with Other Plugins

This plugin works seamlessly with the **coverage_metadata_sync** plugin:

1. **appointment_coverage_label** manages appointment labels
2. **coverage_metadata_sync** listens for label changes and updates patient metadata
3. Together they provide a complete coverage tracking solution

## Setup

No configuration required - the plugin works automatically once installed:

1. Install the plugin using Canvas CLI
2. Enable the plugin in your Canvas instance
3. The plugin will automatically monitor appointment and coverage events

## Logging

The plugin provides detailed logging for troubleshooting:

- **INFO** - Normal workflow events (appointments processed, labels added/removed)
- **WARNING** - Skipped operations (patient not found, no appointments to update)
- **ERROR** - Exception handling (failed effect creation)

Example log output:
```
INFO: Handling APPOINTMENT_CREATED for patient abc123
INFO: Patient abc123 has no coverage. Checking appointments for labeling.
INFO: Found 2 appointments to label for patient abc123.
INFO: Creating AddAppointmentLabel effect for appointment xyz789
```

## Code Structure

```
appointment_coverage_label/
├── CANVAS_MANIFEST.json          # Plugin configuration
├── README.md                      # This file
├── __init__.py                    # Package initializer
└── protocols/
    ├── __init__.py                # Protocol package initializer
    └── appointment_labels.py      # Main protocol implementation
```

### Key Components

- **AppointmentLabelsProtocol** - Main protocol class handling both events
- **handle_coverage_created()** - Removes labels when coverage is added
- **handle_appointment_created()** - Adds labels when appointments are created for patients without coverage
- **compute()** - Routes events to appropriate handlers

## Troubleshooting

### Labels Not Being Added

**Possible Causes:**
- Plugin not enabled in Canvas instance
- Patient already has coverage
- Appointment already has "MISSING_COVERAGE" label

**Check:**
- Verify plugin is installed and enabled
- Confirm patient has no Coverage records
- Review plugin logs for error messages

### Labels Not Being Removed

**Possible Causes:**
- Coverage not properly saved to database
- Coverage record doesn't match patient
- Plugin event handler not triggered

**Check:**
- Verify Coverage.objects.filter(patient=patient).exists() returns True
- Check that coverage is associated with correct patient
- Review Canvas event logs for COVERAGE_CREATED events

## Important Notes

- The plugin applies labels to ALL of a patient's appointments, not just the newly created one
- Labels are managed automatically - manual label changes may be overwritten
- The "MISSING_COVERAGE" label is a standard label name - ensure it exists in your Canvas instance
- This plugin is designed to work alongside existing appointment workflows

---

**Plugin Version:** 1.0.0  
**SDK Version:** 0.1.4  
**License:** UNLICENSED
