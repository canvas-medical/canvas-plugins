# Abnormal Lab Task Notification Plugin

This plugin monitors incoming lab reports and automatically creates task notifications for any abnormal lab values, ensuring they are flagged for prompt clinical review.

## Features

- Monitors `LAB_REPORT_CREATED` events
- Checks lab values for abnormal flags
- Creates tasks with appropriate priority for abnormal results
- Includes details about the abnormal values in the task
- Filters out test-only and junked lab reports

## How It Works

1. When a new lab report is created, the plugin is triggered
2. The plugin examines all lab values in the report
3. For any lab value with an `abnormal_flag`, it collects the details
4. If abnormal values are found, a task is created with:
   - Clear title indicating the number of abnormal values
   - "abnormal-lab" and "urgent-review" labels for easy filtering
   - Link to the original lab report
   - Details about each abnormal value including reference ranges

## Configuration

This plugin requires no additional configuration. It automatically monitors all lab reports and creates tasks as needed.

## Technical Implementation

The plugin uses the Canvas SDK's protocol system to:

1. **Event Handling**: Registers for `LAB_REPORT_CREATED` events using the `RESPONDS_TO` mechanism
2. **Data Access**: Queries lab reports and their associated lab values using Django ORM
3. **Abnormal Detection**: Checks the `abnormal_flag` field of each lab value for non-empty values
4. **Task Creation**: Uses the `AddTask` effect to create tasks in the Canvas system
5. **Error Handling**: Includes proper exception handling and logging for debugging

### Safety Features

- Filters out test-only reports (`for_test_only=True`)
- Filters out junked reports (`junked=True`)  
- Handles missing or null abnormal flags gracefully
- Includes comprehensive error logging
- Validates patient association before creating tasks

### Data Fields Used

From `LabReport`:
- `patient_id`: Links the task to the correct patient
- `for_test_only`: Used to filter out test reports
- `junked`: Used to filter out invalid reports

From `LabValue`:
- `abnormal_flag`: Primary field for detecting abnormal values
- `value`: Lab result value for task details
- `units`: Measurement units for task details  
- `reference_range`: Normal ranges for task details

## Task Details

Created tasks include:
- **Title**: "Review Abnormal Lab Values (N abnormal)" where N is the count
- **Labels**: ["abnormal-lab", "urgent-review"]
- **Status**: OPEN
- **Patient**: Linked to the patient associated with the lab report
- **Linked Object**: References the original lab report

## Example

When a lab report contains abnormal values like:
- High glucose: 180 mg/dL (ref: 70-100)
- Low hemoglobin: 9.2 g/dL (ref: 12-16)

The plugin creates a task titled "Review Abnormal Lab Values (2 abnormal)" with details about each abnormal finding.