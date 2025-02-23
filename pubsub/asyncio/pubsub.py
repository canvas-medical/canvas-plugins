from typing import Any

import redis.asyncio as redis

from pubsub.pubsub import PubSubBase


class Publisher(PubSubBase):
    """Publisher class for pub/sub."""

    def _create_client(self) -> redis.Redis | None:
        if self.redis_endpoint and self.channel:
            return redis.Redis.from_url(self.redis_endpoint, decode_responses=True)

        return None

    async def publish(self, message: Any) -> None:
        """Publishes a message to the channel."""
        if self.client and self.channel:
            await self.client.publish(self.channel, message)
