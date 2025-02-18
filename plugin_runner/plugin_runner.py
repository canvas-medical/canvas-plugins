import asyncio
import json
import os
import pathlib
import pickle
import pkgutil
import sys
import time
import traceback
from collections import defaultdict
from collections.abc import AsyncGenerator
from typing import Any, TypedDict

import grpc
import redis.asyncio as redis

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_generated.messages.plugins_pb2 import ReloadPluginsRequest, ReloadPluginsResponse
from canvas_generated.services.plugin_runner_pb2_grpc import (
    PluginRunnerServicer,
    add_PluginRunnerServicer_to_server,
)
from canvas_sdk.effects import Effect
from canvas_sdk.events import Event, EventRequest, EventResponse, EventType
from canvas_sdk.protocols import ClinicalQualityMeasure
from canvas_sdk.utils.stats import get_duration_ms, statsd_client
from logger import log
from plugin_runner.authentication import token_for_plugin
from plugin_runner.installation import install_plugins
from plugin_runner.sandbox import Sandbox
from settings import (
    CHANNEL_NAME,
    MANIFEST_FILE_NAME,
    PLUGIN_DIRECTORY,
    REDIS_ENDPOINT,
    SECRETS_FILE_NAME,
)

# when we import plugins we'll use the module name directly so we need to add the plugin
# directory to the path
sys.path.append(PLUGIN_DIRECTORY)

# a global dictionary of loaded plugins
# TODO: create typings here for the subkeys
LOADED_PLUGINS: dict = {}

# a global dictionary of events to handler class names
EVENT_HANDLER_MAP: dict[str, list] = defaultdict(list)


class DataAccess(TypedDict):
    """DataAccess."""

    event: str
    read: list[str]
    write: list[str]


Protocol = TypedDict(
    "Protocol",
    {
        "class": str,
        "data_access": DataAccess,
    },
)


ApplicationConfig = TypedDict(
    "ApplicationConfig",
    {
        "class": str,
        "description": str,
        "icon": str,
        "scope": str,
    },
)


class Components(TypedDict):
    """Components."""

    protocols: list[Protocol]
    commands: list[dict]
    content: list[dict]
    effects: list[dict]
    views: list[dict]
    applications: list[ApplicationConfig]


class PluginManifest(TypedDict):
    """PluginManifest."""

    sdk_version: str
    plugin_version: str
    name: str
    description: str
    components: Components
    secrets: list[dict]
    tags: dict[str, str]
    references: list[str]
    license: str
    diagram: bool
    readme: str


