"""The set of event types that have at least one loaded handler.

home-app uses this to skip sending events that no plugin would receive. Skipping
is only safe while home-app's copy is at least as large as the runner's live
routes, so every change follows one order:

1. write the stamp file as ``not-ready`` (home-app sends every event)
2. rebuild the routes
3. bump the generation, then write the new version to the stamp file

home-app reads the stamp file on every event (it is container-local and tiny)
and only trusts a registry fetched over gRPC whose version equals the stamp.
Anything else (missing file, ``not-ready``, a version mismatch) means send.
"""

import os
import pathlib
import threading
import uuid
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from typing import NamedTuple

import sentry_sdk

from logger import log

NOT_READY = "not-ready"


def log_registry_diff(old: frozenset[str], new: frozenset[str]) -> None:
    """Log the event types a rebuild added and removed, if any."""
    added = sorted(new - old)
    removed = sorted(old - new)

    if added or removed:
        log.info(f"Event registry changed: added {added}, removed {removed}")


class RegistrySnapshot(NamedTuple):
    """A consistent view of the registry."""

    version: str
    ready: bool
    event_types: frozenset[str]


class EventRegistry:
    """Tracks which event types have handlers and publishes a version stamp for home-app."""

    def __init__(self, stamp_path: str | None) -> None:
        self._stamp_path = pathlib.Path(stamp_path) if stamp_path else None
        self._boot_id = uuid.uuid4().hex
        self._generation = 0
        self._ready = False
        self._event_types: frozenset[str] = frozenset()
        self._lock = threading.Lock()

    @property
    def version(self) -> str:
        """The version string home-app compares against the stamp file."""
        return f"{self._boot_id}:{self._generation}"

    def snapshot(self) -> RegistrySnapshot:
        """Return the version, readiness, and event types as one consistent read."""
        with self._lock:
            return RegistrySnapshot(self.version, self._ready, self._event_types)

    def mark_not_ready(self) -> None:
        """Tell home-app to send every event, e.g. while the runner starts or stops."""
        with self._lock:
            self._ready = False
            self._write_stamp(NOT_READY)

    @contextmanager
    def rebuilding(self, event_handler_map: Mapping[str, Sequence[str]]) -> Iterator[None]:
        """Wrap a rebuild of ``event_handler_map``.

        The registry is not-ready for the whole rebuild and republished only
        when the body completes. If the body raises, it stays not-ready, so
        home-app keeps sending every event until the next successful rebuild.
        """
        with self._lock:
            self._ready = False
            self._write_stamp(NOT_READY)

            yield

            # HandleEvent reads the map with defaultdict semantics, which leaves
            # empty entries behind for event types nobody handles.
            event_types = frozenset(
                event_type for event_type, handlers in event_handler_map.items() if handlers
            )
            log_registry_diff(self._event_types, event_types)

            self._event_types = event_types
            self._generation += 1
            self._ready = True
            self._write_stamp(self.version)

    def _write_stamp(self, content: str) -> None:
        """Atomically replace the stamp file; on failure remove it so home-app sends everything."""
        if self._stamp_path is None:
            return

        temporary_path = self._stamp_path.with_name(f".{self._stamp_path.name}.{os.getpid()}")

        try:
            temporary_path.write_text(content)
            os.replace(temporary_path, self._stamp_path)
        except OSError as write_error:
            log.exception(f'Failed to write the event registry stamp "{self._stamp_path}"')
            sentry_sdk.capture_exception(write_error)

            try:
                self._stamp_path.unlink(missing_ok=True)
            except OSError as unlink_error:
                log.exception(
                    f'Failed to remove the event registry stamp "{self._stamp_path}"; '
                    "home-app may skip events for handlers loaded after this point"
                )
                sentry_sdk.capture_exception(unlink_error)
