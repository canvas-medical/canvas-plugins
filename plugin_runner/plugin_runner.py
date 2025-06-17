import json
import os
import pathlib
import pickle
import pkgutil
import sys
import threading
import traceback
from collections import defaultdict
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from http import HTTPStatus
from time import sleep
from typing import Any, TypedDict

import grpc
import redis
import sentry_sdk
from django.core.signals import request_finished, request_started
from redis.backoff import ExponentialBackoff
from redis.exceptions import ConnectionError, TimeoutError
from redis.retry import Retry
from sentry_sdk.integrations.logging import ignore_logger

import settings
from canvas_generated.messages.effects_pb2 import EffectType
from canvas_generated.messages.plugins_pb2 import ReloadPluginsRequest, ReloadPluginsResponse
from canvas_generated.services.plugin_runner_pb2_grpc import (
    PluginRunnerServicer,
    add_PluginRunnerServicer_to_server,
)
from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import Response
from canvas_sdk.events import Event, EventRequest, EventResponse, EventType
from canvas_sdk.handlers.simple_api.websocket import DenyConnection
from canvas_sdk.protocols import ClinicalQualityMeasure
from canvas_sdk.utils import metrics
from canvas_sdk.utils.metrics import measured
from logger import log
from plugin_runner.authentication import token_for_plugin
from plugin_runner.installation import install_plugins
from plugin_runner.sandbox import Sandbox, sandbox_from_module
from settings import (
    CHANNEL_NAME,
    CUSTOMER_IDENTIFIER,
    ENV,
    IS_PRODUCTION_CUSTOMER,
    MANIFEST_FILE_NAME,
    PLUGIN_DIRECTORY,
    REDIS_ENDPOINT,
    SECRETS_FILE_NAME,
    SENTRY_DSN,
)

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=ENV,
        release=os.getenv("CANVAS_PLUGINS_REPO_VERSION", "unknown"),
        send_default_pii=True,
        traces_sample_rate=0.0,
        profiles_sample_rate=0.0,
    )

    # Sentry creates an issue for anything logged with logger.error();
    # we want the exceptions themselves, not these error lines
    ignore_logger("plugin_runner_logger")

    global_scope = sentry_sdk.get_global_scope()

    global_scope.set_tag("customer", CUSTOMER_IDENTIFIER)
    global_scope.set_tag("logger", "python")
    global_scope.set_tag("source", "plugin-runner")
    global_scope.set_tag("production_customer", "yes" if IS_PRODUCTION_CUSTOMER else "no")

# when we import plugins we'll use the module name directly so we need to add the plugin
# directory to the path
sys.path.append(PLUGIN_DIRECTORY)

Plugin = TypedDict(
    "Plugin",
    {
        "active": bool,
        "class": Any,
        "sandbox": Any,
        "handler": Any,
        "secrets": dict[str, str],
    },
)

# a global dictionary of loaded plugins
LOADED_PLUGINS: dict[str, Plugin] = {}

# a global dictionary of values made available to all plugins
ENVIRONMENT: dict = {
    "CUSTOMER_IDENTIFIER": CUSTOMER_IDENTIFIER,
}

# a global dictionary of events to handler class names
EVENT_HANDLER_MAP: dict[str, list] = defaultdict(list)


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


ApplicationConfig = TypedDict(
    "ApplicationConfig",
    {
        "class": str,
        "description": str,
        "icon": str,
        "scope": str,
    },
)


