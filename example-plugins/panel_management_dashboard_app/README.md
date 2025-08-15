Panel Management Dashboard Application
======================================

## Description

This is a demonstration application for Canvas that displays all patients and information about their last visit, including the care team member who attended to them and which insurance providers is available.

### Important Note!

There are some configurable settings via `SECRETS`.

- `INSURANCES`: A list of URLs to insurance provider logos to display in the patient dashboard.
- `PAGE_SIZE`: The number of patients to display per page in the dashboard.
- `ALERT_THRESHOLD_DAYS`: The number of days before a patient's last visit to define its warning level color.