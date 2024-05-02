import logging

from pubsub.pubsub import Publisher

# Make this a flag when running the plugin runner.
# IS_DEVELOPMENT=True will log to the console.
# IS_DEVELOPMENT=False will publish to Redis.

IS_DEVELOPMENT = False


class PubSubLogHandler(logging.Handler):
    def __init__(self)-> None:
        self.publisher = Publisher()
        logging.Handler.__init__(self=self)

    def emit(self, record) -> None:
        message = self.format(record)
        self.publisher.publish(message)


class PluginLogger:
    def __init__(self) -> None:
        self.logger = logging.getLogger("plugin_runner_logger")
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(levelname)s %(asctime)s %(message)s')

        streaming_handler = logging.StreamHandler()
        streaming_handler.setFormatter(formatter)
        self.logger.addHandler(streaming_handler)

        if not IS_DEVELOPMENT:
            pubsub_handler = PubSubLogHandler()
            pubsub_handler.setFormatter(formatter)
            self.logger.addHandler(pubsub_handler)

    def debug(self, message) -> None:
        self.logger.debug(message)

    def info(self,message) -> None:
        self.logger.info(message)

    def warning(self, message) -> None:
        self.logger.warning(message)

    def error(self, message) -> None:
        self.logger.error(message)

    def critical(self, message) -> None:
        self.logger.critical(message)