class Components(TypedDict):
    """Components."""

    protocols: list[Protocol]
    commands: list[dict]
    content: list[dict]
    effects: list[dict]
    views: list[dict]
    applications: list[ApplicationConfig]


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

    sandbox: Sandbox

    def HandleEvent(self, request: EventRequest, context: Any) -> Iterable[EventResponse]:
        """This is invoked when an event comes in."""
        event = Event(request)
        with metrics.measure(
            metrics.get_qualified_name(self.HandleEvent), extra_tags={"event": event.name}
        ):
            event_type = event.type
            event_name = event.name
            relevant_plugins = EVENT_HANDLER_MAP[event_name]
            relevant_plugin_handlers = []

            log.debug(f"Processing {relevant_plugins} for {event_name}")
            sentry_sdk.set_tag("event-name", event_name)

            if relevant_plugins:
                # Send the Django request_started signal
                request_started.send(sender=self.__class__)

            if event_type in [EventType.PLUGIN_CREATED, EventType.PLUGIN_UPDATED]:
                plugin_name = event.target.id
                # filter only for the plugin(s) that were created/updated
                relevant_plugins = [p for p in relevant_plugins if p.startswith(f"{plugin_name}:")]
            elif event_type in {
                EventType.SIMPLE_API_AUTHENTICATE,
                EventType.SIMPLE_API_REQUEST,
                EventType.SIMPLE_API_WEBSOCKET_AUTHENTICATE,
            }:
                # The target plugin's name will be part of the home-app URL path, so other plugins that
                # respond to SimpleAPI request events are not relevant
                plugin_name = event.context["plugin_name"]
                relevant_plugins = [p for p in relevant_plugins if p.startswith(f"{plugin_name}:")]

            effect_list = []

            for plugin_name in relevant_plugins:
                log.debug(f"Processing {plugin_name}")
                sentry_sdk.set_tag("plugin-name", plugin_name)

                plugin = LOADED_PLUGINS[plugin_name]
                handler_class = plugin["class"]
                base_plugin_name = plugin_name.split(":")[0]

                secrets = plugin.get("secrets", {})

                secrets.update(
                    {"graphql_jwt": token_for_plugin(plugin_name=plugin_name, audience="home")}
                )

                try:
                    handler = handler_class(event, secrets, ENVIRONMENT)

                    if not handler.accept_event():
                        continue
                    relevant_plugin_handlers.append(handler_class)

                    classname = (
                        handler.__class__.__name__
                        if isinstance(handler, ClinicalQualityMeasure)
                        else None
                    )
                    handler_name = metrics.get_qualified_name(handler.compute)
                    with metrics.measure(
                        name=handler_name,
                        extra_tags={
                            "plugin": base_plugin_name,
                            "event": event_name,
                        },
                    ):
                        _effects = handler.compute()
                        effects = [
                            Effect(
                                type=effect.type,
                                payload=effect.payload,
                                plugin_name=base_plugin_name,
                                classname=classname,
                                handler_name=handler_name,
                            )
                            for effect in _effects
                        ]

                        effects = validate_effects(effects)

                        apply_effects_to_context(effects, event=event)

                        log.info(f"{plugin_name}.compute() completed.")

                except Exception as e:
                    log.error(f"Encountered exception in plugin {plugin_name}:")

                    for error_line_with_newlines in traceback.format_exception(e):
                        for error_line in error_line_with_newlines.split("\n"):
                            log.error(error_line)

                    sentry_sdk.capture_exception(e)
                    continue

                effect_list += effects

            sentry_sdk.set_tag("plugin-name", None)

            # Special handling for SimpleAPI requests: if there were no relevant handlers (as determined
            # by calling ignore_event on handlers), then set the effects list to be a single 404 Not
            # Found response effect. If multiple handlers were able to respond, log an error and set the
            # effects list to be a single 500 Internal Server Error response effect.
            if event.type in {EventType.SIMPLE_API_AUTHENTICATE, EventType.SIMPLE_API_REQUEST}:
                if len(relevant_plugin_handlers) == 0:
                    effect_list = [Response(status_code=HTTPStatus.NOT_FOUND).apply()]
                elif len(relevant_plugin_handlers) > 1:
                    log.error(
                        f"Multiple handlers responded to {EventType.Name(EventType.SIMPLE_API_REQUEST)}"
                        f" {event.context['path']}"
                    )
                    effect_list = [Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR).apply()]
            if event.type == EventType.SIMPLE_API_WEBSOCKET_AUTHENTICATE:
                if len(relevant_plugin_handlers) == 0:
                    effect_list = [DenyConnection().apply()]
                elif len(relevant_plugin_handlers) > 1:
                    log.error(
                        f"Multiple handlers responded to {EventType.Name(EventType.SIMPLE_API_WEBSOCKET_AUTHENTICATE)}"
                        f" {event.context['channel']}"
                    )
                    effect_list = [DenyConnection().apply()]

            # Don't log anything if a plugin handler didn't actually run.
            if relevant_plugins:
                # Send the Django request_finished signal
                request_finished.send(sender=self.__class__)

                log.info(f"Responded to Event {event_name}.")

            yield EventResponse(success=True, effects=effect_list)

    def ReloadPlugins(
        self, request: ReloadPluginsRequest, context: Any
    ) -> Iterable[ReloadPluginsResponse]:
        """This is invoked when we need to reload plugins."""
        log.info("Reloading plugins...")
        try:
            publish_message(message={"action": "reload"})
        except ImportError:
            yield ReloadPluginsResponse(success=False)
        else:
            yield ReloadPluginsResponse(success=True)


STOP_SYNCHRONIZER = threading.Event()


