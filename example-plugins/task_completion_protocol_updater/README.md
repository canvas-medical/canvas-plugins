# Task Completion Protocol Updater

This plugin automatically updates ProtocolCard status when affiliated tasks are completed.

## Overview

When a task is marked as complete, this plugin:

1. Checks if the task has a `LINKED_PROTOCOL_CARD` label
2. Extracts the protocol key from any `PROTOCOL_CARD_{key}` label
3. Updates the corresponding protocol card status to `SATISFIED`

## Usage

To link a task to a protocol card, add these two labels to the task:

1. `LINKED_PROTOCOL_CARD` - indicates this task satisfies/closes a protocol
2. `PROTOCOL_CARD_{key}` - where `{key}` is the unique key of the protocol card to update

For example:
- `LINKED_PROTOCOL_CARD`
- `PROTOCOL_CARD_annual_wellness_visit`

When this task is completed, the protocol card with key `annual_wellness_visit` will be updated to `SATISFIED` status.

## Requirements

- Canvas SDK version 0.45.0 or later
- Task must be associated with a patient
- Protocol card with the specified key must exist or will be created

## Implementation Details

The plugin responds to `TASK_COMPLETED` events and uses the task's patient ID and the extracted protocol key to update the appropriate protocol card via the `ProtocolCard.apply()` method.