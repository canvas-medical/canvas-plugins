Recurring Appointments Plugin
=============================

## Description

This plugin adds recurring appointment functionality to Canvas, allowing healthcare providers to automatically schedule follow-up appointments based on configurable recurrence patterns. When creating an appointment, users can select from daily, weekly, or monthly recurrence options, and the system will automatically generate the appropriate series of appointments.

## Features

- **Recurrence Options**: Support for daily, weekly, and monthly recurring appointments
- **Configurable Intervals**: Users can specify custom intervals (every 1-8 days/weeks/months)
- **Flexible End Conditions**: Configurable number of recurring appointments (default: 30)
- **Automatic Creation**: Automatically generates follow-up appointments when a recurring appointment is created
- **Appointment & Schedule Event Support**: Works with both regular appointments and schedule events
- **Parent-Child Relationship**: Maintains relationship between original appointment and recurring instances

## How It Works

1. **Form Enhancement**: Adds three configurable fields to appointment forms:
   - **Interval**: Dropdown to select frequency (every 1-8 units)
   - **Recurrence Type**: Dropdown with options: Day(s), Week(s), Month(s)
   - **End Condition**: Text field to specify number of appointments to create (default: 30)
2. **Automatic Processing**: When an appointment is created with a recurrence setting, the system automatically:
   - Detects the recurrence pattern from appointment metadata
   - Calculates future appointment dates based on the interval and type
   - Creates the specified number of child appointments or schedule events
   - Preserves all original appointment details (provider, location, duration, etc.)

## Technical Components

- `AppointmentFormFields`: Handler that adds three configurable form fields (interval, recurrence type, and end condition) to appointment forms
- `AppointmentRecurrence`: Handler that processes newly created appointments and generates recurring instances based on the configured recurrence pattern

## Recurrence Logic

The system now uses configurable parameters from the form fields:

- **Interval**: How often to repeat (1-8 units)
- **Recurrence Type**: The time unit (Day(s), Week(s), Month(s))
- **End Condition**: Total number of appointments to create (default: 30)

Examples:
- **Every 2 Days for 10 appointments**: Creates 10 appointments, each 2 days apart
- **Every 3 Weeks for 5 appointments**: Creates 5 appointments, each 3 weeks apart
- **Every 1 Month for 12 appointments**: Creates 12 appointments, each 1 month apart

### Important Note!

The CANVAS_MANIFEST.json is used when installing your plugin. Please ensure it gets updated if you add, remove, or rename handlers.
