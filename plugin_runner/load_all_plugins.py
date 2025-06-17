#!/usr/bin/env uv run

import json
import logging
import re
import sys
import traceback
from collections import defaultdict
from contextlib import redirect_stderr, redirect_stdout
from glob import glob
from io import StringIO
from pathlib import Path
from textwrap import indent

import httpretty

from canvas_generated.messages.events_pb2 import PLUGIN_CREATED
from canvas_generated.messages.events_pb2 import Event as EventRequest
from canvas_sdk.events.base import Event
from canvas_sdk.protocols.base import BaseProtocol
from plugin_runner.plugin_runner import LOADED_PLUGINS, load_or_reload_plugin

ORIGINAL_PATH = sys.path.copy()


def enable_httpretty() -> None:
    """
    Prevent any HTTP requests from being made.
    """
    httpretty.enable(verbose=True, allow_net_connect=False)

    for method in [
        httpretty.GET,
        httpretty.PUT,
        httpretty.POST,
        httpretty.DELETE,
        httpretty.HEAD,
        httpretty.PATCH,
        httpretty.OPTIONS,
        httpretty.CONNECT,
    ]:
        httpretty.register_uri(method, re.compile(r".*"), body="{}")


def disable_httpretty() -> None:
    """
    Allow normal HTTP activity.
    """
    httpretty.disable()
    httpretty.reset()


def main() -> None:
    """
    Iterate through all of our plugins to verify they work with this version of the SDK.
    """
    if len(sys.argv) < 2:
        print("You must specify a base path.")
        sys.exit(1)

    base_path = sys.argv[1]

    for folder in glob(f"{base_path}/**/*"):
        path = Path(folder)

        if "{{" in folder:
            print(f"Ignoring templated path: {folder}")
            continue

        if not path.is_dir():
            continue

        if not (path / "CANVAS_MANIFEST.json").exists():
            print(f"Missing CANVAS_MANIFEST.json in {folder}")
            continue

        sys.path = ORIGINAL_PATH.copy()

        # this makes plugin imports work and mirrors what the plugin_runner does
        sys.path.append((Path(".") / path.parent).as_posix())

        print(path)

        output = StringIO()

        plugin_runner_logger = logging.getLogger("plugin_runner_logger")
        old_handlers = plugin_runner_logger.handlers.copy()
        plugin_runner_logger.handlers = [logging.StreamHandler(output)]

        with redirect_stdout(output), redirect_stderr(output):
            success = load_or_reload_plugin(path)

        output_string = output.getvalue()

        if not success:
            print()
            print(indent(output_string, prefix="    ").rstrip())
            print()

        plugin_runner_logger.handlers = old_handlers

    enable_httpretty()

    for key, plugin in LOADED_PLUGINS.items():
        Klass: type[BaseProtocol] = plugin["class"]

        if not hasattr(Klass, "compute") or not callable(Klass.compute):
            print(f"Skipping {key} due to no compute method")

        event_request = EventRequest(
            type=PLUGIN_CREATED,
            context=json.dumps(
                {
                    "key": "test",
                    "fields": {
                        "coding": {"value": "test"},
                        "goal_statement": {"value": "test"},
                        "questionnaire": {"text": "test"},
                        "medication": {"extra": {"coding": "test"}},
                        "ordering_provider": {"value": "test"},
                        "text": "test",
                    },
                    "method": "GET",
                    "note_id": 5,
                    "note": {
                        "uuid": "b2bd0672-ab36-4eca-b105-884f976ae810",
                        "id": "b2bd0672-ab36-4eca-b105-884f976ae810",
                    },
                    "path": "https://test",
                    "patient_id": 5,
                    "patient": {"id": 5},
                    "results": [],
                    "search_term": "test",
                    "state": "LKD",
                }
            ),
            target="b2bd0672-ab36-4eca-b105-884f976ae810",
            target_type="Patient",
        )
        event = Event(event_request=event_request)

        try:
            klass = Klass(
                event=event,
                secrets=defaultdict(lambda: "test", {"sentinel": True}),
                environment=defaultdict(lambda: "test", {"sentinel": True}),
            )
        except TypeError as e:
            print(f"Failed to instantiate {key}:", e)
            continue

        plugin_runner_logger = logging.getLogger("plugin_runner_logger")
        old_handlers = plugin_runner_logger.handlers.copy()
        plugin_runner_logger.handlers = [logging.StreamHandler(output)]

        output = StringIO()

        error: Exception | None = None

        try:
            with redirect_stdout(output), redirect_stderr(output):
                result = klass.compute()
        except TypeError as e:
            error = e
        except KeyError as e:
            error = e
        except Exception as e:
            error = e

        plugin_runner_logger.handlers = old_handlers

        result_count = len(result)
        request_count = len(httpretty.latest_requests())

        print(f"{key}: {result_count}/{request_count}")

        if error:
            print()

            # abbreviate these, they come from not being able to access the database
            if "fake_getaddrinfo" in str(error):
                print(indent(str(error), prefix="    ").rstrip())
            else:
                print(indent("".join(traceback.format_exception(error)), prefix="    ").rstrip())

            print()

        output_string = output.getvalue()

        if output_string:
            print()
            print(indent(output_string, prefix="    ").rstrip())
            print()

    disable_httpretty()


if __name__ == "__main__":
    main()
