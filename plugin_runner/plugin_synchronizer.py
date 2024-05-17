#!/usr/bin/env python

import os
import pickle

from pathlib import Path
from subprocess import CalledProcessError, check_output, STDOUT

import redis

APP_NAME = os.getenv("APP_NAME")

PLUGINS_PUBSUB_CHANNEL = os.getenv("PLUGINS_PUBSUB_CHANNEL", default="plugins")

REDIS_ENDPOINT = os.getenv("REDIS_ENDPOINT", f"redis://{APP_NAME}-redis:6379")

try:
    CLIENT_ID = Path("/app/container-unique-id.txt").read_text()
except FileNotFoundError:
    CLIENT_ID = "non-unique"


def get_client():
    client = redis.Redis.from_url(REDIS_ENDPOINT)
    pubsub = client.pubsub()

    return client, pubsub


def publish_message(message: dict) -> None:
    client, _ = get_client()

    message_with_id = {**message, "client_id": CLIENT_ID}

    client.publish(PLUGINS_PUBSUB_CHANNEL, pickle.dumps(message_with_id))
    client.close()


def main():
    print("plugin-synchronizer: starting")

    _, pubsub = get_client()

    pubsub.psubscribe(PLUGINS_PUBSUB_CHANNEL)

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
