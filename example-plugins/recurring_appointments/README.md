Recurring Appointments Plugin
=============================

## Description

This plugin adds recurring appointment functionality to Canvas, allowing healthcare providers to automatically schedule follow-up appointments based on configurable recurrence patterns. When creating an appointment, users can select from daily, weekly, or monthly recurrence options, and the system will automatically generate the appropriate series of appointments.

## Features

- **Recurrence Options**: Support for daily, weekly, and monthly recurring appointments
- **Automatic Creation**: Automatically generates follow-up appointments when a recurring appointment is created
- **Flexible Scheduling**: 
  - Daily recurrence: Creates appointments for the next 60 days
  - Weekly recurrence: Creates appointments for the next 8 weeks (2 months)
  - Monthly recurrence: Creates appointments for the next 2 months
- **Appointment & Schedule Event Support**: Works with both regular appointments and schedule events
- **Parent-Child Relationship**: Maintains relationship between original appointment and recurring instances

## How It Works

1. **Form Enhancement**: Adds a "Recurrence" dropdown field to appointment forms with options: None, Daily, Weekly, Monthly
2. **Automatic Processing**: When an appointment is created with a recurrence setting, the system automatically:
   - Detects the recurrence pattern from appointment metadata
   - Calculates future appointment dates based on the pattern
   - Creates child appointments or schedule events linked to the parent appointment
   - Preserves all original appointment details (provider, location, duration, etc.)

## Technical Components

- `AppointmentFormFields`: Handler that adds the recurrence dropdown field to appointment forms
- `AppointmentRecurrence`: Handler that processes newly created appointments and generates recurring instances based on the selected recurrence pattern

## Recurrence Logic

- **Daily**: Creates 60 follow-up appointments (one for each day over 2 months)
- **Weekly**: Creates 8 follow-up appointments (one per week over 2 months) 
- **Monthly**: Creates 2 follow-up appointments (one per month over 2 months)

### Important Note!

The CANVAS_MANIFEST.json is used when installing your plugin. Please ensure it gets updated if you add, remove, or rename handlers.
