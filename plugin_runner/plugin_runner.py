import asyncio
import json

import importlib
import logging

import grpc

from generated.messages.effects_pb2 import Effect, EffectType
from generated.messages.events_pb2 import EventResponse, EventType
from generated.messages.events_pb2 import Event, EventResponse, EventType
from generated.messages.plugins_pb2 import ReloadPluginsRequest, ReloadPluginsResponse
from generated.services.plugin_runner_pb2_grpc import (
    PluginRunnerServicer,
    add_PluginRunnerServicer_to_server,
)

# import my_first_plugin
# import my_second_plugin

LOADED_PLUGINS = {
    "my_first_plugin": __import__("my_first_plugin.my_first_plugin.protocols.protocol"),
    "my_second_plugin": __import__("my_second_plugin.my_second_plugin.protocols.protocol"),
}

# TODO load and store plugins externally
# def get_loaded_plugins():
#     return {
#         "my_first_plugin": my_first_plugin,
#         "my_second_plugin": my_second_plugin
#     }


class PluginRunner(PluginRunnerServicer):
    EVENT_PROTOCOL_MAP = {}

    def __init__(self) -> None:
        # load_plugins()
        self.refresh_event_type_map()
        super().__init__()

    async def HandleEvent(self, request: Event, context):
        event_name = EventType.Name(request.type)
        relevant_plugins = self.EVENT_PROTOCOL_MAP.get(event_name, [])

        effect_list = []
        for plugin_name in relevant_plugins:
            module = LOADED_PLUGINS.get(plugin_name)
            protocol_class = getattr(module, plugin_name).protocols.protocol.Protocol
            effects = protocol_class(request).compute()

            effect_list = [
                Effect(
                    type=EffectType.Value(effect["effect_type"]),
                    payload=json.dumps(effect["payload"]),
                )
                for effect in effects
            ]
        yield EventResponse(success=True, effects=effect_list)

    async def ReloadPlugins(self, request: ReloadPluginsRequest, context):
        try:
            reload_plugins()
        except ImportError:
            yield ReloadPluginsResponse(success=False)
        else:
            self.refresh_event_type_map()
            yield ReloadPluginsResponse(success=True)

    def refresh_event_type_map(self):
        self.EVENT_PROTOCOL_MAP = {}
        for name, module in LOADED_PLUGINS.items():
            protocol_class = None
            try:
                # protocol_file = importlib.import_module(f"{name}.{name}.protocols.protocol")
                # breakpoint()
                protocol_file = getattr(module, name)
                protocol_class = protocol_file.protocols.protocol.Protocol
            except ImportError:
                continue

            if protocol_class and hasattr(protocol_class, "RESPONDS_TO"):
                self.EVENT_PROTOCOL_MAP[protocol_class.RESPONDS_TO] = [name]


def reload_plugins():
    for name, module in LOADED_PLUGINS.items():
        logging.info(f"Reloading plugin: {name}")
        LOADED_PLUGINS[name] = importlib.reload(module)

        protocol_class = getattr(LOADED_PLUGINS[name], name).protocols.protocol.Protocol

        print(f"DEBUG: {name} {protocol_class.NARRATIVE_STRING}")


async def serve():
    port = "50051"

    server = grpc.aio.server()
    server.add_insecure_port("127.0.0.1:" + port)

    add_PluginRunnerServicer_to_server(PluginRunner(), server)

    logging.info(f"Starting server, listening on port {port}")

    reload_plugins()

    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())
