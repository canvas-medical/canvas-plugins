# Coverage Metadata Sync Plugin

This Canvas EMR plugin automatically maintains a patient metadata field that reflects their insurance coverage status based on appointment label changes. It works in tandem with the **appointment_coverage_label** plugin to provide a complete coverage tracking solution.

## What This Plugin Does

This plugin monitors appointment label changes and automatically:

1. **Sets metadata to "Missing"** - When the "MISSING_COVERAGE" label is added to an appointment, the patient's `coverage_status` metadata is updated to "Missing"
2. **Sets metadata to "Active"** - When the "MISSING_COVERAGE" label is removed from an appointment, the patient's `coverage_status` metadata is updated to "Active"

## Why Use This Plugin

- **Centralized Coverage Status** - Maintains a single source of truth for patient coverage status in metadata
- **Easy Reporting** - Enables queries and reports based on coverage status metadata
- **Automated Synchronization** - No manual metadata updates required
- **Integration-Friendly** - Other systems can read the metadata field to understand coverage status
- **Audit Trail** - Metadata changes are tracked in Canvas, providing coverage status history

## How It Works

### Event-Driven Architecture

The plugin responds to appointment label events:

1. **APPOINTMENT_LABEL_ADDED** - Triggered when any label is added to an appointment
2. **APPOINTMENT_LABEL_REMOVED** - Triggered when any label is removed from an appointment

### Workflow: Label Added

When a label is added to an appointment:

```
1. Label added to appointment (could be any label)
2. Plugin checks: Is this the "MISSING_COVERAGE" label?
3. If YES:
   → Get patient ID from event context
   → Update patient metadata key "coverage_status" to value "Missing"
4. If NO (different label):
   → Ignore event, no action taken
```

### Workflow: Label Removed

When a label is removed from an appointment:

```
1. Label removed from appointment (could be any label)
2. Plugin checks: Is this the "MISSING_COVERAGE" label?
3. If YES:
   → Get patient ID from event context
   → Update patient metadata key "coverage_status" to value "Active"
4. If NO (different label):
   → Ignore event, no action taken
```

## Integration with appointment_coverage_label Plugin

This plugin is designed to work seamlessly with the **appointment_coverage_label** plugin:

### Complete Workflow Example

**Step 1: Appointment Created (No Coverage)**
- **appointment_coverage_label** detects new appointment for patient without insurance
- Adds "MISSING_COVERAGE" label to appointment

**Step 2: Label Added (This Plugin)**
- **coverage_metadata_sync** detects "MISSING_COVERAGE" label addition
- Updates patient metadata: `coverage_status = "Missing"`

**Step 3: Coverage Added Later**
- Patient's insurance information is entered into Canvas
- COVERAGE_CREATED event is fired

**Step 4: Label Removed**
- **appointment_coverage_label** removes "MISSING_COVERAGE" label from appointment
- **coverage_metadata_sync** detects label removal
- Updates patient metadata: `coverage_status = "Active"`

### Result
- Appointments are labeled appropriately
- Patient metadata accurately reflects current coverage status
- Both data points stay in sync automatically

## Example Scenarios

### Scenario 1: New Patient Without Insurance

**Initial State:**
- Patient John Doe, no insurance
- Appointment created for 2025-11-15

**Event Flow:**
1. Appointment created → **appointment_coverage_label** adds "MISSING_COVERAGE" label
2. Label added → **coverage_metadata_sync** sets metadata `coverage_status = "Missing"`

**Final State:**
- Appointment has "MISSING_COVERAGE" label
- Patient metadata shows `coverage_status: "Missing"`
- Reports can now identify patients needing coverage

### Scenario 2: Insurance Added

**Initial State:**
- Patient Jane Smith
- Metadata: `coverage_status = "Missing"`
- 3 appointments with "MISSING_COVERAGE" labels

**Event Flow:**
1. Insurance coverage added → COVERAGE_CREATED event fires
2. **appointment_coverage_label** removes labels from all 3 appointments
3. First label removed → **coverage_metadata_sync** sets `coverage_status = "Active"`
4. Subsequent label removals → **coverage_metadata_sync** updates same field (idempotent)

**Final State:**
- All appointments have labels removed
- Patient metadata shows `coverage_status: "Active"`
- Patient record is clean and up-to-date

### Scenario 3: Multiple Patients

**Scenario:**
- 100 patients without insurance
- Each has 1-3 appointments

**Plugin Behavior:**
- Each appointment creation triggers label addition
- Each label addition triggers metadata update
- All 100 patients have `coverage_status = "Missing"` in metadata
- Business intelligence reports can easily identify these patients
- Targeted outreach campaigns can be run based on metadata

## Technical Details

### Events Monitored
- **APPOINTMENT_LABEL_ADDED** - Any label added to appointments
- **APPOINTMENT_LABEL_REMOVED** - Any label removed from appointments

### Effects Generated
- **PatientMetadata.upsert()** - Creates or updates the `coverage_status` metadata field

### Metadata Field

**Key:** `coverage_status`

