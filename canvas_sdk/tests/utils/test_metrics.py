"""Tests for the measure() context manager in canvas_sdk.utils.metrics."""

import os
from unittest.mock import MagicMock, patch

import pytest

from canvas_sdk.utils.metrics import PipelineProxy, StatsDClientProxy, measure


def _make_client() -> tuple[MagicMock, MagicMock]:
    """Return a (mock_client, mock_pipeline) pair wired together."""
    pipeline = MagicMock(spec=PipelineProxy)
    client = MagicMock(spec=StatsDClientProxy)
    client.pipeline.return_value = pipeline
    return client, pipeline


# ---------------------------------------------------------------------------
# Basic timing, execution count, and tags
# ---------------------------------------------------------------------------


@patch("canvas_sdk.utils.metrics.time")
def test_records_timing_and_execution_count(mock_time: MagicMock) -> None:
    """measure() should emit a timing metric and an execution increment."""
    mock_time.perf_counter_ns.side_effect = [0, 5_000_000]
    client, pipeline = _make_client()

    with measure("my_block", client=client):
        pass

    expected_tags = {"name": "my_block", "status": "success"}
    pipeline.timing.assert_called_once_with("plugins.timings", 5.0, tags=expected_tags)
    pipeline.incr.assert_called_once_with("plugins.executions", tags=expected_tags)
    pipeline.send.assert_called_once()


@patch("canvas_sdk.utils.metrics.time")
def test_extra_tags_merged(mock_time: MagicMock) -> None:
    """Extra tags should appear alongside name and status."""
    mock_time.perf_counter_ns.side_effect = [0, 0]
    client, pipeline = _make_client()

    with measure("block", extra_tags={"env": "test", "tier": "free"}, client=client):
        pass

    tags = pipeline.timing.call_args.kwargs["tags"]
    assert tags["name"] == "block"
    assert tags["env"] == "test"
    assert tags["tier"] == "free"
    assert tags["status"] == "success"


@patch("canvas_sdk.utils.metrics.time")
def test_error_status_on_exception(mock_time: MagicMock) -> None:
    """An exception should set status=error, still send, and propagate."""
    mock_time.perf_counter_ns.side_effect = [0, 0]
    client, pipeline = _make_client()

    with pytest.raises(ValueError, match="boom"), measure("block", client=client):
        raise ValueError("boom")

    tags = pipeline.timing.call_args.kwargs["tags"]
    assert tags["status"] == "error"
    pipeline.send.assert_called_once()


# ---------------------------------------------------------------------------
# Duration arithmetic
# ---------------------------------------------------------------------------


@patch("canvas_sdk.utils.metrics.time")
def test_duration_arithmetic(mock_time: MagicMock) -> None:
    """Nanosecond delta should be converted to milliseconds correctly."""
    mock_time.perf_counter_ns.side_effect = [1_000_000_000, 1_123_456_789]
    client, pipeline = _make_client()

    with measure("block", client=client):
        pass

    duration_ms = pipeline.timing.call_args.args[1]
    assert duration_ms == pytest.approx(123.456789)


# ---------------------------------------------------------------------------
# track_queries
# ---------------------------------------------------------------------------


@patch("canvas_sdk.utils.metrics.connection")
@patch("canvas_sdk.utils.metrics.time")
def test_track_queries_captures_metrics(mock_time: MagicMock, mock_conn: MagicMock) -> None:
    """track_queries should record query count and total duration."""
    mock_time.perf_counter_ns.side_effect = [0, 0]
    mock_conn.queries = [{"time": "0.010"}, {"time": "0.025"}]
    client, pipeline = _make_client()

    with measure("block", track_queries=True, client=client):
        pass

    # Should enable debug cursor on entry and disable on exit
    assert mock_conn.force_debug_cursor is False  # final state after cleanup
    mock_conn.queries_log.clear.assert_called_once()

    expected_tags = {"name": "block", "status": "success"}
    pipeline.timing.assert_any_call("plugins.query_count", delta=2, tags=expected_tags)
    pipeline.timing.assert_any_call("plugins.query_duration_ms", delta=35.0, tags=expected_tags)


@patch("canvas_sdk.utils.metrics.connection")
@patch("canvas_sdk.utils.metrics.time")
def test_track_queries_duration_arithmetic(mock_time: MagicMock, mock_conn: MagicMock) -> None:
    """Query durations in seconds should be summed and converted to ms."""
    mock_time.perf_counter_ns.side_effect = [0, 0]
    mock_conn.queries = [{"time": "0.001"}, {"time": "0.002"}, {"time": "0.0035"}]
    client, pipeline = _make_client()

    with measure("block", track_queries=True, client=client):
        pass

    duration_call = [
        c for c in pipeline.timing.call_args_list if c.args[0] == "plugins.query_duration_ms"
    ]
    assert len(duration_call) == 1
    assert duration_call[0].kwargs["delta"] == pytest.approx(6.5)


@patch("canvas_sdk.utils.metrics.time")
def test_track_queries_false_does_not_touch_connection(mock_time: MagicMock) -> None:
    """When track_queries is False, connection should not be accessed."""
    mock_time.perf_counter_ns.side_effect = [0, 0]
    client, pipeline = _make_client()

    with patch("canvas_sdk.utils.metrics.connection"), measure("block", client=client):
        pass

    # No query-related timing calls
    metric_names = [c.args[0] for c in pipeline.timing.call_args_list]
    assert "plugins.query_count" not in metric_names
    assert "plugins.query_duration_ms" not in metric_names


# ---------------------------------------------------------------------------
# track_plugins_usage
# ---------------------------------------------------------------------------