def synchronize_plugins(run_once: bool = False) -> None:
    """
    Listen for messages on the pubsub channel that will indicate it is
    necessary to reinstall and reload plugins.
    """
    log.info(f'synchronize_plugins: listening for messages on pubsub channel "{CHANNEL_NAME}"')

    _, pubsub = get_client()

    pubsub.psubscribe(CHANNEL_NAME)

    while not STOP_SYNCHRONIZER.is_set():
        message = pubsub.get_message(ignore_subscribe_messages=True, timeout=5.0)

        if message is None:
            continue

        log.info(f'synchronize_plugins: received message from pubsub channel "{CHANNEL_NAME}"')

        message_type = message.get("type", "")

        if message_type != "pmessage":
            continue

        data = pickle.loads(message.get("data", pickle.dumps({})))

        if "action" not in data:
            continue

        if data["action"] == "reload":
            log.info("synchronize_plugins: installing/reloading plugins for action=reload")

            try:
                install_plugins()
            except Exception as e:
                log.error(f"synchronize_plugins: install_plugins failed: {e}")
                sentry_sdk.capture_exception(e)

            try:
                load_plugins()
            except Exception as e:
                log.error(f"synchronize_plugins: load_plugins failed: {e}")
                sentry_sdk.capture_exception(e)

        if run_once:
            break


def synchronize_plugins_and_report_errors() -> None:
    """
    Run synchronize_plugins() in perpetuity and report any encountered errors.
    """
    log.info("synchronize_plugins: starting loop...")

    while not STOP_SYNCHRONIZER.is_set():
        try:
            synchronize_plugins()
        except Exception as e:
            log.error(f"synchronize_plugins: error: {e}")
            sentry_sdk.capture_exception(e)

        # don't crush redis if we're retrying in a tight loop
        sleep(0.5)


def validate_effects(effects: list[Effect]) -> list[Effect]:
    """
    Validates the effects based on predefined rules.

    Keeps only the first AUTOCOMPLETE_SEARCH_RESULTS effect and preserve all
    non-search-related effects.
    """
    seen_autocomplete = False
    validated_effects = []

    for effect in effects:
        if effect.type == EffectType.AUTOCOMPLETE_SEARCH_RESULTS:
            if seen_autocomplete:
                log.warning("Discarding additional AUTOCOMPLETE_SEARCH_RESULTS effect.")
                continue

            seen_autocomplete = True

        validated_effects.append(effect)

    return validated_effects


def apply_effects_to_context(effects: list[Effect], event: Event) -> Event:
    """Applies AUTOCOMPLETE_SEARCH_RESULTS effects to the event context.
    If we are dealing with a search event, we need to update the context with the search results.
    """
    event_name = event.name

    # Skip if the event is not a search event
    if not event_name.endswith("__PRE_SEARCH") and not event_name.endswith("__POST_SEARCH"):
        return event

    for effect in effects:
        if effect.type == EffectType.AUTOCOMPLETE_SEARCH_RESULTS:
            event.context["results"] = json.loads(effect.payload)
            # Stop processing effects if we've found a AUTOCOMPLETE_SEARCH_RESULTS
            break

    return event


def find_modules(base_path: pathlib.Path, prefix: str | None = None) -> list[str]:
    """Find all modules in the specified package path."""
    modules: list[str] = []

    for _, module_name, is_pkg in pkgutil.iter_modules(
        [base_path.as_posix()],
    ):
        if is_pkg:
            modules = modules + find_modules(
                base_path / module_name,
                prefix=f"{prefix}.{module_name}" if prefix else module_name,
            )
        else:
            modules.append(f"{prefix}.{module_name}" if prefix else module_name)

    return modules


def publish_message(message: dict) -> None:
    """Publish a message to the pubsub channel."""
    log.info(f'Publishing message to pubsub channel "{CHANNEL_NAME}"')
    client, _ = get_client()

    client.publish(CHANNEL_NAME, pickle.dumps(message))


def get_client() -> tuple[redis.Redis, redis.client.PubSub]:
    """Return a Redis client and pubsub object."""
    client = redis.from_url(
        REDIS_ENDPOINT,
        retry=Retry(backoff=ExponentialBackoff(), retries=10),
        retry_on_error=[ConnectionError, TimeoutError, ConnectionResetError],
        health_check_interval=1,
    )
    pubsub = client.pubsub()

    return client, pubsub


