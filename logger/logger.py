import logging
import os
from typing import Any

from django.conf import settings
from logstash_async.handler import AsynchronousLogstashHandler

from logger.logstash import LogstashFormatterECS
from logger.pubsub import PubSubLogHandler


class PluginLogger:
    """A custom logger for plugins."""

    def __init__(self) -> None:
        self.logger = logging.getLogger("plugin_runner_logger")
        self.logger.setLevel(logging.INFO)

        log_prefix = f"{os.getenv('HOSTNAME', '?')}: {os.getenv('APTIBLE_PROCESS_INDEX', '?')}"

        if log_prefix != "":
            log_prefix = f"[{log_prefix}] "

        formatter = logging.Formatter(
            f"plugin-runner {log_prefix}%(levelname)s %(asctime)s %(message)s"
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
