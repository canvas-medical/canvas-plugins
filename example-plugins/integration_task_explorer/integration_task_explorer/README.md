# Integration Task Explorer Plugin

This plugin provides a Simple API endpoint to explore and test IntegrationTask and IntegrationTaskReview SDK models.

## IntegrationTaskAPI

A Simple API endpoint for querying IntegrationTask data with associated reviews.

**Path:** `/integration-tasks/<patient_id>`

**Query Parameters:**
- `status`: Filter by status
  - `unread` - Unread tasks
  - `pending_review` - Tasks pending review (UNREAD or READ)
  - `processed` - Processed tasks (PROCESSED or REVIEWED)
  - `errors` - Tasks with errors (ERROR or UNREAD_ERROR)
  - `junked` - Junked tasks
  - `not_junked` - Non-junked tasks
- `channel`: Filter by channel
  - `fax` - Fax tasks
  - `uploads` - Document upload tasks
  - `integration_engine` - Tasks from integration engine
  - `patient_portal` - Tasks from patient portal
- `include_reviews`: Include review details (default: `true`)
  - `true` - Include reviews array for each task
  - `false` - Exclude reviews from response

**Example Usage:**
```bash
# Get all tasks for a patient with reviews (use patient key/UUID, not integer ID)
curl http://localhost:8000/plugin-io/api/integration_task_explorer/integration-tasks/d8a61b507d2044fd8070dbcb2738418b

# Get unread fax tasks with reviews
curl http://localhost:8000/plugin-io/api/integration_task_explorer/integration-tasks/d8a61b507d2044fd8070dbcb2738418b?status=unread&channel=fax

# Get all tasks with errors
curl http://localhost:8000/plugin-io/api/integration_task_explorer/integration-tasks/d8a61b507d2044fd8070dbcb2738418b?status=errors

# Get all tasks without reviews (faster response)
curl http://localhost:8000/plugin-io/api/integration_task_explorer/integration-tasks/d8a61b507d2044fd8070dbcb2738418b?include_reviews=false

# Get all tasks (not patient-specific)
curl http://localhost:8000/plugin-io/api/integration_task_explorer/integration-tasks/all
```

**Note:** The `patient_id` parameter must be the patient's UUID key (e.g., `d8a61b507d2044fd8070dbcb2738418b`), not the internal database integer ID.

**Example Response:**
```json
{
  "patient_id": "d8a61b507d2044fd8070dbcb2738418b",
  "count": 1,
  "tasks": [
    {
      "id": 1,
      "status": "PRO",
      "type": "",
      "title": "Document Title",
      "channel": "document_upload",
      "patient_id": "d8a61b507d2044fd8070dbcb2738418b",
      "service_provider_id": null,
      "is_fax": false,
      "is_pending": false,
      "is_processed": true,
      "has_error": false,
      "is_junked": false,
      "created": "2025-12-19 10:42:43.644643+00:00",
      "modified": "2025-12-19 10:51:50.768209+00:00",
      "reviews": [
        {
          "id": 1,
          "template_name": "Lab Report Template",
          "document_key": "abc123",
          "reviewer_id": 5,
          "team_reviewer_id": null,
          "junked": false,
          "is_active": true,
          "created": "2025-12-19 10:45:00.000000+00:00",
          "modified": "2025-12-19 10:45:00.000000+00:00"
        }
      ],
      "review_count": 1
    }
  ]
}
```

## IntegrationTask Model

The IntegrationTask model represents incoming documents that need processing:
- Faxes
- Document uploads
- Lab results
- Patient portal submissions

### Status Values
- `UNREAD` (UNR) - New, unread task
- `UNREAD_ERROR` (UER) - Unread task with error
- `READ` (REA) - Task has been read
- `ERROR` (ERR) - Task has error
- `PROCESSED` (PRO) - Task has been processed
- `REVIEWED` (REV) - Task has been reviewed
- `JUNK` (JUN) - Task marked as junk

### Channel Values
- `fax` - Fax
- `document_upload` - Document Upload
- `from_integration_engine` - From Integration Engine
- `from_patient_portal` - From Patient Portal

## IntegrationTaskReview Model

The IntegrationTaskReview model represents a review assignment for an integration task.

### Fields
- `id` - Review ID
- `task_id` - Associated IntegrationTask ID
- `template_name` - Name of the template used for parsing
- `document_key` - Key identifying the parsed document
- `reviewer_id` - Staff ID of the assigned reviewer
- `team_reviewer_id` - Team ID if assigned to a team
- `junked` - Whether the review has been junked
- `is_active` - True if review is not junked

## Installation

```bash
canvas install integration_task_explorer
```
