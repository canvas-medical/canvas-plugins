# Staff Status Tracker Plugin

This plugin tracks staffing status changes for a clinic by implementing:

## Features

1. **Weekly Cron Job**: Runs every Monday at midnight to collect all staff data and their active/inactive status
2. **Event Handlers**: Listens for `STAFF_ACTIVATED` and `STAFF_DEACTIVATED` events to track real-time changes
3. **CSV Data Format**: Generates data in CSV format with columns:
   - timestamp
   - staff_id
   - first_name
   - last_name
   - email
   - status
   - previous_status
4. **Caching**: Stores CSV data in cache for 7 days

## Usage

The plugin automatically:
- Collects all staff data every Monday at midnight
- Tracks status changes when staff are activated or deactivated
- Maintains a history of status changes in CSV format
- Handles new staff members appropriately (null → active)
- Logs all changes and cached data

## Data Access

- **Read**: staff data
- **Events**: CRON, STAFF_ACTIVATED, STAFF_DEACTIVATED
- **Cache**: Uses Canvas caching system with 7-day retention

## Example Output

```csv
timestamp,staff_id,first_name,last_name,email,status,previous_status
2025-03-06T01:20:32.446Z,abc123,Jane,Doe,jane.doe@example.com,active,
2025-03-06T01:20:32.446Z,def456,Jon,Dowd,jon.dowd@example.com,inactive,
2025-03-10T22:47:16.221Z,abc123,Jane,Doe,jane.doe@example.com,inactive,active
2025-03-11T22:47:16.221Z,ghi789,Kristy,Klark,kristy.klark@example.com,active,null
```