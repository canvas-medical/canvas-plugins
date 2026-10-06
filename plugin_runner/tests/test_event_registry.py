import logging
from pathlib import Path
from unittest.mock import patch

import pytest

from plugin_runner.event_registry import NOT_READY, EventRegistry


@pytest.fixture
def stamp_path(tmp_path: Path) -> Path:
    """Path for the registry stamp file."""
    return tmp_path / "event-registry"


def test_registry_starts_not_ready(stamp_path: Path) -> None:
    """A fresh registry has published nothing, so callers must send every event."""
    registry = EventRegistry(stamp_path.as_posix())

    snapshot = registry.snapshot()

    assert snapshot.ready is False
    assert snapshot.event_types == frozenset()
    assert not stamp_path.exists()


def test_rebuilding_publishes_event_types_and_version(stamp_path: Path) -> None:
    """A completed rebuild publishes the handled event types and stamps the version."""
    registry = EventRegistry(stamp_path.as_posix())
    event_handler_map = {"PATIENT_CREATED": ["plugin:handlers:Handler"]}

    with registry.rebuilding(event_handler_map):
        pass

    snapshot = registry.snapshot()
    assert snapshot.ready is True
    assert snapshot.event_types == frozenset({"PATIENT_CREATED"})
    assert stamp_path.read_text() == snapshot.version


def test_rebuilding_excludes_event_types_without_handlers(stamp_path: Path) -> None:
    """Empty entries left by defaultdict reads are not published as handled."""
    registry = EventRegistry(stamp_path.as_posix())
    event_handler_map = {"PATIENT_CREATED": ["plugin:handlers:Handler"], "PATIENT_UPDATED": []}

    with registry.rebuilding(event_handler_map):
        pass

    assert registry.snapshot().event_types == frozenset({"PATIENT_CREATED"})


def test_stamp_is_not_ready_while_rebuilding(stamp_path: Path) -> None:
    """home-app sees not-ready for the whole rebuild, before any route changes."""
    registry = EventRegistry(stamp_path.as_posix())

    with registry.rebuilding({}):
        pass

    with registry.rebuilding({"PATIENT_CREATED": ["plugin:handlers:Handler"]}):
        assert stamp_path.read_text() == NOT_READY

    assert stamp_path.read_text() == registry.snapshot().version


def test_failed_rebuild_stays_not_ready(stamp_path: Path) -> None:
    """A rebuild that raises leaves the registry not-ready rather than publishing a partial map."""
    registry = EventRegistry(stamp_path.as_posix())

    with registry.rebuilding({"PATIENT_CREATED": ["plugin:handlers:Handler"]}):
        pass

    with pytest.raises(RuntimeError), registry.rebuilding({}):
        raise RuntimeError("load failed")

    assert registry.snapshot().ready is False
    assert stamp_path.read_text() == NOT_READY


def test_each_rebuild_gets_a_new_version(stamp_path: Path) -> None:
    """Versions never repeat within a runner process."""
    registry = EventRegistry(stamp_path.as_posix())

    with registry.rebuilding({}):
        pass
    first_version = registry.snapshot().version

    with registry.rebuilding({}):
        pass

    assert registry.snapshot().version != first_version


def test_restarted_runner_gets_a_new_version(stamp_path: Path) -> None:
    """A new runner process never reuses a previous process's version, even at the same generation."""
    first = EventRegistry(stamp_path.as_posix())
    second = EventRegistry(stamp_path.as_posix())

    with first.rebuilding({}):
        pass
    with second.rebuilding({}):
        pass

    assert first.snapshot().version != second.snapshot().version


def test_mark_not_ready(stamp_path: Path) -> None:
    """mark_not_ready overrides a published version."""
    registry = EventRegistry(stamp_path.as_posix())

    with registry.rebuilding({"PATIENT_CREATED": ["plugin:handlers:Handler"]}):
        pass

    registry.mark_not_ready()

    assert registry.snapshot().ready is False
    assert stamp_path.read_text() == NOT_READY


def test_stamp_write_failure_removes_stamp(stamp_path: Path) -> None:
    """If the stamp cannot be replaced, removing it makes home-app send every event."""
    registry = EventRegistry(stamp_path.as_posix())

    with registry.rebuilding({}):
        pass
    assert stamp_path.exists()

    with (
        patch("plugin_runner.event_registry.os.replace", side_effect=OSError("disk full")),
        patch("plugin_runner.event_registry.sentry_sdk.capture_exception") as capture,
        registry.rebuilding({"PATIENT_CREATED": ["plugin:handlers:Handler"]}),
    ):
        pass

    assert not stamp_path.exists()
    assert capture.called


def test_no_stamp_path_writes_nothing(tmp_path: Path) -> None:
    """Without a configured path the registry still tracks state but writes no file."""
    registry = EventRegistry(None)

    with registry.rebuilding({"PATIENT_CREATED": ["plugin:handlers:Handler"]}):
        pass

    assert registry.snapshot().ready is True
    assert list(tmp_path.iterdir()) == []


def test_rebuilding_logs_registry_diff(stamp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """A rebuild that changes the event types logs what was added and removed."""
    registry = EventRegistry(stamp_path.as_posix())

    with registry.rebuilding({"PATIENT_CREATED": ["plugin:handlers:Handler"]}):
        pass

    caplog.clear()
    with caplog.at_level(logging.INFO), registry.rebuilding({"PATIENT_UPDATED": ["p:h:H"]}):
        pass

    assert (
        "Event registry changed: added ['PATIENT_UPDATED'], removed ['PATIENT_CREATED']"
        in caplog.text
    )


def test_rebuilding_without_changes_logs_nothing(
    stamp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """A rebuild that leaves the event types unchanged does not log a diff."""
    registry = EventRegistry(stamp_path.as_posix())
    event_handler_map = {"PATIENT_CREATED": ["plugin:handlers:Handler"]}

    with registry.rebuilding(event_handler_map):
        pass

    caplog.clear()
    with caplog.at_level(logging.INFO), registry.rebuilding(event_handler_map):
        pass

    assert "Event registry changed" not in caplog.text
