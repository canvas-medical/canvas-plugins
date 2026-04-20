"""Async execution options for effects.

Plugin developers wrap an Effect with :func:`with_async` to have the platform
execute it via Celery instead of inline. Supports delay, retries, and
retry-filtering on exception type or HTTP status code.
"""

import json

from canvas_generated.messages.effects_pb2 import Effect

ASYNC_PROPS_KEY = "async_props"


def with_async(
    effect: Effect,
    *,
    delay_seconds: int | None = None,
    max_retries: int | None = None,
    retry_on_exceptions: list[str] | None = None,
    retry_on_status_codes: list[int] | None = None,
    retry_backoff: bool | int = False,
    retry_backoff_max: int | None = None,
    retry_jitter: bool = False,
) -> Effect:
    """Attach async execution options to an effect.

    The platform will run the effect through Celery rather than inline. All
    async options are packed into the effect's payload under the
    ``async_props`` key, so no extra protobuf fields are needed.

    Args:
        effect: The effect to make async.
        delay_seconds: Wait this many seconds before running. ``0`` runs
            immediately on Celery (async-now). Must be non-negative.
        max_retries: Maximum number of retry attempts on failure. Defaults
            to ``0`` (no retries).
        retry_on_exceptions: Fully-qualified exception class names to retry
            on, e.g. ``["requests.exceptions.ConnectionError",
            "requests.exceptions.Timeout"]``. Matched against the raised
            exception's class and its base classes. Typos fail silently —
            a name that does not match any real exception simply never
            triggers a retry.
        retry_on_status_codes: HTTP status codes to retry on, for effects
            whose handler raises an exception with a ``status_code``
            attribute (e.g. the :class:`HttpRequest` effect). Common:
            ``[500, 502, 503, 504]``.
        retry_backoff: ``True`` for exponential backoff (1, 2, 4, 8, ...
            seconds). A positive ``int`` sets the base delay:
            ``retry_backoff=5`` produces ``5, 10, 20, 40, ...`` Falsy
            values (``False``, ``0``) disable backoff.
        retry_backoff_max: Cap the backoff delay at this many seconds.
        retry_jitter: Add random jitter (0.5x–1.5x) to the backoff delay
            to avoid thundering herd when many tasks retry in sync.

    Returns:
        The same ``Effect`` with async options merged into its payload.
    """
    if delay_seconds is not None:
        if isinstance(delay_seconds, bool) or not isinstance(delay_seconds, int):
            raise TypeError(f"delay_seconds must be an int, got {type(delay_seconds).__name__}")
        if delay_seconds < 0:
            raise ValueError(f"delay_seconds must be non-negative, got {delay_seconds}")
    if max_retries is not None:
        if isinstance(max_retries, bool) or not isinstance(max_retries, int):
            raise TypeError(f"max_retries must be an int, got {type(max_retries).__name__}")
        if max_retries < 0:
            raise ValueError(f"max_retries must be non-negative, got {max_retries}")

    payload = json.loads(effect.payload) if effect.payload else {}
    props = payload.get(ASYNC_PROPS_KEY, {})

    if delay_seconds is not None:
        props["delay_seconds"] = delay_seconds
    if max_retries is not None:
        props["max_retries"] = max_retries
    if retry_on_exceptions is not None:
        props["retry_on_exceptions"] = list(retry_on_exceptions)
    if retry_on_status_codes is not None:
        props["retry_on_status_codes"] = list(retry_on_status_codes)
    if retry_backoff:
        props["retry_backoff"] = retry_backoff
    if retry_backoff_max is not None:
        props["retry_backoff_max"] = retry_backoff_max
    if retry_jitter:
        props["retry_jitter"] = True

    payload[ASYNC_PROPS_KEY] = props
    effect.payload = json.dumps(payload)
    return effect


__all__ = ("ASYNC_PROPS_KEY", "with_async")
