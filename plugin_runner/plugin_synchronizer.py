# import os
#
# import settings
# from logger import log
# from plugin_runner import load_plugins
# from plugin_runner.plugin_installer import install_plugins

# from plugin_runner.plugin_runner import load_plugins

# APP_NAME = os.getenv("APP_NAME")
#
# CUSTOMER_IDENTIFIER = os.getenv("CUSTOMER_IDENTIFIER")
# PLUGINS_PUBSUB_CHANNEL = os.getenv("PLUGINS_PUBSUB_CHANNEL", default="plugins")
#
# CHANNEL_NAME = f"{CUSTOMER_IDENTIFIER}:{PLUGINS_PUBSUB_CHANNEL}"
#
# REDIS_ENDPOINT = os.getenv("REDIS_ENDPOINT", f"redis://{APP_NAME}-redis:6379")


# def get_client() -> tuple[redis.Redis, redis.client.PubSub]:
#     """Return a Redis client and pubsub object."""
#     client = redis.Redis.from_url(REDIS_ENDPOINT)
#     pubsub = client.pubsub()
#
#     return client, pubsub


# async def publish_message(message: dict) -> None:
#     """Publish a message to the pubsub channel."""
#     client, _ = await get_client()
#
#     await client.publish(CHANNEL_NAME, pickle.dumps(message))
#     client.close()
#
#
# import pickle
#
# import redis
#
# CHANNEL_NAME = f"{settings.CUSTOMER_IDENTIFIER}:{settings.PLUGINS_PUBSUB_CHANNEL}"
# REDIS_ENDPOINT = os.getenv("REDIS_ENDPOINT", f"redis://{settings.APP_NAME}-redis:6379")
#
#
# def get_client() -> tuple[redis.Redis, redis.client.PubSub]:
#     """Return an async Redis client and pubsub object."""
#     client = redis.Redis.from_url(settings.REDIS_ENDPOINT)
#     pubsub = client.pubsub()
#
#     return client, pubsub
#
#
# async def synchronize_plugins() -> None:
#     """Listen for messages on the pubsub channel asynchronously."""
#     client, pubsub = get_client()
#     pubsub.psubscribe(CHANNEL_NAME)
#
#     async for message in pubsub.listen():
#         if not message:
#             continue
#
#         message_type = message.get("type", "")
#
#         if message_type != "pmessage":
#             continue
#
#         data = pickle.loads(message.get("data", pickle.dumps({})))
#
#         if "action" not in data:
#             continue
#
#         if data["action"] == "reload":
#             try:
#                 log.info("plugin-synchronizer: installing plugins after receiving restart message")
#                 install_plugins()
#                 load_plugins()
#             except Exception as e:
#                 print("plugin-synchronizer: `install_plugins` failed:", e)
#
#     await client.close()
#     await client.wait_closed()


# def main() -> None:
#     """Listen for messages on the pubsub channel and restart the plugin-runner."""
#     print("plugin-synchronizer: starting")
#     try:
#         print("plugin-synchronizer: installing plugins after web container start")
#         install_plugins()
#         load_plugins()
#     except CalledProcessError as e:
#         print("plugin-synchronizer: `install_plugins` failed:", e)
#
#     _, pubsub = get_client()
#
#     pubsub.psubscribe(CHANNEL_NAME)
#
#     for message in pubsub.listen():
#         if not message:
#             continue
#
#         message_type = message.get("type", "")
#
#         if message_type != "pmessage":
#             continue
#
#         data = pickle.loads(message.get("data", pickle.dumps({})))
#
#         if "action" not in data:
#             continue
#
#         if data["action"] == "reload":
#             try:
#                 log.info("plugin-synchronizer: installing plugins after receiving restart message")
#                 install_plugins()
#                 load_plugins()
#             except Exception as e:
#                 print("plugin-synchronizer: `install_plugins` failed:", e)
#
# try:
#     print("plugin-synchronizer: sending SIGHUP to plugin-runner")
#     check_output(
#         ["circusctl", "signal", "plugin-runner", "1"], cwd="/app", stderr=STDOUT
#     )
# except CalledProcessError as e:
#     print("plugin-synchronizer: `circusctl signal plugin-runner 1` failed:", e)


# if __name__ == "__main__":
#     main()
