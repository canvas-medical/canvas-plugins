"""Tests for BlockRefillCommit.

The handler reacts to REFILL_COMMAND__PRE_COMMIT — the event both "Commit" and
"Sign and send" route through on a refill — and returns a
CommandValidationErrorEffect that aborts the commit and surfaces a message on the
command. The effect is pure (no data-layer access), so these tests exercise the
real effect and assert on its serialized payload; only the logger is patched.
"""

import json
from typing import Any
from unittest.mock import Mock, patch

from example_commands.handlers.example_refill import REFILL_BLOCKED_MESSAGE, BlockRefillCommit

from canvas_sdk.effects import EffectType
from canvas_sdk.events import EventType

HANDLER_MODULE = "example_commands.handlers.example_refill"


def _compute(target_id: str = "refill-uuid") -> list[Any]:
    """Run compute() with the logger patched; returns the effects list."""
    handler = BlockRefillCommit(event=Mock(target=Mock(id=target_id)))
    with patch(f"{HANDLER_MODULE}.log"):
        return handler.compute()


def test_responds_to_refill_pre_commit() -> None:
    """Handler subscribes to REFILL_COMMAND__PRE_COMMIT."""
    assert EventType.Name(EventType.REFILL_COMMAND__PRE_COMMIT) in BlockRefillCommit.RESPONDS_TO


def test_has_required_attributes() -> None:
    """Handler exposes the contract expected by the plugin runner."""
    assert hasattr(BlockRefillCommit, "RESPONDS_TO")
    assert hasattr(BlockRefillCommit, "compute")


def test_compute_returns_single_validation_error_effect() -> None:
    """compute() returns exactly one COMMAND_VALIDATION_ERRORS effect."""
    effects = _compute()
    assert len(effects) == 1
    assert effects[0].type == EffectType.COMMAND_VALIDATION_ERRORS


def test_compute_payload_carries_block_message() -> None:
    """The emitted effect carries the refill-blocked message for the UI."""
    effects = _compute()
    payload = json.loads(effects[0].payload)
    messages = [error["message"] for error in payload["data"]["errors"]]
    assert messages == [REFILL_BLOCKED_MESSAGE]


def test_compute_logs_command_uuid() -> None:
    """compute() logs the UUID of the command it is blocking."""
    handler = BlockRefillCommit(event=Mock(target=Mock(id="refill-uuid-log")))
    with patch(f"{HANDLER_MODULE}.log") as mock_log:
        handler.compute()
    log_messages = [call.args[0] for call in mock_log.info.call_args_list]
    assert any("refill-uuid-log" in msg for msg in log_messages)
