import asyncio
import json

import logging

import grpc

from generated.messages.effects_pb2 import Effect, EffectType
from generated.messages.events_pb2 import EventResponse, EventType
from generated.services.plugin_runner_pb2_grpc import PluginRunnerServicer, add_PluginRunnerServicer_to_server


class PluginRunner(PluginRunnerServicer):
    async def HandleEvent(self, request, context):
        event_name = EventType.Name(request.type)
        logging.info(f'Handling event: {event_name}')

        effect_type = EffectType.LOG
        effect_payload = f'Handled Event: "{event_name}"'

        if event_name == "ASSESS_COMMAND__CONDITION_SELECTED":
            received_message = json.loads(request.target)
            print(received_message)
            has_hypertension_condition = [i for i in received_message["data"]["condition"]["codings"] if i["code"] == "I10" and i["system"] == "ICD-10"]
            if has_hypertension_condition:
                effect_type = EffectType.ADD_PLAN_COMMAND
                effect_dict = {
                    "note": received_message["note"],
                    "data": {
                        "narrative": "Instruct patient to monitor and record blood pressure at home."
                    }
                }
                effect_payload = json.dumps(effect_dict)

        yield EventResponse(success=True, effects=[Effect(type=effect_type, payload=effect_payload)])

async def serve():
    port = "50051"
    server = grpc.aio.server()
    add_PluginRunnerServicer_to_server(PluginRunner(), server)
    server.add_insecure_port("127.0.0.1:" + port)
    logging.info("Starting server, listening on " + port)
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())