@patch("canvas_sdk.utils.metrics.time")
def test_track_plugins_usage_adds_plugin_tags(mock_time: MagicMock) -> None:
    """When is_plugin_caller returns a plugin, tags should include plugin and handler."""
    mock_time.perf_counter_ns.side_effect = [0, 0]
    client, pipeline = _make_client()

    with (
        patch(
            "canvas_sdk.utils.plugins.is_plugin_caller",
            return_value=(True, "my_plugin.protocols.handler"),
        ),
        measure("block", track_plugins_usage=True, client=client),
    ):
        pass

    tags = pipeline.timing.call_args.kwargs["tags"]
    assert tags["plugin"] == "my_plugin"
    assert tags["handler"] == "my_plugin.protocols.handler"


@patch("canvas_sdk.utils.metrics.time")
def test_track_plugins_usage_non_plugin_caller(mock_time: MagicMock) -> None:
    """When caller is not a plugin, tags should not include plugin or handler."""
    mock_time.perf_counter_ns.side_effect = [0, 0]
    client, pipeline = _make_client()

    with (
        patch(
            "canvas_sdk.utils.plugins.is_plugin_caller",
            return_value=(False, None),
        ),
        measure("block", track_plugins_usage=True, client=client),
    ):
        pass

    tags = pipeline.timing.call_args.kwargs["tags"]
    assert "plugin" not in tags
    assert "handler" not in tags


# ---------------------------------------------------------------------------
# track_memory_usage
# ---------------------------------------------------------------------------


@patch("canvas_sdk.utils.metrics.psutil")
@patch("canvas_sdk.utils.metrics.time")
def test_track_memory_usage_captures_rss_delta(
    mock_time: MagicMock, mock_psutil: MagicMock
) -> None:
    """track_memory_usage should record the RSS delta in bytes."""
    mock_time.perf_counter_ns.side_effect = [0, 0]
    mb = 1024 * 1024
    mock_process = MagicMock()
    mock_process.memory_info.side_effect = [
        MagicMock(rss=100 * mb),
        MagicMock(rss=101 * mb),
    ]
    mock_psutil.Process.return_value = mock_process
    client, pipeline = _make_client()

    with measure("block", track_memory_usage=True, client=client):
        pass

    expected_tags = {"name": "block", "status": "success"}
    pipeline.timing.assert_any_call("plugins.rss_delta_in_bytes", delta=1 * mb, tags=expected_tags)


@patch("canvas_sdk.utils.metrics.log")
@patch(
    "canvas_sdk.utils.plugins.is_plugin_caller",
    return_value=(True, "test_plugin.protocols.handler"),
)
@patch("canvas_sdk.utils.metrics.psutil")
@patch("canvas_sdk.utils.metrics.time")
def test_memory_excessive_growth_logs_warning(
    mock_time: MagicMock, mock_psutil: MagicMock, _mock_caller: MagicMock, mock_log: MagicMock
) -> None:
    """RSS growth above threshold should trigger a warning."""
    mock_time.perf_counter_ns.side_effect = [0, 0]
    mb = 1024 * 1024
    mock_process = MagicMock()
    mock_process.memory_info.side_effect = [
        MagicMock(rss=100 * mb),
        MagicMock(rss=110 * mb),  # 10 MB growth, default threshold is 5 MB
    ]
    mock_psutil.Process.return_value = mock_process
    client, pipeline = _make_client()

    with measure("block", track_memory_usage=True, client=client):
        pass

    mock_log.warning.assert_called_once()
    assert "Excessive memory growth" in mock_log.warning.call_args.args[0]


@patch("canvas_sdk.utils.metrics.log")
@patch("canvas_sdk.utils.metrics.psutil")
@patch("canvas_sdk.utils.metrics.time")
def test_memory_below_threshold_no_warning(
    mock_time: MagicMock, mock_psutil: MagicMock, mock_log: MagicMock
) -> None:
    """RSS growth below threshold should not trigger a warning."""
    mock_time.perf_counter_ns.side_effect = [0, 0]
    mb = 1024 * 1024
    mock_process = MagicMock()
    mock_process.memory_info.side_effect = [
        MagicMock(rss=100 * mb),
        MagicMock(rss=101 * mb),  # 1 MB growth, below 5 MB threshold
    ]
    mock_psutil.Process.return_value = mock_process
    client, pipeline = _make_client()

    with measure("block", track_memory_usage=True, client=client):
        pass

    mock_log.warning.assert_not_called()


@patch("canvas_sdk.utils.metrics.log")
@patch(
    "canvas_sdk.utils.plugins.is_plugin_caller",
    return_value=(True, "test_plugin.protocols.handler"),
)
@patch("canvas_sdk.utils.metrics.psutil")
@patch("canvas_sdk.utils.metrics.time")
@patch.dict(os.environ, {"PLUGIN_MEMORY_GROWTH_THRESHOLD_MB": "2"})
def test_memory_threshold_respects_env_var(
    mock_time: MagicMock, mock_psutil: MagicMock, _mock_caller: MagicMock, mock_log: MagicMock
) -> None:
    """The warning threshold should be configurable via env var."""
    mock_time.perf_counter_ns.side_effect = [0, 0]
    mb = 1024 * 1024
    mock_process = MagicMock()
    mock_process.memory_info.side_effect = [
        MagicMock(rss=100 * mb),
        MagicMock(rss=103 * mb),  # 3 MB growth, above 2 MB threshold
    ]
    mock_psutil.Process.return_value = mock_process
    client, pipeline = _make_client()

    with measure("block", track_memory_usage=True, client=client):
        pass

    mock_log.warning.assert_called_once()
