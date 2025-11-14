# Task Comment Logger

An example plugin that demonstrates how to work with the `NoteTask` model to access task-related data, including the original internal comment and all subsequently added comments.

## Overview

This plugin listens for task and task comment events and logs a comprehensive list of all comments associated with a task. It demonstrates:

- Using the `NoteTask` model to access the `internal_comment` field
- Querying `TaskComment` records for a task
- Handling multiple event types (TASK_CREATED, TASK_UPDATED, TASK_COMMENT_CREATED, TASK_COMMENT_UPDATED)
- Sorting and displaying comments chronologically

## What It Does

When a task is created, updated, or a comment is added/updated, the handler:

1. Retrieves the task from the event context
2. Finds all `NoteTask` records associated with the task
3. Extracts the `internal_comment` from each `NoteTask` (entered during task creation)
4. Retrieves all `TaskComment` records for the task
5. Sorts all comments by creation timestamp
6. Logs the complete comment history

## Example Output

```
[TaskCommentLogger] Task 'Follow up on lab results' (ID: 12345) has 3 comment(s):
  1. [internal_comment] Dr. Smith (2025-01-15 10:30:00): Patient needs follow-up for abnormal lipid panel
  2. [task_comment] Nurse Johnson (2025-01-16 14:20:00): Called patient, left voicemail
  3. [task_comment] Dr. Smith (2025-01-17 09:15:00): Patient returned call, scheduled follow-up visit
```

## Use Cases

This example plugin can be adapted for:

- Auditing task comment history
- Generating task activity reports
- Triggering notifications based on comment content
- Analyzing task collaboration patterns
- Creating comment-based workflows

## Key Models Used

- **`NoteTask`**: A command model that represents a task created from a note. Contains the `internal_comment` field which stores notes entered during task creation.
- **`Task`**: The underlying task model
- **`TaskComment`**: Comments added to a task after creation

## Installation

```bash
canvas install task_comment_logger
```

## Testing

To test this plugin, create a task in Canvas with an internal comment, then add additional comments to see the logging output in the Canvas logs.

## Learn More

For more information about working with tasks in Canvas, see the [Canvas SDK documentation](https://docs.canvasmedical.com/).
