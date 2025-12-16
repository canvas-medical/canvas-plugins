# Plugin Specification: Simple Demo Plugin

## Overview
The simplest possible Canvas plugin demonstrating core functionality: responding to an event and displaying a banner alert.

## Purpose
Create a minimal working example that shows:
- How to handle Canvas events
- How to return effects to the Canvas UI
- Basic plugin structure and configuration

## Requirements

### Trigger
**Event Type:** `PATIENT_UPDATED`
- Fires when a patient record is updated
- Provides patient ID in the event target

### Action
**Effect Type:** `AddBannerAlert`
- Display a simple informational message in the patient timeline
- Message: "Hello from your demo plugin! This patient record was just updated."
- Intent: `info` (blue informational banner)
- Placement: Patient timeline

## Technical Specification

### Handler Type
`BaseProtocol` - Event-driven protocol handler

### Event Context
- Event: `PATIENT_UPDATED`
- Event target includes: Patient ID

### Effect Response
```python
AddBannerAlert(
    narrative="Hello from your demo plugin! This patient record was just updated.",
    intent=AddBannerAlert.Intent.INFO,
    placement=[AddBannerAlert.Placement.TIMELINE]
)
```

### Plugin Configuration
- Plugin name: `simple-demo-plugin`
- Package name: `simple_demo_plugin`
- Description: "A minimal demo plugin that displays a banner when a patient record is updated"
- Version: 0.1.0
- Implements protocol: `patient-updated`

## User Story
**As a** Canvas user
**I want** to see a banner message when a patient record is updated
**So that** I can verify the plugin is working correctly

## Acceptance Criteria
1. Plugin successfully deploys to Canvas instance
2. Updating any patient record triggers the plugin
3. A blue informational banner appears with the demo message
4. No errors appear in logs
5. Tests achieve 100% coverage

## Out of Scope
- Patient-specific logic or clinical decision support
- External API calls
- Database queries
- Complex business logic
- Task creation or other effects

## Implementation Notes
- Keep code minimal and well-commented
- Focus on clarity over features
- Serve as a template for future plugin development
- Include comprehensive tests for the handler
