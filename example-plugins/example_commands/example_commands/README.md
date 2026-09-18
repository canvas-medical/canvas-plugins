example-commands
================

## Description

Examples of reacting to command lifecycle events.

Auto-populating command values with defaults when a command originates in a note:
- Refer
- Imaging Order

Blocking a command commit on pre-commit:
- Refill — `BlockRefillCommit` rejects the commit so a refill can't be signed and
  sent from Canvas. Both "Commit" and "Sign and send" route through
  `REFILL_COMMAND__PRE_COMMIT`; there is no SDK effect to hide the in-command
  button, so this gates the action with a `CommandValidationErrorEffect` instead.
  Add a condition in `compute()` to block selectively rather than every refill.
