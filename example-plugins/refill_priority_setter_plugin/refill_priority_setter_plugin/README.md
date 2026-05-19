# Refill Priority Setter Plugin

## Description

This plugin provides automated task management for refill processing workflows. It includes two handlers: one that automatically sets task priority to URGENT for teams with refill processing responsibilities, and another that creates follow-up tasks when a refill prescription is queued for transmission.

## Functionality

The plugin contains two handlers that work together to ensure proper refill task management:

### 1. RefillTaskPriorityHandler

Automatically manages task priorities for refill-related workflows.

**Priority Assignment Logic:**
- Checks if the task is assigned to a team with the `PROCESS_REFILL_REQUESTS` responsibility.
- If the team has this responsibility, sets the task priority to **URGENT**.
- If the team doesn't have this responsibility, maintains the current priority (no downgrading).

**Events Handled:**
- **TASK_CREATED** — sets priority to URGENT for newly created tasks assigned to refill teams.
- **TASK_UPDATED** — updates priority when task assignments change.
- **TASK_COMMAND__POST_UPDATE** — updates priority when tasks are created via commands.

### 2. CreateRefillTaskHandler

Automatically creates a follow-up task when a refill prescription is queued for transmission.

**Task Creation Logic:**
- Listens for `PRESCRIPTION_PENDING` events.
- Skips the prescription unless `prescription.is_refill` is true, so original prescriptions don't generate follow-up tasks.
- Creates a follow-up task titled `Follow up on refill of {medication}`.
- Sets priority to **URGENT** for timely processing.
- Assigns the task to a team with the `PROCESS_REFILL_REQUESTS` responsibility (or leaves it unassigned if no such team exists).
- Prevents duplicate tasks for the same medication and patient.

**Events Handled:**
- **PRESCRIPTION_PENDING** — fires after Sign / Sign & Send queues the refill for transmission, regardless of which UI button the prescriber clicked.

> **Why `PRESCRIPTION_PENDING` rather than `REFILL_COMMAND__POST_COMMIT`?**
> The plugin originally listened for `REFILL_COMMAND__POST_COMMIT`, but home-app's refill submit flow does not always dispatch the command-lifecycle event reliably from every UI path. `PRESCRIPTION_PENDING` is a prescription-model event that fires on the actual state transition, which is a more dependable signal that the prescriber has queued the refill.

## Configuration

This plugin requires no special configuration or secrets to function.

### Important Note!

The `CANVAS_MANIFEST.json` is used when installing your plugin. Please ensure it gets updated if you add, remove, or rename handlers.
