import logging
import os
from logging.handlers import SocketHandler


class PluginLogger:
    def __init__(self) -> None:
        self.logger = logging.getLogger("plugin_runner_logger")
        self.logger.setLevel(logging.INFO)
        log_prefix = os.getenv("HOSTNAME", "")
        if log_prefix != "":
            log_prefix = f"[{log_prefix}] "
        formatter = logging.Formatter(f"{log_prefix}%(levelname)s %(asctime)s %(message)s")

        streaming_handler = logging.StreamHandler()
        streaming_handler.setFormatter(formatter)
        self.logger.addHandler(streaming_handler)

        socket_handler = SocketHandler(
            "localhost",
            os.getenv(
                "PLUGIN_RUNNER_LOG_PORT",
                6521,
            ),
        )
        socket_handler.setFormatter(formatter)
        self.logger.addHandler(socket_handler)

    def debug(self, message) -> None:
        self.logger.debug(message)

    def info(self, message) -> None:
        self.logger.info(message)

    def warning(self, message) -> None:
        self.logger.warning(message)

    def error(self, message) -> None:
        self.logger.error(message)

    def critical(self, message) -> None:
        self.logger.critical(message)
