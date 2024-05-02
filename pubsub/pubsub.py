import redis


# replace with home-app env variables
# i.e. os.getenv("REDIS_ENDPOINT")
HOST = 'localhost'
PORT = 6399
CHANNEL = 'myinstance'


class PubSubBase:
    def __init__(self) -> None:
        self.host = HOST
        self.port = PORT
        self.channel = CHANNEL
        self.client = self._create_client()

    def _create_client(self):
        return redis.StrictRedis(host=self.host, port=self.port)


class Publisher(PubSubBase):
    def publish(self, message):
        self.client.publish(self.channel, message)


class Subscriber(PubSubBase):
    def subscribe(self):
        ps = self.client.pubsub()
        ps.subscribe(self.channel)
        for msg in ps.listen():
            if msg["type"] == "message":
                print(msg["data"])


