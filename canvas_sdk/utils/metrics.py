import time
from collections.abc import Callable, Generator
from contextlib import contextmanager
from datetime import timedelta
from functools import wraps
from typing import Any, TypeVar, cast, overload

from django.conf import settings
from statsd.client.base import StatsClientBase
from statsd.client.udp import Pipeline
from statsd.defaults.env import statsd as default_statsd_client

LINE_PROTOCOL_TRANSLATION = str.maketrans(
    {
        ",": r"\,",
        "=": r"\=",
        " ": r"\ ",
        ":": r"__",
    }
)


def tags_to_line_protocol(tags: dict[str, Any]) -> str:
    """Generate a tags string compatible with the InfluxDB line protocol.

    See: https://docs.influxdata.com/influxdb/v1.1/write_protocols/line_protocol_tutorial/
    """
    return ",".join(
        f"{tag_name}={str(tag_value).translate(LINE_PROTOCOL_TRANSLATION)}"
        for tag_name, tag_value in tags.items()
    )


def get_qualified_name(fn: Callable) -> str:
    """Get the qualified name of a function."""
    return f"{fn.__module__}.{fn.__qualname__}"


class StatsDClientProxy:
    """Proxy for a StatsD client."""

    def __init__(self) -> None:
        self.client = default_statsd_client

    def gauge(self, metric_name: str, value: float, tags: dict[str, str]) -> None:
        """Sends a gauge metric to StatsD with properly formatted tags.

        Args:
            metric_name (str): The name of the metric.
            value (float): The value to report.
            tags (dict[str, str]): Dictionary of tags to attach to the metric.
        """
        if not settings.METRICS_ENABLED:
            return

        statsd_tags = tags_to_line_protocol(tags)
        self.client.gauge(f"{metric_name},{statsd_tags}", value)

    def timing(self, metric_name: str, delta: float | timedelta, tags: dict[str, str]) -> None:
        """Sends a timing metric to StatsD with properly formatted tags.

        Args:
            metric_name (str): The name of the metric.
            delta (float | timedelta): The value to report.
            tags (dict[str, str]): Dictionary of tags to attach to the metric.
        """
        if not settings.METRICS_ENABLED:
            return

        statsd_tags = tags_to_line_protocol(tags)
        self.client.timing(f"{metric_name},{statsd_tags}", delta)

    def incr(self, metric_name: str, tags: dict[str, str], count: int = 1, rate: int = 1) -> None:
        """Sends an increment metric to StatsD with properly formatted tags.

        Args:
            metric_name (str): The name of the metric.
            count (int): The increment to report.
            rate (int): The sample rate.
            tags (dict[str, str]): Dictionary of tags to attach to the metric.
        """
        if not settings.METRICS_ENABLED:
            return

        statsd_tags = tags_to_line_protocol(tags)
        self.client.incr(f"{metric_name},{statsd_tags}", count, rate)

    def pipeline(self) -> "PipelineProxy":
        """Returns a pipeline for batching StatsD metrics."""
        return PipelineProxy(self.client)


class PipelineProxy(StatsDClientProxy):
    """Proxy for a StatsD pipeline."""

    def __init__(self, client: StatsClientBase | None) -> None:
        super().__init__()
        self.client = Pipeline(client or self.client)

    def send(self) -> None:
        """Sends the batched metrics to StatsD."""
        if not settings.METRICS_ENABLED:
            return

        self.client.send()


statsd_client = StatsDClientProxy()


@contextmanager
def measure(
    name: str,
    extra_tags: dict[str, str] | None = None,
    client: StatsDClientProxy | None = None,
    track_plugins_usage: bool = False,
) -> Generator[PipelineProxy, None, None]:
    """A context manager for collecting metrics about a context block.

    Args:
        name: The name of the block being measured (added as a StatsD tag)
        extra_tags: A dict of extra tags to be added to all recorded metrics.
        client: An optional alternate StatsD client.
        track_plugins_usage: Whether to track plugin usage (Adds plugin and handler tags if the caller was a plugin).

    Yields:
        A pipeline for collecting additional metrics in the same batch.
    """
    client = client or statsd_client

    if track_plugins_usage:
        from canvas_sdk.utils.plugins import is_plugin_caller

        is_plugin, caller = is_plugin_caller()
        if is_plugin and caller:
            extra_tags = extra_tags or {}
            extra_tags["plugin"] = caller.split(".")[0]
            extra_tags["handler"] = caller

    tags = {"name": name, **(extra_tags or {})}

    pipeline = client.pipeline()
    timing_start = time.perf_counter_ns()
    try:
        yield pipeline
    except BaseException as ex:
        tags = {**tags, "status": "error"}
        raise ex
    else:
        tags = {**tags, "status": "success"}
    finally:
        duration_ms = (time.perf_counter_ns() - timing_start) / 1_000_000
        pipeline.timing("plugins.timings", duration_ms, tags=tags)
        pipeline.incr("plugins.executions", tags=tags)
        pipeline.send()


F = TypeVar("F", bound=Callable)


@overload
def measured(fn: F) -> F: ...


@overload
def measured(**options: Any) -> Callable[[F], F]: ...


def measured(fn: F | None = None, **options: Any) -> Callable[[F], F] | F:
    """Collect metrics about the decorated function.

    Args:
        fn: The decorated function.
        options: Additional options for the decorator, such as `client` and `extra_tags`.

    Returns:
        A decorated function if called without arguments (@measured), or a
        decorator if called with arguments (@measured(client=...))
    """

    def _decorator(fn: F) -> F:
        @wraps(fn)
        def _wrapped(*args: Any, **kwargs: Any) -> Any:
            with measure(get_qualified_name(fn), **options):
                return fn(*args, **kwargs)

        return cast(F, _wrapped)

    return _decorator(fn) if fn else _decorator


__exports__ = ()
