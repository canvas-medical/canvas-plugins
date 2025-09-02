# Urgent Task Banner Plugin

## Description

This plugin automatically manages a banner alert on a patient's chart to provide high visibility into urgent, time-sensitive tasks. It ensures the banner's presence is always synchronized with the real-time state of a patient's tasks by listening to dedicated task events.

## Functionality

The plugin contains a single protocol that listens for and acts on two specific events:

### On `TASK_CREATED` (Task Creation)

When a new task is created, the protocol immediately checks if the task's `priority` field has been set to **"Urgent"**. If it has, the plugin adds a banner alert to the associated patient's chart.

### On `TASK_PRIORITY_UPDATED` (Task Priority Is Changed)

This plugin is designed to efficiently respond to the custom `TASK_PRIORITY_UPDATED` event. This event fires only when a task's priority is modified, preventing the plugin from running unnecessarily on every task update. The event's context provides the priority value *before* and *after* the change.

-   **Banner Addition**: If the priority changes **to "Urgent"** from any other value, the plugin adds the banner alert.
-   **Banner Removal**: If the priority changes **from "Urgent"** to any other value (or is cleared), the plugin removes the banner alert.

## Configuration

This plugin requires no special configuration or secrets to function.

### Important Note!

The `CANVAS_MANIFEST.json` is used when installing your plugin. Please ensure it gets updated if you add, remove, or rename protocols.