class PluginRunner(PluginRunnerServicer):
    """This process runs provided plugins that register interest in incoming events."""

    sandbox: Sandbox

    async def HandleEvent(
        self, request: EventRequest, context: Any
    ) -> AsyncGenerator[EventResponse, None]:
        """This is invoked when an event comes in."""
        event_start_time = time.time()
        event = Event(request)
        event_type = event.type
        event_name = event.name
        relevant_plugins = EVENT_HANDLER_MAP[event_name]

        if event_type in [EventType.PLUGIN_CREATED, EventType.PLUGIN_UPDATED]:
            plugin_name = event.target.id
            # filter only for the plugin(s) that were created/updated
            relevant_plugins = [p for p in relevant_plugins if p.startswith(f"{plugin_name}:")]

        effect_list = []

        for plugin_name in relevant_plugins:
            plugin = LOADED_PLUGINS[plugin_name]
            handler_class = plugin["class"]
            base_plugin_name = plugin_name.split(":")[0]

            secrets = plugin.get("secrets", {})
            secrets["graphql_jwt"] = token_for_plugin(plugin_name=plugin_name, audience="home")

            try:
                handler = handler_class(event, secrets)
                classname = (
                    handler.__class__.__name__
                    if isinstance(handler, ClinicalQualityMeasure)
                    else None
                )

                compute_start_time = time.time()
                _effects = await asyncio.get_running_loop().run_in_executor(None, handler.compute)
                effects = [
                    Effect(
                        type=effect.type,
                        payload=effect.payload,
                        plugin_name=base_plugin_name,
                        classname=classname,
                    )
                    for effect in _effects
                ]

                effects = validate_effects(effects)

                apply_effects_to_context(effects, event=event)

                compute_duration = get_duration_ms(compute_start_time)

                log.info(f"{plugin_name}.compute() completed ({compute_duration} ms)")
                statsd_client.timing(
                    "plugins.protocol_duration_ms",
                    delta=compute_duration,
                    tags={"plugin": plugin_name},
                )
            except Exception as e:
                for error_line_with_newlines in traceback.format_exception(e):
                    for error_line in error_line_with_newlines.split("\n"):
                        log.error(error_line)
                continue

            effect_list += effects

        event_duration = get_duration_ms(event_start_time)

        # Don't log anything if a plugin handler didn't actually run.
        if relevant_plugins:
            log.info(f"Responded to Event {event_name} ({event_duration} ms)")
            statsd_client.timing(
                "plugins.event_duration_ms", delta=event_duration, tags={"event": event_name}
            )

        yield EventResponse(success=True, effects=effect_list)

    async def ReloadPlugins(
        self, request: ReloadPluginsRequest, context: Any
    ) -> AsyncGenerator[ReloadPluginsResponse, None]:
        """This is invoked when we need to reload plugins."""
        log.info("Reloading plugins...")
        try:
            await publish_message(message={"action": "reload"})
        except ImportError:
            yield ReloadPluginsResponse(success=False)
        else:
            yield ReloadPluginsResponse(success=True)


async def synchronize_plugins(run_once: bool = False) -> None:
    """
    Listen for messages on the pubsub channel that will indicate it is
    necessary to reinstall and reload plugins.
    """
    log.info(f'synchronize_plugins: listening for messages on pubsub channel "{CHANNEL_NAME}"')

    client, pubsub = get_client()
    await pubsub.psubscribe(CHANNEL_NAME)

    while True:
        message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=None)

        if message is not None:
            log.info(f'synchronize_plugins: received message from pubsub channel "{CHANNEL_NAME}"')

            message_type = message.get("type", "")

            if message_type != "pmessage":
                continue

            data = pickle.loads(message.get("data", pickle.dumps({})))

            if "action" not in data:
                continue

            if data["action"] == "reload":
                log.info("synchronize_plugins: installing and reloading plugins for action=reload")

                try:
                    install_plugins()
                except Exception as e:
                    # TODO capture_exception when Sentry is installed
                    log.error(f"synchronize_plugins: install_plugins failed: {e}")

                try:
                    load_plugins()
                except Exception as e:
                    # TODO capture_exception when Sentry is installed
                    log.error(f"synchronize_plugins: load_plugins failed: {e}")
        if run_once:
            break


async def synchronize_plugins_and_report_errors() -> None:
    """
    Run synchronize_plugins() in perpetuity and report any encountered errors.
    """
    log.info("Starting synchronize_plugins loop...")

    while True:
        try:
            await synchronize_plugins()
        except Exception as e:
            log.error(f"synchronize_plugins error: {e}")

        # don't crush redis if we're retrying in a tight loop
        await asyncio.sleep(0.5)


def validate_effects(effects: list[Effect]) -> list[Effect]:
    """Validates the effects based on predefined rules.

    Keeps only the first AUTOCOMPLETE_SEARCH_RESULTS effect and preserve all
    non-search-related effects.
    """
    seen_autocomplete = False
    validated_effects = []

    for effect in effects:
        if effect.type == EffectType.AUTOCOMPLETE_SEARCH_RESULTS:
            if seen_autocomplete:
                log.warning("Discarding additional AUTOCOMPLETE_SEARCH_RESULTS effect.")
                continue

            seen_autocomplete = True

        validated_effects.append(effect)

    return validated_effects


