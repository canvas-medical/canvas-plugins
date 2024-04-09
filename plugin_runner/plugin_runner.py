import asyncio
import importlib
import json
import logging
import os
import pathlib
import sys

from collections import defaultdict

import grpc

from canvas_sdk.effects import Effect, EffectType
from generated.messages.events_pb2 import Event, EventResponse, EventType
from generated.messages.plugins_pb2 import ReloadPluginsRequest, ReloadPluginsResponse
from generated.services.plugin_runner_pb2_grpc import (
    PluginRunnerServicer,
    add_PluginRunnerServicer_to_server,
)

ENV = os.getenv("ENV", "development")

IS_PRODUCTION = ENV == "production"

MANIFEST_FILE_NAME = "CANVAS_MANIFEST.json"

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

    async def HandleEvent(self, request: Event, context):
        event_name = EventType.Name(request.type)
        relevant_plugins = EVENT_PROTOCOL_MAP.get(event_name, [])

        effect_list = []

        for plugin_name in relevant_plugins:
            plugin = LOADED_PLUGINS[plugin_name]
            protocol_class = plugin["class"]
            effects = protocol_class(request).compute()
            effect_list += effects

        yield EventResponse(success=True, effects=effect_list)

    async def ReloadPlugins(self, request: ReloadPluginsRequest, context):
        try:
            load_plugins()
        except ImportError:
            yield ReloadPluginsResponse(success=False)
        else:
            yield ReloadPluginsResponse(success=True)


def load_or_reload_plugin(path: pathlib.Path) -> None:
    logging.info(f"Loading {path}")

    manifest_file = path / MANIFEST_FILE_NAME
    manifest_json = manifest_file.read_text()

    # the name is the folder name underneath the plugins directory
    name = path.name

    try:
        manifest_json = json.loads(manifest_json)
    except Exception as e:
        logging.warn(f'Unable to load plugin "{name}":', e)
        return

    # TODO add existing schema validation from Michela here
    try:
        protocols = manifest_json["components"]["protocols"]
    except Exception as e:
        logging.warn(f'Unable to load plugin "{name}":', e)
        return

    for protocol in protocols:
        # TODO add class colon validation to existing schema validation
        protocol_module, protocol_class = protocol["class"].split(":")
        name_and_class = f"{name}:{protocol_module}:{protocol_class}"

        if name_and_class in LOADED_PLUGINS:
            logging.info(f"Reloading plugin: {name_and_class}")

            protocol_module = LOADED_PLUGINS[name_and_class]["module"]

            importlib.reload(protocol_module)

            LOADED_PLUGINS[name_and_class]["active"] = True
        else:
            logging.info(f"Loading plugin: {name_and_class}")

            module = importlib.import_module(protocol_module)

            LOADED_PLUGINS[name_and_class] = {
                "active": True,
                "class": getattr(module, protocol_class),
                "module": module,
                "protocol": protocol,
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
                logging.warn(f"Unknown RESPONDS_TO type: {type(responds_to)}")


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

    logging.info(f"Starting server, listening on port {port}")

    load_plugins()

    await server.start()

    async def server_graceful_shutdown():
        logging.info("Starting graceful shutdown...")
        await server.stop(5)

    _cleanup_coroutines.append(server_graceful_shutdown())

    await server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(serve())
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(*_cleanup_coroutines)
        loop.close()
