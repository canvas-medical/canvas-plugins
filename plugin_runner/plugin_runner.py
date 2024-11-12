import asyncio
import importlib.util
import json
import os
import pathlib
import signal
import sys
import time
import traceback
from collections import defaultdict
from types import FrameType
from typing import Any, AsyncGenerator, Optional, TypedDict, cast

import grpc
import statsd

from canvas_generated.messages.plugins_pb2 import (
    ReloadPluginsRequest,
    ReloadPluginsResponse,
)
from canvas_generated.services.plugin_runner_pb2_grpc import (
    PluginRunnerServicer,
    add_PluginRunnerServicer_to_server,
)
from canvas_sdk.effects import Effect
from canvas_sdk.events import Event, EventResponse, EventType
from canvas_sdk.protocols import ClinicalQualityMeasure
from canvas_sdk.utils.stats import get_duration_ms, tags_to_line_protocol
from logger import log
from plugin_runner.authentication import token_for_plugin
from plugin_runner.plugin_synchronizer import publish_message
from plugin_runner.sandbox import Sandbox

ENV = os.getenv("ENV", "development")

IS_PRODUCTION = ENV == "production"

MANIFEST_FILE_NAME = "CANVAS_MANIFEST.json"

SECRETS_FILE_NAME = "SECRETS.json"

# specify a local plugin directory for development
PLUGIN_DIRECTORY = "/plugin-runner/custom-plugins" if IS_PRODUCTION else "./custom-plugins"

# when we import plugins we'll use the module name directly so we need to add the plugin
# directory to the path
sys.path.append(PLUGIN_DIRECTORY)

# a global dictionary of loaded plugins
# TODO: create typings here for the subkeys
LOADED_PLUGINS: dict = {}

# a global dictionary of events to protocol class names
EVENT_PROTOCOL_MAP: dict = {}


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


class Components(TypedDict):
    """Components."""

    protocols: list[Protocol]
    commands: list[dict]
    content: list[dict]
    effects: list[dict]
    views: list[dict]


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

    def __init__(self) -> None:
        self.statsd_client = statsd.StatsClient()
        super().__init__()

    sandbox: Sandbox

    async def HandleEvent(
        self, request: Event, context: Any
    ) -> AsyncGenerator[EventResponse, None]:
        """This is invoked when an event comes in."""
        event_start_time = time.time()
        event_type = request.type
        event_name = EventType.Name(event_type)
        relevant_plugins = EVENT_PROTOCOL_MAP.get(event_name, [])

        if event_type in [EventType.PLUGIN_CREATED, EventType.PLUGIN_UPDATED]:
            plugin_name = request.target
            # filter only for the plugin(s) that were created/updated
            relevant_plugins = [p for p in relevant_plugins if p.startswith(f"{plugin_name}:")]

        effect_list = []

        for plugin_name in relevant_plugins:
            plugin = LOADED_PLUGINS[plugin_name]
            protocol_class = plugin["class"]
            base_plugin_name = plugin_name.split(":")[0]

            secrets = plugin.get("secrets", {})
            secrets["graphql_jwt"] = token_for_plugin(plugin_name=plugin_name, audience="home")

            try:
                protocol = protocol_class(request, secrets)
                classname = (
                    protocol.__class__.__name__
                    if isinstance(protocol, ClinicalQualityMeasure)
                    else None
                )

                compute_start_time = time.time()
                _effects = await asyncio.get_running_loop().run_in_executor(None, protocol.compute)
                effects = [
                    Effect(
                        type=effect.type,
                        payload=effect.payload,
                        plugin_name=base_plugin_name,
                        classname=classname,
                    )
                    for effect in _effects
                ]
                compute_duration = get_duration_ms(compute_start_time)

                log.info(f"{plugin_name}.compute() completed ({compute_duration} ms)")
                statsd_tags = tags_to_line_protocol({"plugin": plugin_name})
                self.statsd_client.timing(
                    f"plugins.protocol_duration_ms,{statsd_tags}",
                    delta=compute_duration,
                )
            except Exception as e:
                for error_line_with_newlines in traceback.format_exception(e):
                    for error_line in error_line_with_newlines.split("\n"):
                        log.error(error_line)
                continue

            effect_list += effects

        event_duration = get_duration_ms(event_start_time)

        # Don't log anything if a protocol didn't actually run.
        if relevant_plugins:
            log.info(f"Responded to Event {event_name} ({event_duration} ms)")
            statsd_tags = tags_to_line_protocol({"event": event_name})
            self.statsd_client.timing(
                f"plugins.event_duration_ms,{statsd_tags}",
                delta=event_duration,
            )

        yield EventResponse(success=True, effects=effect_list)

    async def ReloadPlugins(
        self, request: ReloadPluginsRequest, context: Any
    ) -> AsyncGenerator[ReloadPluginsResponse, None]:
        """This is invoked when we need to reload plugins."""
        try:
            load_plugins()
            publish_message({"action": "restart"})
        except ImportError:
            yield ReloadPluginsResponse(success=False)
        else:
            yield ReloadPluginsResponse(success=True)


