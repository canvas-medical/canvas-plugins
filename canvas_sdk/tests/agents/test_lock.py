"""Tests for the agent_lock per-scope_key single-flight primitive."""
# ruff: noqa: SIM117  # tests intentionally nest contexts to expose lock contention

from collections.abc import Generator

import pytest
from django.core.cache import caches

from canvas_sdk.agents import AgentLocked, agent_lock


@pytest.fixture(autouse=True)
def _isolate_cache() -> Generator[None, None, None]:
    """Clear the "plugins" cache backend before each test.

    Each test should start with no locks held; flush the LocMemCache the
    test environment uses so prior tests don't leak lock entries.
    """
    caches["plugins"].clear()
    yield
    caches["plugins"].clear()


def test_lock_acquires_and_releases_on_normal_exit() -> None:
    """A held lock is released when the context manager exits cleanly."""
    with agent_lock("plugin:agent:patient:1"):
        pass

    # Lock should be reacquirable now that the previous holder released it.
    with agent_lock("plugin:agent:patient:1"):
        pass


def test_lock_releases_on_exception() -> None:
    """If the wrapped block raises, the lock still releases via finally."""

    class _Boom(RuntimeError):
        pass

    with pytest.raises(_Boom):
        with agent_lock("plugin:agent:patient:2"):
            raise _Boom

    # Lock should be reacquirable.
    with agent_lock("plugin:agent:patient:2"):
        pass


def test_concurrent_acquisition_raises_agent_locked() -> None:
    """A second attempt while the first holds the lock raises AgentLocked."""
    with agent_lock("plugin:agent:patient:3", holder_id="first"):
        with pytest.raises(AgentLocked, match="held by 'first'"):
            with agent_lock("plugin:agent:patient:3", holder_id="second"):
                pytest.fail("Second acquisition should not have succeeded")


def test_locks_are_scoped_per_scope_key() -> None:
    """Different scope_keys don't contend; both can hold their locks concurrently."""
    with agent_lock("plugin:agent:patient:A"):
        with agent_lock("plugin:agent:patient:B"):
            # Both locks held simultaneously — no contention because the keys differ.
            pass


def test_holder_id_surfaces_in_error_message() -> None:
    """AgentLocked names both the current holder and the rejected attempt."""
    with agent_lock("plugin:agent:patient:4", holder_id="run-A"):
        with pytest.raises(AgentLocked) as exc_info:
            with agent_lock("plugin:agent:patient:4", holder_id="run-B"):
                pass

    message = str(exc_info.value)
    assert "'run-A'" in message, "current holder should appear in the error"
    assert "'run-B'" in message, "rejected attempt should appear in the error"


def test_auto_generated_holder_id_when_unspecified() -> None:
    """When holder_id isn't supplied, a UUID is generated and used as the sentinel.

    The contract is just that the sentinels differ between two concurrent
    attempts so the second sees something other than its own sentinel back
    from the cache. We exercise that without inspecting the generated value.
    """
    with agent_lock("plugin:agent:patient:5"):
        with pytest.raises(AgentLocked):
            with agent_lock("plugin:agent:patient:5"):
                pass


def test_context_manager_yields_sentinel() -> None:
    """The ``as``-bound value is the sentinel used to claim the lock."""
    with agent_lock("plugin:agent:patient:6", holder_id="run-explicit") as sentinel:
        assert sentinel == "run-explicit"

    with agent_lock("plugin:agent:patient:7") as sentinel:
        # UUID-shaped — just enough to confirm something was generated.
        assert len(sentinel) >= 32