**Values:**
- `"Missing"` - Patient lacks insurance coverage (MISSING_COVERAGE label present)
- `"Active"` - Patient has insurance coverage (MISSING_COVERAGE label removed)

### Data Access
- **Read:** Event context (patient ID, label name)
- **Write:** Patient metadata

### Label Monitored
- **MISSING_COVERAGE** - The specific label that triggers metadata updates

### Error Handling

The plugin includes comprehensive error handling:
- Safely accesses event context with defensive checks
- Validates label name before processing
- Logs warnings for unexpected event types
- Catches exceptions during metadata effect creation
- Returns empty effect list on errors to prevent workflow interruption

### Performance Considerations

- Filters events early (ignores non-MISSING_COVERAGE labels)
- Single metadata operation per event
- Idempotent updates (safe to call multiple times)
- Minimal database queries
- Fast execution path for ignored events

## Setup

No configuration required - the plugin works automatically once installed:

1. Install the plugin using Canvas CLI
2. Enable the plugin in your Canvas instance
3. Optionally install **appointment_coverage_label** plugin for complete automation
4. The plugin will automatically monitor appointment label events

## Metadata Access

Once the plugin is running, you can access the coverage status metadata:

### Via Django ORM
```python
from canvas_sdk.v1.data.patient import Patient
from canvas_sdk.v1.data.patient_metadata import PatientMetadata

# Get patient
patient = Patient.objects.get(id="patient-id")

# Get coverage status metadata
metadata = PatientMetadata.objects.filter(
    patient=patient,
    key="coverage_status"
).first()

if metadata:
    print(f"Coverage status: {metadata.value}")
    # Output: "Coverage status: Missing" or "Coverage status: Active"
```

### For Reporting
```python
# Find all patients with missing coverage
missing_coverage = PatientMetadata.objects.filter(
    key="coverage_status",
    value="Missing"
).values_list("patient_id", flat=True)

# Find all patients with active coverage
active_coverage = PatientMetadata.objects.filter(
    key="coverage_status",
    value="Active"
).values_list("patient_id", flat=True)
```

## Logging

The plugin provides detailed logging for troubleshooting:

- **INFO** - Normal workflow events (metadata updates, event processing)
- **WARNING** - Skipped operations (non-MISSING_COVERAGE labels, unexpected events)
- **ERROR** - Exception handling (failed metadata effects)

Example log output:
```
INFO: Reacting to 'APPOINTMENT_LABEL_ADDED'. Updating patient abc123 metadata 'coverage_status' to 'Missing'.
INFO: Ignoring event for label 'URGENT' because it is not the monitored label ('MISSING_COVERAGE').
ERROR: Failed to create PatientMetadata effect for patient xyz789: [error details]
```

## Code Structure

```
coverage_metadata_sync/
├── CANVAS_MANIFEST.json          # Plugin configuration
├── README.md                      # This file
├── __init__.py                    # Package initializer
└── protocols/
    ├── __init__.py                # Protocol package initializer
    └── metadata_sync.py           # Main protocol implementation
```

### Key Components

- **CoverageStatusSyncProtocol** - Main protocol class handling label events
- **compute()** - Event routing and metadata update logic
- **MONITORED_LABEL** - Constant defining which label triggers updates ("MISSING_COVERAGE")
- **METADATA_KEY** - Constant defining metadata field name ("coverage_status")

## Troubleshooting

### Metadata Not Being Updated

**Possible Causes:**
- Plugin not enabled in Canvas instance
- Label change events not firing
- Different label being used (not "MISSING_COVERAGE")

**Check:**
- Verify plugin is installed and enabled
- Confirm label events are being generated in Canvas
- Review plugin logs for event processing messages
- Ensure label name exactly matches "MISSING_COVERAGE"

### Metadata Shows Wrong Value

**Possible Causes:**
- Label was added/removed outside of normal workflow
- Multiple conflicting label events
- Race condition with multiple appointments

**Check:**
- Review event logs for sequence of label changes
- Verify most recent label event for patient
- Check if patient has multiple appointments with different label states

### Integration Issues

**Problem:** Plugin works but labels aren't being added/removed

**Solution:** This plugin only RESPONDS to label changes. Install the **appointment_coverage_label** plugin to automatically manage labels.

## Important Notes

- This plugin only monitors the "MISSING_COVERAGE" label - other labels are ignored
- Metadata updates are idempotent - repeated updates to same value are safe
- The `coverage_status` field is created automatically if it doesn't exist
- Works best when paired with **appointment_coverage_label** plugin
- Metadata field can be customized by changing `METADATA_KEY` constant in code

## Best Practices

1. **Deploy Both Plugins Together** - Use with **appointment_coverage_label** for complete automation
2. **Monitor Logs Initially** - Watch logs after deployment to verify correct operation
3. **Include in Reports** - Leverage metadata field in coverage reporting dashboards
4. **Document Metadata Field** - Inform staff about `coverage_status` field availability
5. **Test Before Production** - Verify in staging environment with test appointments

---

**Plugin Version:** 1.0.0  
**SDK Version:** 0.1.4  
**License:** UNLICENSED
