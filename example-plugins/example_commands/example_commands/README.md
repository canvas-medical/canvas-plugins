example-commands
================

## Description

Examples of reacting to command lifecycle events.

Auto-populating command values with defaults when a command originates in a note:
- Refer
- Imaging Order

Blocking a command commit with a validation error:
- Refill — `BlockRefillCommit` returns a `CommandValidationErrorEffect` on
  `REFILL_COMMAND__POST_VALIDATION`, so a refill can't be signed and sent from
  Canvas. The error disables the command's REVIEW button, which keeps Sign and
  send, Sign, and Print out of reach; the message shows as a tooltip on the
  disabled button. The block applies in the note UI only. There is no SDK
  effect to hide the in-command button, so this gates the action instead. Add a
  condition in `compute()` to block selectively rather than every refill.
  `REFILL_COMMAND__PRE_COMMIT` does not work for this, because a validation
  error returned there is ignored on the refill sign actions.
