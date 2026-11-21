"""Error reporting for code that also loads outside the plugin runner.

The SDK and the plugin loader run inside the plugin runner, and also inside `canvas validate`,
`canvas deploy` and plugin tests, where the runner's packages are not installed. They report
through this module, and the plugin runner points it at Sentry when it starts
(``plugin_runner.plugin_runner``). Until then, reports go nowhere.
"""

from collections.abc import Mapping
from typing import Any, Literal, Protocol

Level = Literal["fatal", "critical", "error", "warning", "info", "debug"]


class ErrorReporter(Protocol):
    """What the plugin runner provides to receive reports."""

    def capture_exception(self, error: BaseException) -> None:
        """Report an exception."""
        ...

    def capture_message(
        self,
        message: str,
        level: Level,
        tags: Mapping[str, str],
        context: Mapping[str, Mapping[str, Any]],
    ) -> None:
        """Report a message at a level, with tags and named context blocks."""
        ...


_reporter: ErrorReporter | None = None


def set_reporter(reporter: ErrorReporter | None) -> None:
    """Send every later report to ``reporter``, or nowhere when it is None."""
    global _reporter
    _reporter = reporter


def capture_exception(error: BaseException) -> None:
    """Report an exception to the installed reporter."""
    if _reporter is not None:
        _reporter.capture_exception(error)


def capture_message(
    message: str,
    level: Level,
    tags: Mapping[str, str] | None = None,
    context: Mapping[str, Mapping[str, Any]] | None = None,
) -> None:
    """Report a message to the installed reporter."""
    if _reporter is not None:
        _reporter.capture_message(message, level, tags or {}, context or {})


__exports__ = ()
