#!/usr/bin/env python

import os
import pickle
from pathlib import Path
from subprocess import STDOUT, CalledProcessError, check_output

import redis

APP_NAME = os.getenv("APP_NAME")

CUSTOMER_IDENTIFIER = os.getenv("CUSTOMER_IDENTIFIER")
PLUGINS_PUBSUB_CHANNEL = os.getenv("PLUGINS_PUBSUB_CHANNEL", default="plugins")

CHANNEL_NAME = f"{CUSTOMER_IDENTIFIER}:{PLUGINS_PUBSUB_CHANNEL}"

REDIS_ENDPOINT = os.getenv("REDIS_ENDPOINT", f"redis://{APP_NAME}-redis:6379")

try:
    CLIENT_ID = Path("/app/container-unique-id.txt").read_text()
except FileNotFoundError:
    CLIENT_ID = "non-unique"


def get_client() -> tuple[redis.Redis, redis.client.PubSub]:
    """Return a Redis client and pubsub object."""
    client = redis.Redis.from_url(REDIS_ENDPOINT)
    pubsub = client.pubsub()

    return client, pubsub


def publish_message(message: dict) -> None:
    """Publish a message to the pubsub channel."""
    client, _ = get_client()

    message_with_id = {**message, "client_id": CLIENT_ID}

    client.publish(CHANNEL_NAME, pickle.dumps(message_with_id))
    client.close()


def main() -> None:
    """Listen for messages on the pubsub channel and restart the plugin-runner."""
    print("plugin-synchronizer: starting")

    _, pubsub = get_client()

    pubsub.psubscribe(CHANNEL_NAME)

    for message in pubsub.listen():
        if not message:
            continue

        message_type = message.get("type", "")

        if message_type != "pmessage":
            continue

        data = pickle.loads(message.get("data", pickle.dumps({})))

        if "action" not in data or "client_id" not in data:
            return

        # Don't respond to our own messages
        if data["client_id"] == CLIENT_ID:
            return

        if data["action"] == "restart":
            # Run the plugin installer process
            try:
                print("plugin-synchronizer: installing plugins")
                check_output(["./manage.py", "install_plugins_v2"], cwd="/app", stderr=STDOUT)
            except CalledProcessError as e:
                print("plugin-synchronizer: `./manage.py install_plugins_v2` failed:", e)

            try:
                print("plugin-synchronizer: sending SIGHUP to plugin-runner")
                check_output(
                    ["circusctl", "signal", "plugin-runner", "1"], cwd="/app", stderr=STDOUT
                )
            except CalledProcessError as e:
                print("plugin-synchronizer: `circusctl signal plugin-runner 1` failed:", e)


if __name__ == "__main__":
    main()
