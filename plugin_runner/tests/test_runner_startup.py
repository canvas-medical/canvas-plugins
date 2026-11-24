from unittest.mock import MagicMock, patch

from statsd.defaults.env import statsd as default_statsd_client

from canvas_sdk.utils import metrics, reporting
from plugin_runner import plugin_runner


def test_the_runner_reports_through_sentry() -> None:
    """Loading the runner points the SDK's error reporting at Sentry."""
    assert isinstance(reporting._reporter, plugin_runner.SentryReporter)


def test_the_runner_configures_metrics() -> None:
    """Loading the runner sends metrics through statsd and reads memory with psutil."""
    assert metrics._client is default_statsd_client
    assert metrics._process_rss_bytes is plugin_runner.process_rss_bytes
    assert plugin_runner.process_rss_bytes() > 0


def test_sentry_reporter_captures_exceptions_on_the_current_scope() -> None:
    """Exceptions keep whatever tags the runner set on the current scope."""
    error = ValueError("boom")

    with patch.object(plugin_runner.sentry_sdk, "capture_exception") as capture_exception:
        plugin_runner.SentryReporter().capture_exception(error)

    capture_exception.assert_called_once_with(error)


def test_sentry_reporter_captures_messages_with_their_tags_and_context() -> None:
    """A message goes out on its own scope, carrying its tags and context blocks."""
    scope = MagicMock()

    with (
        patch.object(plugin_runner.sentry_sdk, "new_scope") as new_scope,
        patch.object(plugin_runner.sentry_sdk, "capture_message") as capture_message,
    ):
        new_scope.return_value.__enter__.return_value = scope
        plugin_runner.SentryReporter().capture_message(
            "message", "fatal", {"plugin-name": "p"}, {"block": {"k": "v"}}
        )

    scope.set_tag.assert_called_once_with("plugin-name", "p")
    scope.set_context.assert_called_once_with("block", {"k": "v"})
    capture_message.assert_called_once_with("message", level="fatal")
