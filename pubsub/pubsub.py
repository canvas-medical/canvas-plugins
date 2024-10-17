import os
from typing import Any

import redis

REDIS_ENDPOINT = os.getenv("REDIS_ENDPOINT")
CUSTOMER_IDENTIFIER = os.getenv("CUSTOMER_IDENTIFIER")
CHANNEL_SUFFIX = "plugin-logging-stream"


class PubSubBase:
    """Base class for pub/sub."""

    def __init__(self) -> None:
        self.redis_endpoint = REDIS_ENDPOINT
        self.channel = self._get_channel_name()
        self.client = self._create_client()

    def _get_channel_name(self) -> str | None:
        if CUSTOMER_IDENTIFIER:
            return f"{CUSTOMER_IDENTIFIER}:{CHANNEL_SUFFIX}"

        return None

    def _create_client(self) -> redis.Redis | None:
        if self.redis_endpoint and self.channel:
            return redis.Redis.from_url(self.redis_endpoint, decode_responses=True)

        return None


class Publisher(PubSubBase):
    """Publisher class for pub/sub."""

    def publish(self, message: Any) -> None:
        """Publishes a message to the channel."""
        if self.client and self.channel:
            self.client.publish(self.channel, message)
