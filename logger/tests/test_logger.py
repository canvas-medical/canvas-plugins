"""Tests for plugin name / handler name propagation in plugin-runner logging.

Covers the contextvar-based binding (``plugin_context``), the per-record
filter that surfaces the names onto ``LogRecord`` instances, and the ECS
formatter's ``labels.plugin`` / ``labels.handler`` emission.
"""

import json
import logging

from logger.logger import (
    PluginNameFilter,
    _current_handler_name,
    _current_plugin_name,
    plugin_context,
)
from logger.logstash import LogstashFormatterECS


def test_plugin_context_binds_handler_and_derived_plugin_name() -> None:
    """``plugin_context(handler_name)`` binds the handler verbatim and the
    plugin folder derived from its leading dotted segment.
    """
    with plugin_context("my_plugin.handlers.foo.MyHandler"):
        assert _current_handler_name.get() == "my_plugin.handlers.foo.MyHandler"
        assert _current_plugin_name.get() == "my_plugin"

    # Both vars are released on exit so unrelated callers see a clean slate.
    assert _current_handler_name.get() is None
    assert _current_plugin_name.get() is None


def test_plugin_context_is_noop_for_falsy_input() -> None:
    """Passing ``None`` (or empty string) doesn't bind anything — callers can
    feed through optional values without guarding.
    """
    with plugin_context(None):
        assert _current_handler_name.get() is None
        assert _current_plugin_name.get() is None

    with plugin_context(""):
        assert _current_handler_name.get() is None
        assert _current_plugin_name.get() is None


def test_plugin_context_nested_inner_overrides_outer() -> None:
    """Nested blocks swap both vars on entry and restore on exit."""
    with plugin_context("plugin_a.Handler"):
        assert _current_plugin_name.get() == "plugin_a"

        with plugin_context("plugin_b.Other"):
            assert _current_plugin_name.get() == "plugin_b"
            assert _current_handler_name.get() == "plugin_b.Other"

        # Outer values restored after the inner block exits.
        assert _current_plugin_name.get() == "plugin_a"
        assert _current_handler_name.get() == "plugin_a.Handler"


def _make_record() -> logging.LogRecord:
    """Build a minimal LogRecord for filter/formatter tests."""
    return logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="hello",
        args=(),
        exc_info=None,
    )


def test_plugin_name_filter_populates_attributes_inside_plugin_context() -> None:
    """While ``plugin_context`` is active the filter writes plugin/handler
    names plus the streaming-format prefix string onto the record.
    """
    record = _make_record()
    name_filter = PluginNameFilter()

    with plugin_context("my_plugin.handlers.MyHandler"):
        assert name_filter.filter(record) is True

    assert record.plugin_name == "my_plugin"  # type: ignore[attr-defined]
    assert record.handler_name == "my_plugin.handlers.MyHandler"  # type: ignore[attr-defined]
    assert record.plugin_name_prefix == "[my_plugin] "  # type: ignore[attr-defined]


def test_plugin_name_filter_outside_plugin_context() -> None:
    """Without an active plugin the filter sets ``plugin_name``/``handler_name``
    to None and emits an empty prefix so the format template stays
    interpolation-safe.
    """
    record = _make_record()
    name_filter = PluginNameFilter()

    assert name_filter.filter(record) is True
    assert record.plugin_name is None  # type: ignore[attr-defined]
    assert record.handler_name is None  # type: ignore[attr-defined]
    assert record.plugin_name_prefix == ""  # type: ignore[attr-defined]


def test_logstash_formatter_emits_labels_plugin_and_handler() -> None:
    """ECS output carries ``labels.plugin`` and ``labels.handler`` (alongside
    the static ``labels.customer`` default) when both are bound.
    """
    formatter = LogstashFormatterECS()
    record = _make_record()
    PluginNameFilter().filter(record)  # baseline (no plugin context)

    with plugin_context("my_plugin.handlers.MyHandler"):
        # Re-run the filter with plugin_context active; in production the
        # logger-level filter does this automatically before the formatter.
        record = _make_record()
        PluginNameFilter().filter(record)
        output = json.loads(formatter.format(record))

    assert output["labels"]["plugin"] == "my_plugin"
    assert output["labels"]["handler"] == "my_plugin.handlers.MyHandler"
    # The static customer label survives the merge.
    assert "customer" in output["labels"]


def test_logstash_formatter_omits_plugin_labels_when_no_plugin_context() -> None:
    """Without an active plugin the ECS output keeps only the static labels
    (no spurious ``plugin``/``handler`` keys).
    """
    formatter = LogstashFormatterECS()
    record = _make_record()
    PluginNameFilter().filter(record)

    output = json.loads(formatter.format(record))

    assert "plugin" not in output.get("labels", {})
    assert "handler" not in output.get("labels", {})
