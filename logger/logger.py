import logging
import os
from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any

from django.conf import settings
from logstash_async.handler import AsynchronousLogstashHandler

from logger.logstash import LogstashFormatterECS
from logger.pubsub import PubSubLogHandler

_current_handler_name: ContextVar[str | None] = ContextVar("_current_handler_name", default=None)
_current_plugin_name: ContextVar[str | None] = ContextVar("_current_plugin_name", default=None)


@contextmanager
def plugin_context(handler_name: str | None) -> Generator[None, None, None]:
    """Bind the active plugin's handler name (and derived plugin name)."""
    if not handler_name:
        yield
        return
    plugin_name = handler_name.split(".", 1)[0] or None
    handler_token = _current_handler_name.set(handler_name)
    plugin_token = _current_plugin_name.set(plugin_name)
    try:
        yield
    finally:
        _current_plugin_name.reset(plugin_token)
        _current_handler_name.reset(handler_token)


class PluginNameFilter(logging.Filter):
    """Surface active plugin/handler names onto each ``LogRecord``.

    Writes:

    - ``record.plugin_name`` — used by the logstash formatters to emit
      ``labels.plugin``.
    - ``record.handler_name`` — used by the logstash formatters to emit
      ``labels.handler``.
    - ``record.plugin_name_prefix`` — the literal ``"[<plugin_name>] "``
      referenced by the streaming/pub-sub format template; empty string
      when no plugin is active so the template stays interpolation-safe
      either way.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """Populate plugin/handler name fields from the current context vars."""
        plugin_name = _current_plugin_name.get()
        handler_name = _current_handler_name.get()
        record.plugin_name = plugin_name
        record.handler_name = handler_name
        record.plugin_name_prefix = f"[{plugin_name}] " if plugin_name else ""
        return True


class PluginLogger:
    """A custom logger for plugins."""

    def __init__(self) -> None:
        self.logger = logging.getLogger("plugin_runner_logger")
        self.logger.setLevel(logging.INFO)
        self.logger.addFilter(PluginNameFilter())

        log_prefix = f"{os.getenv('HOSTNAME', '?')}: {os.getenv('APTIBLE_PROCESS_INDEX', '?')}"

        if log_prefix != "":
            log_prefix = f"[{log_prefix}] "

        formatter = logging.Formatter(
            f"plugin-runner {log_prefix}%(plugin_name_prefix)s%(levelname)s %(asctime)s %(message)s"
        )

        streaming_handler = logging.StreamHandler()
        streaming_handler.setFormatter(formatter)

        self.logger.addHandler(streaming_handler)

        if settings.REDIS_ENDPOINT:
            pubsub_handler = PubSubLogHandler()
            pubsub_handler.setFormatter(formatter)

            self.logger.addHandler(pubsub_handler)

        if settings.LOGSTASH_HOST:
            logstash_handler = AsynchronousLogstashHandler(
                host=settings.LOGSTASH_HOST,
                port=settings.LOGSTASH_PORT,
                database_path=None,
                transport=settings.LOGSTASH_PROTOCOL,
            )
            logstash_handler.setFormatter(LogstashFormatterECS())
            self.logger.addHandler(logstash_handler)

    def debug(self, message: Any, *args: Any, **kwargs: Any) -> None:
        """Logs a debug message."""
        self.logger.debug(message, *args, **kwargs)

    def info(self, message: Any, *args: Any, **kwargs: Any) -> None:
        """Logs an info message."""
        self.logger.info(message, *args, **kwargs)

    def warning(self, message: Any, *args: Any, **kwargs: Any) -> None:
        """Logs a warning message."""
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: Any, *args: Any, **kwargs: Any) -> None:
        """Logs an error message."""
        self.logger.error(message, *args, **kwargs)

    def exception(self, message: Any, *args: Any, **kwargs: Any) -> None:
        """Convenience method for logging an ERROR with exception information."""
        self.logger.exception(message, *args, **kwargs)

    def critical(self, message: Any, *args: Any, **kwargs: Any) -> None:
        """Logs a critical message."""
        self.logger.critical(message)


__exports__ = ()
