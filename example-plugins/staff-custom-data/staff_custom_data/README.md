staff-custom-data
=================

## Description

A plugin for storing and managing extended staff profile data using the PluginData API. Demonstrates custom JSONB storage with filtering capabilities.

## Data Model

Staff data is stored per staff member with the following structure:

```json
{
    "biography": "Markdown formatted biography text",
    "specialties": ["Cardiology", "Internal Medicine"],
    "languages": ["English", "Spanish"],
    "years_of_experience": 15,
    "accepting_new_patients": true
}
```

| Field | Type | Description |
|-------|------|-------------|
| `biography` | string | Staff member's bio (supports markdown) |
| `specialties` | string[] | Medical specialties |
| `languages` | string[] | Languages spoken |
| `years_of_experience` | integer | Years in practice |
| `accepting_new_patients` | boolean | Currently accepting new patients |

## API Endpoints

Base path: `/plugin-io/api/staff_custom_data`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/staff/` | List all staff data (with filtering) |
| GET | `/staff/{uuid}/` | Get data for a single staff member |
| PUT | `/staff/{uuid}/` | Update staff data (partial updates supported) |

## Filtering

The list endpoint supports query parameters for filtering:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `specialty` | Filter by specialty (case-insensitive, partial match) | `?specialty=cardio` |
| `language` | Filter by language spoken | `?language=spanish` |
| `accepting_new_patients` | Filter by availability | `?accepting_new_patients=true` |
| `min_experience` | Minimum years of experience | `?min_experience=10` |

Filters can be combined: `?specialty=cardio&language=spanish&accepting_new_patients=true`

## Usage Examples

### Create/Update staff data (PUT)

Updates are merged with existing data - you only need to send the fields you want to change.

```bash
curl -X PUT "https://your-instance/plugin-io/api/staff_custom_data/staff/abc-123-def/" \
  -H "Content-Type: application/json" \
  -d '{
    "biography": "## Dr. Smith\n\nBoard certified cardiologist with 15 years of experience.",
    "specialties": ["Cardiology", "Internal Medicine"],
    "languages": ["English", "Spanish"],
    "years_of_experience": 15,
    "accepting_new_patients": true
  }'
```

**Response (200 OK):**
```json
{
    "message": "Staff data updated",
    "staff_uuid": "abc-123-def",
    "biography": "## Dr. Smith\n\nBoard certified cardiologist with 15 years of experience.",
    "specialties": ["Cardiology", "Internal Medicine"],
    "languages": ["English", "Spanish"],
    "years_of_experience": 15,
    "accepting_new_patients": true
}
```

### Partial update (PUT)

Update only specific fields - other fields are preserved:

```bash
curl -X PUT "https://your-instance/plugin-io/api/staff_custom_data/staff/abc-123-def/" \
  -H "Content-Type: application/json" \
  -d '{"accepting_new_patients": false}'
```

### Get single staff data (GET)

```bash
curl "https://your-instance/plugin-io/api/staff_custom_data/staff/abc-123-def/"
```

**Response (200 OK):**
```json
{
    "staff_uuid": "abc-123-def",
    "biography": "## Dr. Smith\n\nBoard certified cardiologist with 15 years of experience.",
    "specialties": ["Cardiology", "Internal Medicine"],
    "languages": ["English", "Spanish"],
    "years_of_experience": 15,
    "accepting_new_patients": false
}
```

### List all staff data (GET)

```bash
curl "https://your-instance/plugin-io/api/staff_custom_data/staff/"
```

**Response (200 OK):**
```json
{
    "staff": [
        {
            "staff_uuid": "abc-123-def",
            "biography": "## Dr. Smith\n\nBoard certified cardiologist.",
            "specialties": ["Cardiology", "Internal Medicine"],
            "languages": ["English", "Spanish"],
            "years_of_experience": 15,
            "accepting_new_patients": true
        },
        {
            "staff_uuid": "xyz-789-ghi",
            "biography": "## Dr. Jones\n\nFamily medicine specialist.",
            "specialties": ["Family Medicine", "Pediatrics"],
            "languages": ["English"],
            "years_of_experience": 8,
            "accepting_new_patients": true
        }
    ],
    "count": 2
}
```

### List with filters (GET)

Find Spanish-speaking cardiologists with 10+ years experience who are accepting patients:

```bash
curl "https://your-instance/plugin-io/api/staff_custom_data/staff/?specialty=cardio&language=spanish&min_experience=10&accepting_new_patients=true"
```

## Data Storage

This plugin uses the `PluginData` API for JSONB storage with:
- Automatic plugin isolation (each plugin can only access its own data)
- Shallow merge on updates (via PostgreSQL's `||` operator)
- Row-Level Security enforcement at the database level
