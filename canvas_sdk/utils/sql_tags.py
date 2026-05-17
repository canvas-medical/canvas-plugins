"""SDK-side shim over home-app's SQL commenter context-variable registry.

When the plugin-runner runs inlined into home-app (production), this re-exports
``query_tags`` from ``app.sql_tags`` so SQL queries issued from inside a handler
get tagged with plugin / event / handler context. When the canvas-plugins repo
is exercised standalone (no home-app on the path, e.g. local plugin tests),
``query_tags`` is a no-op context manager.
"""

from collections.abc import Iterator
from contextlib import contextmanager

try:
    from app.sql_tags import query_tags
except ImportError:

    @contextmanager
    def query_tags(**tags: str | None) -> Iterator[None]:
        """No-op fallback used outside the home-app runtime."""
        yield


__all__ = ["query_tags"]
