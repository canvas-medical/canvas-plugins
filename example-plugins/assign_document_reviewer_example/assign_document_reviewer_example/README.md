# Assign Document Reviewer Example

Example plugin demonstrating the `ASSIGN_DOCUMENT_REVIEWER` effect.

## Overview

This plugin shows how to use the `AssignDocumentReviewer` effect to automatically
assign staff members or teams as reviewers to documents in the Data Integration queue.

## Effect Usage

```python
from canvas_sdk.effects.data_integration import (
    AssignDocumentReviewer,
    Priority,
    ReviewMode,
)

# Assign a reviewer with all options
effect = AssignDocumentReviewer(
    document_id="12345",                    # Required: IntegrationTask ID (str or int)
    reviewer_id="staff-key",                # Optional: Staff member to assign
    team_id="team-uuid",                    # Optional: Team to assign
    priority=Priority.HIGH,                 # normal or high (default: normal)
    review_mode=ReviewMode.REVIEW_REQUIRED, # review_required, already_reviewed, or review_not_required
    annotations=[                           # Optional: display annotations for prefill
        {"text": "Team lead", "color": "#4CAF50"},
        {"text": "Primary care", "color": "#2196F3"},
    ],
    source_protocol="llm_v1",               # Optional: identifies the source plugin/protocol
)

applied = effect.apply()
```

## Field Details

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| document_id | str \| int | Yes | - | IntegrationTask ID |
| reviewer_id | str | No | None | Staff key to assign |
| team_id | str | No | None | Team UUID to assign |
| priority | Priority | No | NORMAL | Review priority level (normal/high) |
| review_mode | ReviewMode | No | REVIEW_REQUIRED | Review mode |
| annotations | list[dict] | No | None | Display annotations (objects with text and color) |
| source_protocol | str | No | None | Identifies the source plugin/protocol |

## Priority Values

| SDK Value | Database Value | Description |
|-----------|---------------|-------------|
| normal    | False         | Standard priority (default) |
| high      | True          | Elevated priority |

## ReviewMode Values

| SDK Value          | Database Value | Display Label            |
|--------------------|----------------|--------------------------|
| review_required    | RR             | Review required          |
| already_reviewed   | AR             | Already reviewed offline |
| review_not_required| RN             | Review not required      |

## Protocols

### AssignDocumentReviewerProtocol

Responds to events and assigns a reviewer with high priority and review required.

## Prefill Support

When the effect is processed, an `IntegrationTaskPrefill` record is created/updated with:

- `field_type`: "reviewer"
- `value`: Contains `reviewer_id`, `reviewer_name`, `team_id`, `team_name` as applicable
- `annotations`: The list provided by the plugin (stored as-is)
- `source_protocol`: The identifier provided by the plugin

This prefill data can be used by the UI to pre-populate reviewer fields and display
annotations to help users understand why a particular reviewer was suggested.

## Notes

- Both `reviewer_id` and `team_id` are optional and can be provided together
- If both are provided, the home-app interpreter will assign both
- The home-app interpreter validates that the document, staff, and team exist
- Whitespace is automatically stripped from string fields
- Annotations are passed directly to the prefill without modification
