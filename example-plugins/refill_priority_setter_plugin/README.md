# Refill Priority Setter Plugin

## Description

This plugin automatically sets task priority to URGENT for teams with refill processing responsibilities. It ensures that tasks assigned to refill processing teams are properly prioritized for timely handling.

## Functionality

The plugin contains a single protocol that listens for task creation and update events:

### Priority Assignment Logic

When a task is created or updated, the protocol:
1. Checks if the task is assigned to a team with the `PROCESS_REFILL_REQUESTS` responsibility
2. If the team has this responsibility, sets the task priority to **URGENT**
3. If the team doesn't have this responsibility, maintains the current priority (no downgrading)

### Events Handled

- **TASK_CREATED**: Sets priority to URGENT for newly created tasks assigned to refill teams
- **TASK_UPDATED**: Updates priority when task assignments change
- **TASK_COMMAND__POST_UPDATE**: Updates priority when tasks are created via commands

## Configuration

This plugin requires no special configuration or secrets to function.

### Important Note!

The `CANVAS_MANIFEST.json` is used when installing your plugin. Please ensure it gets updated if you add, remove, or rename protocols.
