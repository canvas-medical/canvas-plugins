# Specialty Report Explorer Plugin

This plugin provides a Simple API endpoint to explore and test SpecialtyReportTemplate, SpecialtyReportTemplateField, and SpecialtyReportTemplateFieldOption SDK models.

## SpecialtyReportTemplateAPI

A Simple API endpoint for querying SpecialtyReportTemplate data with associated fields and options.

**Path:** `/specialty-report-templates`

**Query Parameters:**

- `active`: Filter active templates

  - `true` - Active templates only

- `search`: Full-text search query

  - Search in template names and search_keywords field

- `custom`: Filter custom or builtin templates

  - `true` - Custom templates only

  - `false` - Builtin templates only

- `specialty_code`: Filter by specialty taxonomy code

  - Example: `207RC0000X` for Cardiology

  - Example: `207ND0100X` for Dermatology

- `include_fields`: Include field details (default: `false`)

  - `true` - Include fields array for each template

  - `false` - Exclude fields from response

- `include_options`: Include field options (default: `false`)

  - `true` - Include options array for each field (requires `include_fields=true`)

  - `false` - Exclude options from response

**Example Usage:**

```bash
# Get all templates
curl http://localhost:8000/plugin-io/api/speciality_report_explorer/specialty-report-templates

# Get active templates
curl http://localhost:8000/plugin-io/api/speciality_report_explorer/specialty-report-templates?active=true

# Search for templates
curl http://localhost:8000/plugin-io/api/speciality_report_explorer/specialty-report-templates?search=cardiology

# Filter by specialty code
curl http://localhost:8000/plugin-io/api/speciality_report_explorer/specialty-report-templates?specialty_code=207RC0000X

# Get builtin templates with fields
curl http://localhost:8000/plugin-io/api/speciality_report_explorer/specialty-report-templates?custom=false&include_fields=true

# Get templates with fields and options
curl http://localhost:8000/plugin-io/api/speciality_report_explorer/specialty-report-templates?include_fields=true&include_options=true

# Combined filters
curl http://localhost:8000/plugin-io/api/speciality_report_explorer/specialty-report-templates?active=true&specialty_code=207RC0000X&include_fields=true
```

**Example Response:**

```json
{
  "count": 1,
  "templates": [
    {
      "dbid": 1,
      "name": "Cardiology Consultation Report",
      "code": "TEST_CARD001",
      "code_system": "http://example.com/codes",
      "search_keywords": "cardiology cardiac heart cardiovascular",
      "active": true,
      "custom": false,
      "search_as": "cardiology",
      "specialty_name": "Cardiology",
      "specialty_code": "207RC0000X",
      "specialty_code_system": "http://nucc.org/provider-taxonomy",
      "fields": [
        {
          "dbid": 1,
          "sequence": 1,
          "code": "TEST_CC",
          "code_system": "http://loinc.org",
          "label": "Chief Complaint",
          "units": null,
          "type": "text",
          "required": true,
          "options": [
            {
              "dbid": 1,
              "label": "Normal",
              "key": "TEST_NORMAL"
            }
          ],
          "option_count": 1
        }
      ],
      "field_count": 1
    }
  ]
}
```

## SpecialtyReportTemplate Model

The SpecialtyReportTemplate model represents specialty consultation report templates used for LLM-powered specialty/referral report parsing.

### Fields

- `dbid` - Template ID (primary key)

- `name` - Template name

- `code` - Template code

- `code_system` - Code system URI

- `search_keywords` - Keywords for full-text search

- `active` - Whether the template is active

- `custom` - Whether the template is custom (vs. builtin)

- `search_as` - Alternative search term

- `specialty_name` - Name of the medical specialty

- `specialty_code` - Specialty taxonomy code (e.g., "207RC0000X")

- `specialty_code_system` - Specialty code system URI (e.g., "http://nucc.org/provider-taxonomy")

## SpecialtyReportTemplateField Model

The SpecialtyReportTemplateField model represents field definitions within a specialty report template.

### Fields

- `dbid` - Field ID (primary key)

- `sequence` - Display order of the field

- `code` - Field code (nullable)

- `code_system` - Code system URI

- `label` - Field label/name

- `units` - Measurement units (nullable)

- `type` - Field type (text, select, float, radio, checkbox, etc.)

- `required` - Whether the field is required

- `report_template_id` - Foreign key to SpecialtyReportTemplate

## SpecialtyReportTemplateFieldOption Model

The SpecialtyReportTemplateFieldOption model represents options for select/radio/checkbox fields.

### Fields

- `dbid` - Option ID (primary key)

- `label` - Option display label

- `key` - Option value key

- `field_id` - Foreign key to SpecialtyReportTemplateField

## Installation

```bash
canvas install speciality_report_explorer
```

## Testing

Comprehensive manual testing is available via a Python test script. See [TESTING.md](../TESTING.md) for detailed documentation.

**Quick Start:**
```bash
cd speciality_report_explorer
python tests/test_specialty_report_template_api_manual.py
```

The test script validates all query parameters, filter combinations, and edge cases.
