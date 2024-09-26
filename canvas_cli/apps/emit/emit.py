import json
import random
from pathlib import Path
from typing import Annotated

import grpc
import typer

from canvas_generated.messages.events_pb2 import Event as PluginRunnerEvent
from canvas_generated.messages.events_pb2 import EventType as PluginRunnerEventType
from canvas_generated.services.plugin_runner_pb2_grpc import PluginRunnerStub


def emit(
    event_fixture: str,
    plugin_runner_port: Annotated[
        str, typer.Option(help="Port of your locally running plugin runner")
    ] = "50051",
) -> None:
    """
    Send an event fixture to your locally running plugin-runner process, and print any resultant effects.

    Valid fixture files are newline-delimited JSON, with each containing the keys `EventType`, `target`, and `context`. Some fixture files are included in the canvas-plugins repo.
    """
    # Grab a random event from the fixture file ndjson
    lines = Path(event_fixture).read_text().splitlines()
    myline = random.choice(lines)
    event_data = json.loads(myline)
    event = PluginRunnerEvent(
        type=PluginRunnerEventType.Value(event_data["EventType"]),
        target=event_data["target"],
        context=event_data["context"],
    )
    with grpc.insecure_channel(f"localhost:{plugin_runner_port}") as channel:
        stub = PluginRunnerStub(channel)
        responses = stub.HandleEvent(event)

        for response in responses:
            for effect in response.effects:
                print(effect)
