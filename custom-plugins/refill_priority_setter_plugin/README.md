# Refill Priority Setter Plugin

## Description

This plugin automates the management of task priorities for a specific clinical workflow: prescription refills. It ensures that new refill-related tasks are correctly prioritized and that the priority is cleared if the task becomes unassigned.

## Functionality

The plugin contains a single protocol that listens for and acts on two specific events:

### On `TASK_CREATED` (Task Creation)

When a new task is created, the protocol performs the following checks:
1.  It first verifies that the task's title contains the word "refill" (case-insensitive).
2.  It then checks that the task is assigned to a team with the `PROCESS_REFILL_REQUESTS` responsibility.
3.  If **both** conditions are met, the task's `priority` is automatically set to **"Urgent"**.

### On `TASK_UPDATED` (Task Update)

When an existing task is updated, the protocol checks if the task still has a team assigned.
- If the task is **not** assigned to a team, its `priority` is automatically cleared (set to `None`). This prevents stale priorities from remaining on unassigned tasks.

## Configuration

This plugin requires no special configuration or secrets to function.

### Important Note!

The `CANVAS_MANIFEST.json` is used when installing your plugin. Please ensure it gets updated if you add, remove, or rename protocols.
