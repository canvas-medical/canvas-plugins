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

# TODO load and store plugins globally
LOADED_PLUGINS = {}


class PluginRunner(PluginRunnerServicer):
    async def HandleEvent(self, request: Event, context):
        event_name = EventType.Name(request.type)

        logging.info(f"Handling event: {event_name}")

        yield EventResponse(
            success=True, effects=[Effect(type="Log", payload=f'Handled Event: "{event_name}"')]
        )

    async def ReloadPlugins(self, request: ReloadPluginsRequest, context):
        try:
            for name, module in LOADED_PLUGINS.items():
                logging.info(f"Reloading plugin: {name}")
                importlib.reload(module)
        except ImportError:
            yield ReloadPluginsResponse(success=False)
        else:
            yield ReloadPluginsResponse(success=True)


def load_plugins():
    # TODO: walk plugins directory, import and add each plugin to
    # LOADED_PLUGINS
    pass


async def serve():
    port = "50051"

    server = grpc.aio.server()
    server.add_insecure_port("127.0.0.1:" + port)

    add_PluginRunnerServicer_to_server(PluginRunner(), server)

    logging.info(f"Starting server, listening on port {port}")

    load_plugins()

    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())