def apply_effects_to_context(effects: list[Effect], event: Event) -> Event:
    """Applies AUTOCOMPLETE_SEARCH_RESULTS effects to the event context.
    If we are dealing with a search event, we need to update the context with the search results.
    """
    event_name = event.name

    # Skip if the event is not a search event
    if not event_name.endswith("__PRE_SEARCH") and not event_name.endswith("__POST_SEARCH"):
        return event

    for effect in effects:
        if effect.type == EffectType.AUTOCOMPLETE_SEARCH_RESULTS:
            event.context["results"] = json.loads(effect.payload)
            # Stop processing effects if we've found a AUTOCOMPLETE_SEARCH_RESULTS
            break

    return event


def find_modules(base_path: pathlib.Path, prefix: str | None = None) -> list[str]:
    """Find all modules in the specified package path."""
    modules: list[str] = []

    for _, module_name, is_pkg in pkgutil.iter_modules(
        [base_path.as_posix()],
    ):
        if is_pkg:
            modules = modules + find_modules(
                base_path / module_name,
                prefix=f"{prefix}.{module_name}" if prefix else module_name,
            )
        else:
            modules.append(f"{prefix}.{module_name}" if prefix else module_name)

    return modules


def sandbox_from_module(base_path: pathlib.Path, module_name: str) -> Any:
    """Sandbox the code execution."""
    module_path = base_path / str(module_name.replace(".", "/") + ".py")

    if not module_path.exists():
        raise ModuleNotFoundError(f'Could not load module "{module_name}"')

    sandbox = Sandbox(module_path, namespace=module_name)

    return sandbox.execute()


async def publish_message(message: dict) -> None:
    """Publish a message to the pubsub channel."""
    log.info(f'Publishing message to pubsub channel "{CHANNEL_NAME}"')
    client, _ = get_client()

    await client.publish(CHANNEL_NAME, pickle.dumps(message))


def get_client() -> tuple[redis.Redis, redis.client.PubSub]:
    """Return an async Redis client and pubsub object."""
    client = redis.Redis.from_url(REDIS_ENDPOINT)
    pubsub = client.pubsub()

    return client, pubsub


def load_or_reload_plugin(path: pathlib.Path) -> None:
    """Given a path, load or reload a plugin."""
    log.info(f'Loading plugin at "{path}"')

    manifest_file = path / MANIFEST_FILE_NAME
    manifest_json_str = manifest_file.read_text()

    # the name is the folder name underneath the plugins directory
    name = path.name

    try:
        manifest_json: PluginManifest = json.loads(manifest_json_str)
    except Exception as e:
        log.error(f'Unable to load plugin "{name}": {e}')
        return

    secrets_file = path / SECRETS_FILE_NAME

    secrets_json = {}
    if secrets_file.exists():
        try:
            secrets_json = json.load(secrets_file.open())
        except Exception as e:
            log.error(f'Unable to load secrets for plugin "{name}": {str(e)}')

    # TODO add existing schema validation from Michela here
    try:
        handlers = manifest_json["components"].get("protocols", []) + manifest_json[
            "components"
        ].get("applications", [])
    except Exception as e:
        log.error(f'Unable to load plugin "{name}": {str(e)}')
        return

    for handler in handlers:
        # TODO add class colon validation to existing schema validation
        # TODO when we encounter an exception here, disable the plugin in response
        try:
            handler_module, handler_class = handler["class"].split(":")
            name_and_class = f"{name}:{handler_module}:{handler_class}"
        except ValueError:
            log.error(f'Unable to parse class for plugin "{name}": "{handler["class"]}"')
            continue

        try:
            result = sandbox_from_module(path.parent, handler_module)

            if name_and_class in LOADED_PLUGINS:
                log.info(f"Reloading plugin '{name_and_class}'")

                LOADED_PLUGINS[name_and_class]["active"] = True

                LOADED_PLUGINS[name_and_class]["class"] = result[handler_class]
                LOADED_PLUGINS[name_and_class]["sandbox"] = result
                LOADED_PLUGINS[name_and_class]["secrets"] = secrets_json
            else:
                log.info(f"Loading plugin '{name_and_class}'")

                LOADED_PLUGINS[name_and_class] = {
                    "active": True,
                    "class": result[handler_class],
                    "sandbox": result,
                    "handler": handler,
                    "secrets": secrets_json,
                }
        except Exception as err:
            log.error(f'Error importing module "{name_and_class}": {err}')

            for error_line in traceback.format_exception(err):
                log.error(error_line)


