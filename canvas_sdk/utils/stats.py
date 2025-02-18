from datetime import timedelta
from time import time
from typing import Any

from statsd.defaults.env import statsd as default_statsd_client


def get_duration_ms(start_time: float) -> int:
    """Get the duration in milliseconds since the given start time."""
    return int((time() - start_time) * 1000)


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
        statsd_tags = tags_to_line_protocol(tags)
        self.client.gauge(f"{metric_name},{statsd_tags}", value)

    def timing(self, metric_name: str, delta: float | timedelta, tags: dict[str, str]) -> None:
        """Sends a timing metric to StatsD with properly formatted tags.

        Args:
            metric_name (str): The name of the metric.
            delta (float | timedelta): The value to report.
            tags (dict[str, str]): Dictionary of tags to attach to the metric.
        """
        statsd_tags = tags_to_line_protocol(tags)
        self.client.timing(f"{metric_name},{statsd_tags}", delta)


statsd_client = StatsDClientProxy()
