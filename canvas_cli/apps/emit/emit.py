import json
import random
from pathlib import Path
from typing import Annotated

import grpc
import typer

from canvas_generated.messages.events_pb2 import Event as PluginRunnerEvent
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
    # If an event fixture file exists at the specified path, use it.
    # Otherwise, see if it represents an event that we have a Canvas-provided
    # fixture for and use that.
    event_fixture_path = Path(event_fixture)

    if not event_fixture_path.exists():
        candidate_built_in_fixture_path = (
            Path(__file__).resolve().parent / "event_fixtures" / f"{event_fixture}.ndjson"
        )
        if candidate_built_in_fixture_path.exists():
            event_fixture_path = candidate_built_in_fixture_path
        else:
            print(f"ERROR: No file found at location {event_fixture}.")
            print(f"ERROR: No built-in fixture file found named {event_fixture}.ndjson.")
            return

    # Grab a random event from the fixture file ndjson
    lines = event_fixture_path.read_text().splitlines()
    myline = random.choice(lines)
    event_data = json.loads(myline)
    event = PluginRunnerEvent(
        type=event_data["EventType"],
        target=event_data["target"],
        context=event_data["context"],
    )
    with grpc.insecure_channel(f"localhost:{plugin_runner_port}") as channel:
        stub = PluginRunnerStub(channel)
        responses = stub.HandleEvent(event)

        at_least_one_effect = False
        try:
            for response in responses:
                for effect in response.effects:
                    at_least_one_effect = True
                    print(effect)

            if not at_least_one_effect:
                print("SUCCESS: No effects returned.")
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                print(
                    f"ERROR: Couldn't make a connection to a plugin runner process at localhost:{plugin_runner_port}. Is it running?"
                )
