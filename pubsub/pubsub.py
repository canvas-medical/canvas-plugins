import os
from typing import Any

import redis
from redis.backoff import ExponentialBackoff
from redis.exceptions import ConnectionError, TimeoutError
from redis.retry import Retry

REDIS_ENDPOINT = os.getenv("REDIS_ENDPOINT")
CUSTOMER_IDENTIFIER = os.getenv("CUSTOMER_IDENTIFIER")
CHANNEL_SUFFIX = "plugin-logging-stream"


class PubSubBase:
    """Base class for pub/sub."""

    def __init__(self) -> None:
        self.channel = self._get_channel_name()
        # The endpoint URL is passed straight to the client rather than kept, and the
        # client itself has no public name.
        self._client = self._create_client(REDIS_ENDPOINT)

    def _get_channel_name(self) -> str | None:
        if CUSTOMER_IDENTIFIER:
            return f"{CUSTOMER_IDENTIFIER}:{CHANNEL_SUFFIX}"

        return None

    def _create_client(self, redis_endpoint: str | None) -> redis.Redis | None:
        if redis_endpoint and self.channel:
            return redis.Redis.from_url(
                redis_endpoint,
                decode_responses=True,
                retry=Retry(backoff=ExponentialBackoff(), retries=10),
                retry_on_error=[ConnectionError, TimeoutError, ConnectionResetError],
                health_check_interval=1,
                socket_keepalive=True,
            )

        return None


class Publisher(PubSubBase):
    """Publisher class for pub/sub."""

    def publish(self, message: Any) -> None:
        """Publishes a message to the channel."""
        if self._client and self.channel:
            self._client.publish(self.channel, message)
