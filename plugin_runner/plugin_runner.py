import asyncio

from concurrent import futures
import logging

import grpc

from messages.effects_pb2 import Effect
from messages.events_pb2 import EventResponse, EventType
from services.plugin_runner_pb2_grpc import PluginRunnerServicer, add_PluginRunnerServicer_to_server


class PluginRunner(PluginRunnerServicer):
    async def HandleEvent(self, request, context):
        event_name = EventType.Name(request.type)
        logging.info(f'Handling event: {event_name}')
        yield EventResponse(success=True, effects=[Effect(type='Log', payload=f'Handled Event: "{event_name}"')])

async def serve():
    port = "50051"
    server = grpc.aio.server()
    add_PluginRunnerServicer_to_server(PluginRunner(), server)
    server.add_insecure_port("[::]:" + port)
    logging.info("Starting server, listening on " + port)
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())
