from collections.abc import Generator
from unittest.mock import MagicMock

import pytest

from canvas_sdk.utils import reporting


@pytest.fixture
def reporter() -> Generator[MagicMock, None, None]:
    """Install a recording reporter, restoring whichever one was installed before."""
    previous = reporting._reporter
    recorder = MagicMock()
    reporting.set_reporter(recorder)
    yield recorder
    reporting.set_reporter(previous)


def test_reports_go_nowhere_without_a_reporter() -> None:
    """Outside the plugin runner nothing is installed, and reporting is a no-op."""
    previous = reporting._reporter
    reporting.set_reporter(None)

    try:
        reporting.capture_exception(ValueError("boom"))
        reporting.capture_message("message", level="error")
    finally:
        reporting.set_reporter(previous)


def test_capture_exception_reaches_the_installed_reporter(reporter: MagicMock) -> None:
    """An exception is handed to the reporter as is."""
    error = ValueError("boom")

    reporting.capture_exception(error)

    reporter.capture_exception.assert_called_once_with(error)


def test_capture_message_passes_level_tags_and_context(reporter: MagicMock) -> None:
    """A message carries its level, tags and context blocks to the reporter."""
    reporting.capture_message(
        "message", level="fatal", tags={"plugin-name": "p"}, context={"block": {"k": "v"}}
    )

    reporter.capture_message.assert_called_once_with(
        "message", "fatal", {"plugin-name": "p"}, {"block": {"k": "v"}}
    )


def test_capture_message_defaults_to_no_tags_or_context(reporter: MagicMock) -> None:
    """Tags and context default to empty mappings."""
    reporting.capture_message("message", level="warning")

    reporter.capture_message.assert_called_once_with("message", "warning", {}, {})