def handle_hup_cb(_signum: int, _frame: Optional[FrameType]) -> None:
    """handle_hup_cb."""
    log.info("Received SIGHUP, reloading plugins...")
    load_plugins()


def sandbox_from_module_name(module_name: str) -> Any:
    """Sandbox the code execution."""
    spec = importlib.util.find_spec(module_name)

    if not spec or not spec.origin:
        raise Exception(f'Could not load plugin "{module_name}"')

    origin = pathlib.Path(spec.origin)
    source_code = origin.read_text()

    sandbox = Sandbox(source_code)

    return sandbox.execute()


def load_or_reload_plugin(path: pathlib.Path) -> None:
    """Given a path, load or reload a plugin."""
    log.info(f"Loading {path}")

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
        protocols = manifest_json["components"]["protocols"]
    except Exception as e:
        log.error(f'Unable to load plugin "{name}": {str(e)}')
        return

    for protocol in protocols:
        # TODO add class colon validation to existing schema validation
        # TODO when we encounter an exception here, disable the plugin in response
        try:
            protocol_module, protocol_class = protocol["class"].split(":")
            name_and_class = f"{name}:{protocol_module}:{protocol_class}"
        except ValueError:
            log.error(f"Unable to parse class for plugin '{name}': '{protocol['class']}'")
            continue

        try:
            if name_and_class in LOADED_PLUGINS:
                log.info(f"Reloading plugin '{name_and_class}'")

                result = sandbox_from_module_name(protocol_module)

                LOADED_PLUGINS[name_and_class]["active"] = True

                LOADED_PLUGINS[name_and_class]["class"] = result[protocol_class]
                LOADED_PLUGINS[name_and_class]["sandbox"] = result
                LOADED_PLUGINS[name_and_class]["secrets"] = secrets_json
            else:
                log.info(f"Loading plugin '{name_and_class}'")

                result = sandbox_from_module_name(protocol_module)

                LOADED_PLUGINS[name_and_class] = {
                    "active": True,
                    "class": result[protocol_class],
                    "sandbox": result,
                    "protocol": protocol,
                    "secrets": secrets_json,
                }
        except Exception as err:
            log.error(f"Error importing module '{name_and_class}': {err}")
            for error_line in traceback.format_exception(err):
                log.error(error_line)


def refresh_event_type_map() -> None:
    """Ensure the event subscriptions are up to date."""
    global EVENT_PROTOCOL_MAP
    EVENT_PROTOCOL_MAP = defaultdict(list)

    for name, plugin in LOADED_PLUGINS.items():
        if hasattr(plugin["class"], "RESPONDS_TO"):
            responds_to = plugin["class"].RESPONDS_TO

            if isinstance(responds_to, str):
                EVENT_PROTOCOL_MAP[responds_to].append(name)
            elif isinstance(responds_to, list):
                for event in responds_to:
                    EVENT_PROTOCOL_MAP[event].append(name)
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

    # filter to only the directories containing a manifest file
    plugin_paths = [path for path in plugin_paths if (path / MANIFEST_FILE_NAME).exists()]

    # load or reload each plugin
    for plugin_path in plugin_paths:
        load_or_reload_plugin(plugin_path)

    # if a plugin has been uninstalled/disabled remove it from LOADED_PLUGINS
    for name, plugin in LOADED_PLUGINS.copy().items():
        if not plugin["active"]:
            del LOADED_PLUGINS[name]

    refresh_event_type_map()


_cleanup_coroutines = []


async def serve(specified_plugin_paths: list[str] | None = None) -> None:
    """Run the server."""
    port = "50051"

    server = grpc.aio.server()
    server.add_insecure_port("127.0.0.1:" + port)

    add_PluginRunnerServicer_to_server(PluginRunner(), server)

    log.info(f"Starting server, listening on port {port}")

    load_plugins(specified_plugin_paths)

    await server.start()

    async def server_graceful_shutdown() -> None:
        log.info("Starting graceful shutdown...")
        await server.stop(5)

    _cleanup_coroutines.append(server_graceful_shutdown())

    await server.wait_for_termination()


def run_server(specified_plugin_paths: list[str] | None = None) -> None:
    """Run the server."""
    loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)

    signal.signal(signal.SIGHUP, handle_hup_cb)

    try:
        loop.run_until_complete(serve(specified_plugin_paths))
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(*_cleanup_coroutines)
        loop.close()


if __name__ == "__main__":
    run_server()
