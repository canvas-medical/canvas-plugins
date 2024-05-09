import redis
import os


REDIS_ENDPOINT = os.getenv("REDIS_ENDPOINT")
CUSTOMER_IDENTIFIER = os.getenv("CUSTOMER_IDENTIFIER")
CHANNEL_SUFFIX = "pluging-logging-stream"


class PubSubBase:
    def __init__(self) -> None:
        self.redis_endpoint = REDIS_ENDPOINT
        self.channel = self._get_channel_name()
        self.client = self._create_client()

    def _get_channel_name(self) -> str | None:
        if CUSTOMER_IDENTIFIER:
            return f"{CUSTOMER_IDENTIFIER}:{CHANNEL_SUFFIX}"

    def _create_client(self) -> redis.Redis | None:
        if self.redis_endpoint and self.channel:
            return redis.Redis.from_url(self.redis_endpoint, decode_responses=True)


class Publisher(PubSubBase):
    def publish(self, message) -> None:
        if self.client and self.channel:
            self.client.publish(self.channel, message)