def load_or_reload_plugin(path: pathlib.Path) -> bool:
    """Given a path, load or reload a plugin."""
    log.info(f'Loading plugin at "{path}"')

    manifest_file = path / MANIFEST_FILE_NAME
    manifest_json_str = manifest_file.read_text()

    # the name is the folder name underneath the plugins directory
    name = path.name

    try:
        manifest_json: PluginManifest = json.loads(manifest_json_str)
    except Exception as e:
        log.error(f'Unable to load plugin "{name}": {e}')
        sentry_sdk.capture_exception(e)

        return False

    secrets_file = path / SECRETS_FILE_NAME
    secrets_json = {}

    if secrets_file.exists():
        try:
            secrets_json = json.load(secrets_file.open())
        except Exception as e:
            log.error(f'Unable to load secrets for plugin "{name}": {str(e)}')
            sentry_sdk.capture_exception(e)

    # TODO add existing schema validation from Michela here
    try:
        handlers = manifest_json["components"].get("protocols", []) + manifest_json[
            "components"
        ].get("applications", [])
    except Exception as e:
        log.error(f'Unable to load plugin "{name}": {str(e)}')
        sentry_sdk.capture_exception(e)

        return False

    any_failed = False

    for handler in handlers:
        # TODO add class colon validation to existing schema validation
        # TODO when we encounter an exception here, disable the plugin in response
        try:
            handler_module, handler_class = handler["class"].split(":")
            name_and_class = f"{name}:{handler_module}:{handler_class}"
        except ValueError as e:
            log.error(f'Unable to parse class for plugin "{name}": "{handler["class"]}"')
            sentry_sdk.capture_exception(e)

            any_failed = True

            continue

        try:
            sandbox = sandbox_from_module(path.parent, handler_module)
            result = sandbox.execute()

            if name_and_class in LOADED_PLUGINS:
                log.info(f"Reloading plugin '{name_and_class}'")

                LOADED_PLUGINS[name_and_class]["active"] = True

                LOADED_PLUGINS[name_and_class]["class"] = result[handler_class]
                LOADED_PLUGINS[name_and_class]["sandbox"] = result
                LOADED_PLUGINS[name_and_class]["secrets"] = secrets_json
            else:
                log.info(f"Loading plugin '{name_and_class}'")

                LOADED_PLUGINS[name_and_class] = {
                    "active": True,
                    "class": result[handler_class],
                    "sandbox": result,
                    "handler": handler,
                    "secrets": secrets_json,
                }
        except Exception as e:
            log.error(f'Error importing module "{name_and_class}": {e}')

            for error_line in traceback.format_exception(e):
                log.error(error_line)

            sentry_sdk.capture_exception(e)

            any_failed = True

    return not any_failed


def refresh_event_type_map() -> None:
    """Ensure the event subscriptions are up to date."""
    EVENT_HANDLER_MAP.clear()

    for name, plugin in LOADED_PLUGINS.items():
        if hasattr(plugin["class"], "RESPONDS_TO"):
            responds_to = plugin["class"].RESPONDS_TO

            if isinstance(responds_to, str):
                EVENT_HANDLER_MAP[responds_to].append(name)
            elif isinstance(responds_to, list):
                for event in responds_to:
                    EVENT_HANDLER_MAP[event].append(name)
            else:
                log.warning(f"Unknown RESPONDS_TO type: {type(responds_to)}")


@measured
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

    # load or reload each plugin
    for plugin_path in plugin_paths:
        load_or_reload_plugin(plugin_path)

    # if a plugin has been uninstalled/disabled remove it from LOADED_PLUGINS
    for name, plugin in LOADED_PLUGINS.copy().items():
        if not plugin["active"]:
            del LOADED_PLUGINS[name]

    refresh_event_type_map()


# NOTE: specified_plugin_paths powers the `canvas run-plugins` command
def main(specified_plugin_paths: list[str] | None = None) -> None:
    """Run the server and the synchronize_plugins loop."""
    port = "50051"

    executor = ThreadPoolExecutor(max_workers=settings.PLUGIN_RUNNER_MAX_WORKERS)
    server = grpc.server(thread_pool=executor)
    server.add_insecure_port("127.0.0.1:" + port)

    add_PluginRunnerServicer_to_server(PluginRunner(), server)

    log.info(f"Starting server, listening on port {port}")

    # Only install plugins and start the synchronizer thread if the plugin runner was not started
    # from the CLI
    synchronizer_thread = threading.Thread(target=synchronize_plugins_and_report_errors)
    if specified_plugin_paths is None:
        install_plugins()
        STOP_SYNCHRONIZER.clear()
        synchronizer_thread.start()

    load_plugins(specified_plugin_paths)

    server.start()

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown(wait=True, cancel_futures=True)
        if synchronizer_thread.is_alive():
            STOP_SYNCHRONIZER.set()
            synchronizer_thread.join()


if __name__ == "__main__":
    main()
