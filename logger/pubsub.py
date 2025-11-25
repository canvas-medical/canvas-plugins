import logging
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


__exports__ = ()
