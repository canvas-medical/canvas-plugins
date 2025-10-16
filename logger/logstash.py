import contextlib
import datetime
import json
import logging
import re
import sys
import traceback
from logging import LogRecord
from types import TracebackType
from typing import Any

import requests
from django.conf import settings


class HttpTransport:
    """
    Send messages to Logstash in V1 format.
    """

    def __init__(self, host: str, **kwargs: Any) -> None:
        self.url = host

        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def send(self, events: list[Any], **kwargs: Any) -> None:
        """Send events to Logstash."""
        for event in events:
            try:
                self.session.post(self.url, data=event)
            except (KeyboardInterrupt, SystemExit):
                raise
            except BaseException as e:
                print("Logstash exception", e)

    def close(self) -> None:
        """Close the transport."""
        pass


ExcInfo = tuple[type[BaseException], BaseException, TracebackType | None]


def _figure_out_exc_info(v: Any) -> ExcInfo:
    """
    Depending on the Python version will try to do the smartest thing possible
    to transform *v* into an ``exc_info`` tuple.
    """
    if isinstance(v, BaseException):
        return v.__class__, v, v.__traceback__

    if isinstance(v, tuple):
        return v

    if v:
        return sys.exc_info()  # type: ignore[return-value]

    return v


def _json_default(obj: Any) -> str:
    """
    Coerce everything to strings. All objects representing time get output as
    ISO8601.
    """
    if isinstance(obj, datetime.datetime | datetime.date | datetime.time):
        return obj.isoformat()

    return str(obj)


class LogstashFormatterV1(logging.Formatter):
    """
    A custom formatter to prepare logs to be shipped out to logstash V1 format.
    """

    unwanted_fields = [
        "args",
        "created",
        "filename",
        "funcName",
        "levelno",
        "lineno",
        "module",
        "msecs",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "request",
        "response",
        "threadName",
    ]

    mappings = {
        "levelname": "log_level",
        "name": "log_name",
    }

    def __init__(self) -> None:
        super().__init__()

        self.defaults = {
            "app": "plugin-runner",
            "customer": settings.CUSTOMER_IDENTIFIER,
            "plugin_context": True,
        }

        self.source_host = settings.HOSTNAME

    @staticmethod
    def get_location(fields: dict) -> str:
        """
        Format the log location in a way that saves some bytes.
        """
        path = "?"

        if "pathname" in fields:
            path = re.sub(r"^/plugin-runner/", "", fields["pathname"])
            path = re.sub(r"^/usr/local/lib/python3.\d\d/dist-packages/", "", path)
            path = re.sub(r"^/venvs/plugin-runner/lib/python3.\d\d/site-packages/", "", path)
        elif "filename" in fields:
            path = fields["filename"]

        return "{}:{}".format(path, fields.get("lineno", "?"))

    @staticmethod
    def get_method(fields: dict) -> str:
        """
        Get the method that originated the log.
        """
        return "{}.{}:{}".format(
            fields.get("name", "?"), fields.get("module", "?"), fields.get("funcName", "?")
        )

    def format(self, record: LogRecord) -> str:
        """
        Format a log record to JSON, if the message is a dict assume an empty
        message and use the dict as additional fields.
        """
        fields = record.__dict__.copy()

        if "msg" in fields and isinstance(fields["msg"], dict):
            msg = fields.pop("msg")

            # if the dict has an "event" key, use that as the message
            # to avoid conflicts with other message types that use event as an object.
            if "event" in msg:
                fields["message"] = msg.pop("event")

            fields.update(msg)
        elif "msg" in fields and "message" not in fields:
            msg = record.getMessage()

            del fields["msg"]

            with contextlib.suppress(KeyError, IndexError, ValueError):
                msg = msg.format(**fields)

            fields["message"] = msg

        if "exc_info" in fields:
            if fields["exc_info"]:
                exc_info = _figure_out_exc_info(fields["exc_info"])
                fields["exception_message"] = str(exc_info[1])
                fields["exception_type"] = f"{exc_info[0].__module__}.{exc_info[0].__qualname__}"
                fields["stack_trace"] = traceback.format_exception(*exc_info)
            del fields["exc_info"]

        if "exc_text" in fields and not fields["exc_text"]:
            del fields["exc_text"]

        now = datetime.datetime.now(datetime.UTC)

        base_log = {
            "@timestamp": now.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "@version": 1,
            "location": self.get_location(fields),
            "method": self.get_method(fields),
            "source_host": self.source_host,
        }

        for field in self.unwanted_fields:
            if field in fields:
                del fields[field]

        # Remove None fields (like `params` most of the time) and empty
        # argument lists (like `args` most of the time)
        fields = {key: value for key, value in fields.items() if value is not None and value != []}

        # Rename fields with mapping set
        for old_name, new_name in self.mappings.items():
            if old_name in fields:
                fields[new_name] = fields.pop(old_name)

        base_log.update(fields)

        log_record = self.defaults.copy()
        log_record.update(base_log)

        return json.dumps(log_record, default=_json_default)


class LogstashFormatterECS(logging.Formatter):
    """
    A custom formatter to prepare logs to be shipped out to logstash ECS format.
    """

    def __init__(self) -> None:
        super().__init__()

        self.defaults = {
            "service": {"name": "plugin-runner"},
            "labels": {"customer": settings.CUSTOMER_IDENTIFIER},
            "host": {"name": settings.HOSTNAME},
        }

    def format(self, record: LogRecord) -> str:
        """
        Format a log record to JSON, if the message is a dict assume an empty
        message and use the dict as additional fields.
        """
        fields = record.__dict__.copy()

        if "msg" in fields and isinstance(fields["msg"], dict):
            msg = fields.pop("msg")

            # if the dict has an "event" key, use that as the message
            # to avoid conflicts with other message types that use event as an object.
            if "event" in msg:
                fields["message"] = msg.pop("event")

            fields.update(msg)
        elif "msg" in fields and "message" not in fields:
            msg = record.getMessage()

            del fields["msg"]

            with contextlib.suppress(KeyError, IndexError, ValueError):
                msg = msg.format(**fields)

            fields["message"] = msg

        if "exc_info" in fields:
            if fields["exc_info"]:
                exc_info = _figure_out_exc_info(fields["exc_info"])
                fields["exception_message"] = str(exc_info[1])
                fields["exception_type"] = f"{exc_info[0].__module__}.{exc_info[0].__qualname__}"
                fields["stack_trace"] = traceback.format_exception(*exc_info)
            del fields["exc_info"]

        if "exc_text" in fields and not fields["exc_text"]:
            del fields["exc_text"]

        now = datetime.datetime.now(datetime.UTC)

        log_record = {
            **self.defaults,
            "@timestamp": now.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "message": fields.get("message", ""),
            "log": {
                "level": fields.get("levelname", ""),
            },
            **(
                {
                    "error": {
                        "message": fields["exception_message"],
                        "type": fields["exception_type"],
                        "stack_trace": fields["stack_trace"],
                    }
                }
                if "exception_message" in fields
                else {}
            ),
        }

        return json.dumps(log_record, default=_json_default)


__exports__ = ()
