import logging
import os
from typing import Any

import redis

from pubsub.pubsub import Publisher


class PubSubLogHandler(logging.Handler):
    """Custom logging handler that publishes logs to a pub/sub channel."""

    def __init__(self) -> None:
        self.publisher = Publisher()
        logging.Handler.__init__(self=self)

    def emit(self, record: Any) -> None:
        """Publishes the log message to the pub/sub channel."""
        message = self.format(record)

        try:
            self.publisher.publish(message)
        except redis.ConnectionError as e:
            print(f"PubSubLogHandler: failed to log message due to redis error: {e}")


class PluginLogger:
    """A custom logger for plugins."""

    def __init__(self) -> None:
        self.logger = logging.getLogger("plugin_runner_logger")
        self.logger.setLevel(logging.INFO)

        log_prefix = os.getenv("HOSTNAME", "")

        if log_prefix != "":
            log_prefix = f"[{log_prefix}] "

        formatter = logging.Formatter(
            f"plugin_runner {log_prefix}%(levelname)s %(asctime)s %(message)s"
        )

        streaming_handler = logging.StreamHandler()
        streaming_handler.setFormatter(formatter)

        self.logger.addHandler(streaming_handler)

        if os.getenv("REDIS_ENDPOINT"):
            pubsub_handler = PubSubLogHandler()
            pubsub_handler.setFormatter(formatter)

            self.logger.addHandler(pubsub_handler)

    def debug(self, message: Any) -> None:
        """Logs a debug message."""
        self.logger.debug(message)

    def info(self, message: Any) -> None:
        """Logs an info message."""
        self.logger.info(message)

    def warning(self, message: Any) -> None:
        """Logs a warning message."""
        self.logger.warning(message)

    def error(self, message: Any) -> None:
        """Logs an error message."""
        self.logger.error(message)

    def critical(self, message: Any) -> None:
        """Logs a critical message."""
        self.logger.critical(message)


__exports__ = ()
