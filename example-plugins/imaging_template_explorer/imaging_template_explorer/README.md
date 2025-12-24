# Imaging Template Explorer Plugin

This example plugin demonstrates how to use the `ImagingReportTemplate` SDK data models to query and display imaging report template information.

## Features

### 1. Simple API Endpoint (`ImagingTemplateAPI`)

A REST endpoint at `/imaging-templates/<patient_id>` that allows querying imaging report templates.

#### Path Parameters

| Parameter | Description |
|-----------|-------------|
| `patient_id` | Patient ID (required) |

#### Query Parameters

| Parameter | Description |
|-----------|-------------|
| `search` | Search templates by keywords |
| `active` | Filter to active templates only (`true`/`false`) |
| `custom` | Filter to custom (user-created) templates only (`true`/`false`) |
| `builtin` | Filter to built-in templates only (`true`/`false`) |

#### Example Requests

The full URL format is: `/plugin-io/api/<plugin_name>/<handler_path>`

```bash
# List all templates for a patient
curl http://localhost:8000/plugin-io/api/imaging_template_explorer/imaging-templates/abc-123-patient-uuid

# Search for MRI templates
curl "http://localhost:8000/plugin-io/api/imaging_template_explorer/imaging-templates/abc-123-patient-uuid?search=MRI"

# Get only active templates
curl "http://localhost:8000/plugin-io/api/imaging_template_explorer/imaging-templates/abc-123-patient-uuid?active=true"

# Get only custom templates
curl "http://localhost:8000/plugin-io/api/imaging_template_explorer/imaging-templates/abc-123-patient-uuid?active=true&custom=true"

# Get built-in templates
curl "http://localhost:8000/plugin-io/api/imaging_template_explorer/imaging-templates/abc-123-patient-uuid?builtin=true"
```

#### Response Format

```json
{
    "patient_id": "abc-123-patient-uuid",
    "count": 2,
    "templates": [
        {
            "dbid": 1,
            "name": "CT, abdomen and pelvis",
            "long_name": "CT, abdomen and pelvis; with contrast",
            "code": "74176",
            "code_system": "CPT",
            "active": true,
            "custom": false,
            "rank": 10,
            "fields": [
                {
                    "dbid": 1,
                    "label": "Findings",
                    "code": "123456",
                    "type": "text",
                    "required": true,
                    "sequence": 1,
                    "options": []
                }
            ]
        }
    ]
}
```

### 2. Protocol Card (`ImagingTemplateProtocolCard`)

A protocol that displays imaging template statistics as a protocol card in the patient chart summary. The card shows:

- Total count of templates
- Count of active templates
- Count of custom templates
- Count of built-in templates
- List of top templates by rank

## SDK Models Used

This plugin demonstrates usage of the following SDK models:

- `ImagingReportTemplate` - Main template model
- `ImagingReportTemplateField` - Template field definitions
- `ImagingReportTemplateFieldOption` - Field options

### QuerySet Methods Demonstrated

- `active()` - Filter to active templates
- `search(query)` - Search by keywords
- `custom()` - Filter to custom templates
- `builtin()` - Filter to built-in templates
- `prefetch_related()` - Efficient loading of related fields and options

## Installation

1. Add the plugin to your Canvas instance
2. The API endpoint will be available at `/imaging-templates`
3. The protocol card will appear in patient chart summaries