def refresh_event_type_map() -> None:
    """Ensure the event subscriptions are up to date."""
    EVENT_HANDLER_MAP.clear()

    for name, plugin in LOADED_PLUGINS.items():
        if hasattr(plugin["class"], "RESPONDS_TO"):
            responds_to = plugin["class"].RESPONDS_TO

            if isinstance(responds_to, str):
                EVENT_HANDLER_MAP[responds_to].append(name)
            elif isinstance(responds_to, list):
                for event in responds_to:
                    EVENT_HANDLER_MAP[event].append(name)
            else:
                log.warning(f"Unknown RESPONDS_TO type: {type(responds_to)}")


def load_plugins(specified_plugin_paths: list[str] | None = None) -> None:
    """Load the plugins."""
    # first mark each plugin as inactive since we want to remove it from
    # LOADED_PLUGINS if it no longer exists on disk
    for plugin in LOADED_PLUGINS.values():
        plugin["active"] = False

    if specified_plugin_paths is not None:
        # convert to Paths
        plugin_paths = [pathlib.Path(name) for name in specified_plugin_paths]

        for plugin_path in plugin_paths:
            # when we import plugins we'll use the module name directly so we need to add the plugin
            # directory to the path
            path_to_append = pathlib.Path(".") / plugin_path.parent
            sys.path.append(path_to_append.as_posix())
    else:
        candidates = os.listdir(PLUGIN_DIRECTORY)

        # convert to Paths
        plugin_paths = [pathlib.Path(os.path.join(PLUGIN_DIRECTORY, name)) for name in candidates]

    # get all directories under the plugin directory
    plugin_paths = [path for path in plugin_paths if path.is_dir()]

    # load or reload each plugin
    for plugin_path in plugin_paths:
        load_or_reload_plugin(plugin_path)

    # if a plugin has been uninstalled/disabled remove it from LOADED_PLUGINS
    for name, plugin in LOADED_PLUGINS.copy().items():
        if not plugin["active"]:
            del LOADED_PLUGINS[name]

    refresh_event_type_map()

    log_nr_event_handlers()


def log_nr_event_handlers() -> None:
    """Log the number of event handlers for each event."""
    for key in EventType.keys():  # noqa: SIM118
        value = len(EVENT_HANDLER_MAP[key]) if key in EVENT_HANDLER_MAP else 0
        statsd_client.timing("plugins.event_nr_handlers", value, tags={"event": key})


_cleanup_coroutines = []


async def serve(specified_plugin_paths: list[str] | None = None) -> None:
    """Run the server."""
    port = "50051"

    server = grpc.aio.server()
    server.add_insecure_port("127.0.0.1:" + port)

    add_PluginRunnerServicer_to_server(PluginRunner(), server)

    log.info(f"Starting server, listening on port {port}")

    install_plugins()
    load_plugins(specified_plugin_paths)

    await server.start()

    async def server_graceful_shutdown() -> None:
        log.info("Starting graceful shutdown...")
        await server.stop(5)

    _cleanup_coroutines.append(server_graceful_shutdown())

    await server.wait_for_termination()


# NOTE: specified_plugin_paths powers the `canvas run-plugins` command
def run_server(specified_plugin_paths: list[str] | None = None) -> None:
    """Run the server."""
    loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(
            asyncio.gather(
                serve(specified_plugin_paths),
                synchronize_plugins_and_report_errors(),
            )
        )
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(*_cleanup_coroutines)
        loop.close()


if __name__ == "__main__":
    run_server()
