# Refill Priority Setter Plugin

## Description

This plugin provides automated task management for refill processing workflows. It includes two protocols: one that automatically sets task priority to URGENT for teams with refill processing responsibilities, and another that creates follow-up tasks when refill commands are committed.

## Functionality

The plugin contains two protocols that work together to ensure proper refill task management:

### 1. RefillTaskPriorityProtocol

This protocol automatically manages task priorities for refill-related workflows:

**Priority Assignment Logic:**
- Checks if the task is assigned to a team with the `PROCESS_REFILL_REQUESTS` responsibility
- If the team has this responsibility, sets the task priority to **URGENT**
- If the team doesn't have this responsibility, maintains the current priority (no downgrading)

**Events Handled:**
- **TASK_CREATED**: Sets priority to URGENT for newly created tasks assigned to refill teams
- **TASK_UPDATED**: Updates priority when task assignments change
- **TASK_COMMAND__POST_UPDATE**: Updates priority when tasks are created via commands

### 2. CreateRefillTaskProtocol

This protocol automatically creates follow-up tasks when refill commands are committed:

**Task Creation Logic:**
- Listens for `REFILL_COMMAND__POST_COMMIT` events
- Creates a follow-up task with title "Follow up on refill of {medication}"
- Sets priority to **URGENT** for timely processing
- Assigns to a team with `PROCESS_REFILL_REQUESTS` responsibility
- Prevents duplicate tasks for the same medication and patient

**Events Handled:**
- **REFILL_COMMAND__POST_COMMIT**: Creates follow-up task when refill commands are committed

## Configuration

This plugin requires no special configuration or secrets to function.

### Important Note!

The `CANVAS_MANIFEST.json` is used when installing your plugin. Please ensure it gets updated if you add, remove, or rename protocols.
