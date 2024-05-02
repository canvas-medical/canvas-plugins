import asyncio
import importlib.util
import json
# import logging
import os
import pathlib
import sys

from collections import defaultdict

import grpc

from canvas_sdk.events import Event, EventResponse, EventType
from generated.messages.plugins_pb2 import ReloadPluginsRequest, ReloadPluginsResponse
from generated.services.plugin_runner_pb2_grpc import (
    PluginRunnerServicer,
    add_PluginRunnerServicer_to_server,
)

from sandbox import Sandbox

from logger.logger import PluginLogger
log = PluginLogger()

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
LOADED_PLUGINS = {}

# a global dictionary of events to protocol class names
EVENT_PROTOCOL_MAP = {}


class PluginRunner(PluginRunnerServicer):
    def __init__(self) -> None:
        super().__init__()

    sandbox: Sandbox

    async def HandleEvent(self, request: Event, context):
        event_name = EventType.Name(request.type)
        relevant_plugins = EVENT_PROTOCOL_MAP.get(event_name, [])

        effect_list = []

        for plugin_name in relevant_plugins:
            plugin = LOADED_PLUGINS[plugin_name]
            protocol_class = plugin["class"]
            effects = protocol_class(request, plugin.get("secrets", {})).compute()
            effect_list += effects

        yield EventResponse(success=True, effects=effect_list)

    async def ReloadPlugins(self, request: ReloadPluginsRequest, context):
        try:
            load_plugins()
        except ImportError:
            yield ReloadPluginsResponse(success=False)
        else:
            yield ReloadPluginsResponse(success=True)


def sandbox_from_module_name(module_name: str):
    spec = importlib.util.find_spec(module_name)

    if not spec or not spec.origin:
        raise Exception(f'Could not load plugin "{module_name}"')

    origin = pathlib.Path(spec.origin)
    source_code = origin.read_text()

    sandbox = Sandbox(source_code)

    return sandbox.execute()


def load_or_reload_plugin(path: pathlib.Path) -> None:
    log.info(f"Loading {path}")

    manifest_file = path / MANIFEST_FILE_NAME
    manifest_json = manifest_file.read_text()

    # the name is the folder name underneath the plugins directory
    name = path.name

    try:
        manifest_json = json.loads(manifest_json)
    except Exception as e:
        log.warning(f'Unable to load plugin "{name}":', e)
        return

    secrets_file = path / SECRETS_FILE_NAME

    secrets_json = {}
    if secrets_file.exists():
        try:
            secrets_json = json.load(secrets_file.open())
        except Exception as e:
            logging.warn(f'Unable to load secrets for plugin "{name}":', e)

    # TODO add existing schema validation from Michela here
    try:
        protocols = manifest_json["components"]["protocols"]
    except Exception as e:
        log.warning(f'Unable to load plugin "{name}":', e)
        return

    for protocol in protocols:
        # TODO add class colon validation to existing schema validation
        protocol_module, protocol_class = protocol["class"].split(":")
        name_and_class = f"{name}:{protocol_module}:{protocol_class}"

        if name_and_class in LOADED_PLUGINS:
            log.info(f"Reloading plugin: {name_and_class}")

            result = sandbox_from_module_name(protocol_module)

            LOADED_PLUGINS[name_and_class]["active"] = True

            LOADED_PLUGINS[name_and_class]["class"] = result[protocol_class]
            LOADED_PLUGINS[name_and_class]["sandbox"] = result
            LOADED_PLUGINS[name_and_class]["secrets"] = secrets_json
        else:
            log.info(f"Loading plugin: {name_and_class}")

            result = sandbox_from_module_name(protocol_module)

            LOADED_PLUGINS[name_and_class] = {
                "active": True,
                "class": result[protocol_class],
                "sandbox": result,
                "protocol": protocol,
                "secrets": secrets_json,
            }


def refresh_event_type_map():
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


def load_plugins():
    # first mark each plugin as inactive since we want to remove it from
    # LOADED_PLUGINS if it no longer exists on disk
    for plugin in LOADED_PLUGINS.values():
        plugin["active"] = False

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


async def serve():
    port = "50051"

    server = grpc.aio.server()
    server.add_insecure_port("127.0.0.1:" + port)

    add_PluginRunnerServicer_to_server(PluginRunner(), server)

    log.info(f"Starting server, listening on port {port}")

    load_plugins()

    await server.start()

    async def server_graceful_shutdown():
        log.info("Starting graceful shutdown...")
        await server.stop(5)

    _cleanup_coroutines.append(server_graceful_shutdown())

    await server.wait_for_termination()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(serve())
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(*_cleanup_coroutines)
        loop.close()
