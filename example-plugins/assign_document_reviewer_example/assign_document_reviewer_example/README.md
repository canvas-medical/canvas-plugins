# Assign Document Reviewer Example

Example plugin demonstrating the `ASSIGN_DOCUMENT_REVIEWER` effect.

## Overview

This plugin shows how to use the `AssignDocumentReviewer` effect to automatically
assign staff members or teams as reviewers to documents in the Data Integration queue.

## Effect Usage

```python
from canvas_sdk.effects.assign_document_reviewer import (
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
    confidence_scores={"document_id": 0.95},# Optional: confidence score (0.0-1.0)
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
| confidence_scores | dict | No | None | Confidence score for document ID |

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

## Confidence Scores

The `confidence_scores` field is used for monitoring and debugging only.
It accepts a dictionary with `"document_id"` as the key and a float (0.0-1.0) as the value:

```python
confidence_scores={"document_id": 0.95}
```

## Notes

- Both `reviewer_id` and `team_id` are optional and can be provided together
- If both are provided, the home-app interpreter will assign both
- The home-app interpreter validates that the document, staff, and team exist
- Whitespace is automatically stripped from string fields
