"""Per-scope_key single-flight lock for agent runs.

Implements the doc §6.2 lock primitive: a per-``scope_key`` lock acquired
at the start of an agent invocation and released when it completes (or
crashes / times out). Two concurrent attempts for the same scope_key
race; the loser raises :class:`AgentLocked` and the caller decides how
to handle it — retry-with-backoff for triggered agents (the doc's
``autoretry_for=(AgentLocked,)`` pattern), HTTP 409 for interactive
user-initiated invocations like chat.

Storage is the per-customer "plugins" cache (Caching API, backed by
the EHR instance's Postgres) — same namespace plugin authors use via
:func:`canvas_sdk.caching.plugins.get_cache`, but accessed through the
lower-level client so this helper works from both plugin and platform
code paths. Tenant isolation comes from the cache backend's
``KEY_PREFIX = CUSTOMER_IDENTIFIER``.

The lock primitive is :meth:`Cache.get_or_set` with a per-acquisition
sentinel:

- Caller A passes ``sentinel_a``; cache had no entry, sets it, returns
  ``sentinel_a``. A holds the lock.
- Caller B passes ``sentinel_b`` while A still holds it; cache returns
  ``sentinel_a`` (the existing value). B's returned value ``!= sentinel_b``,
  so B raises :class:`AgentLocked` without ever taking the lock.

TTL on the cache entry bounds blast radius if the holder crashes
without releasing; after ``timeout_seconds`` the lock becomes
acquirable by the next caller automatically.

Scope-key uniqueness across plugins is the plugin author's
responsibility — by convention scope_keys are prefixed with the plugin
name and agent identity (e.g. ``"agent_runner_poc:chart_chat:patient:
{id}"``), so locks naturally don't collide between plugins.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from uuid import uuid4

from canvas_sdk.caching.client import get_cache

DEFAULT_LOCK_TIMEOUT_SECONDS = 600


class AgentLocked(RuntimeError):
    """Raised when another invocation already holds the lock for this scope_key."""


@contextmanager
def agent_lock(
    scope_key: str,
    *,
    holder_id: str | None = None,
    timeout_seconds: int = DEFAULT_LOCK_TIMEOUT_SECONDS,
) -> Iterator[str]:
    """Acquire a per-``scope_key`` single-flight lock for the duration of the block.

    Args:
        scope_key: The lock key. By convention the scope_key already encodes
            plugin name and agent identity (e.g.
            ``"agent_runner_poc:chart_chat:patient:p1"``) so two distinct
            agents on the same patient don't serialize against each other,
            and locks don't collide across plugins.
        holder_id: Optional identifier for the lock holder, included verbatim
            in :class:`AgentLocked`'s error message to make debugging
            contention easier (the message tells the caller which prior run
            won the race). Typically the agent's ``run_id`` for triggered
            invocations. A random UUID is generated if not supplied.
        timeout_seconds: TTL on the lock entry. The holder is expected to
            complete and release within this window; if it crashes, the TTL
            ensures the lock eventually expires and the next attempt succeeds.

    Yields:
        The sentinel value used to claim the lock (``holder_id`` or the
        generated UUID), in case callers want to log or correlate it.

    Raises:
        AgentLocked: If the lock is already held by another holder. Caller
            decides whether to retry (with backoff) or surface the
            contention to the user.
    """
    # The "plugins" cache driver has KEY_PREFIX=CUSTOMER_IDENTIFIER baked in,
    # so locks are tenant-isolated automatically. We bypass canvas_sdk.caching
    # .plugins.get_cache (which requires a plugin frame in the call stack)
    # because this helper has to work from platform code paths like the
    # plugin-runner's RunAgent RPC too.
    cache = get_cache(driver="plugins")
    lock_key = f"agent-lock:{scope_key}"
    sentinel = holder_id or str(uuid4())

    existing = cache.get_or_set(lock_key, sentinel, timeout_seconds=timeout_seconds)
    if existing != sentinel:
        raise AgentLocked(
            f"Agent lock {scope_key!r} is held by {existing!r}; attempt by {sentinel!r} rejected."
        )
    try:
        yield sentinel
    finally:
        cache.delete(lock_key)


__exports__ = ("AgentLocked", "agent_lock")
