from time import time
from typing import Any


def get_duration_ms(start_time: time) -> int:
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
