import base64
import json
import os
import pathlib
import pickle
import pkgutil
import sys
import threading
from collections import defaultdict
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from http import HTTPStatus
from time import sleep
from typing import Any, NotRequired, TypedDict, cast

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
from canvas_generated.messages.plugins_pb2 import (
    ReloadPluginRequest,
    ReloadPluginResponse,
    ReloadPluginsRequest,
    ReloadPluginsResponse,
    UnloadPluginRequest,
    UnloadPluginResponse,
)
from canvas_generated.services.plugin_runner_pb2_grpc import (
    PluginRunnerServicer,
    add_PluginRunnerServicer_to_server,
)
from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import Response
from canvas_sdk.events import Event, EventRequest, EventResponse, EventType
from canvas_sdk.handlers.simple_api.websocket import DenyConnection
from canvas_sdk.protocols import ClinicalQualityMeasure
from canvas_sdk.templates.utils import _engine_for_plugin
from canvas_sdk.utils import metrics
from canvas_sdk.utils.metrics import measured
from canvas_sdk.v1.plugin_database_context import plugin_database_context
from logger import log
from plugin_runner.authentication import token_for_plugin
from plugin_runner.exceptions import (
    NamespaceAccessError,
    PluginInstallationError,
    PluginUninstallationError,
)
from plugin_runner.installation import (
    enabled_plugins,
    install_plugin,
    install_plugins,
    uninstall_plugin,
)
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
    # Lazy import for faster reload time in dev
    from sentry_sdk.integrations.executing import ExecutingIntegration
    from sentry_sdk.integrations.pure_eval import PureEvalIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=ENV,
        integrations=[
            ExecutingIntegration(),
            PureEvalIntegration(),
        ],
        release=os.getenv("CANVAS_PLUGINS_REPO_VERSION", "unknown"),
        send_default_pii=True,
        spotlight=False,
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

Plugin = TypedDict(
    "Plugin",
    {
        "active": bool,
        "class": Any,
        "sandbox": Any,
        "handler": Any,
        "secrets": dict[str, str],
        "namespace_config": NotRequired[dict[str, str] | None],
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


class CustomData(TypedDict):
    """Configuration for custom data storage in a shared namespace."""

    namespace: str  # The namespace schema name (e.g., "acme_org__shared")
    access: str  # "read" or "read_write"


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
    custom_data: NotRequired[CustomData]


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
            elif event_type in {
                EventType.REVENUE__PAYMENT_PROCESSOR__CHARGE,
                EventType.REVENUE__PAYMENT_PROCESSOR__SELECTED,
                EventType.REVENUE__PAYMENT_PROCESSOR__PAYMENT_METHODS__LIST,
                EventType.REVENUE__PAYMENT_PROCESSOR__PAYMENT_METHODS__ADD,
                EventType.REVENUE__PAYMENT_PROCESSOR__PAYMENT_METHODS__REMOVE,
            }:
                # The target plugin's name will be part of the payment processor identifier, so other plugins that
                # respond to payment processor charge events are not relevant
                try:
                    plugin_name = (
                        base64.b64decode(event.context["identifier"]).decode("utf-8").split(".")[0]
                    )
                    relevant_plugins = [
                        p for p in relevant_plugins if p.startswith(f"{plugin_name}:")
                    ]
                except Exception as ex:
                    log.exception(
                        f"Failed to decode identifier for event {event_name} with context {event.context}"
                    )
                    sentry_sdk.capture_exception(ex)
                    relevant_plugins = []

            effect_list = []

            for plugin_name in relevant_plugins:
                log.debug(f"Processing {plugin_name}")
                sentry_sdk.set_tag("plugin-name", plugin_name)

                plugin = LOADED_PLUGINS[plugin_name]
                handler_class = plugin["class"]
                base_plugin_name = plugin_name.split(":")[0]
                namespace_config = plugin.get("namespace_config")

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

                    # Determine namespace and access level for database context
                    db_namespace = namespace_config["namespace"] if namespace_config else None
                    db_access_level = (
                        namespace_config["access_level"] if namespace_config else "read"
                    )

                    with (
                        metrics.measure(
                            name=handler_name,
                            track_queries=True,
                            extra_tags={
                                "plugin": base_plugin_name,
                                "event": event_name,
                            },
                        ),
                        plugin_database_context(
                            base_plugin_name,
                            namespace=db_namespace,
                            access_level=db_access_level,
                        ),
                    ):
                        _effects = handler.compute()
                        effects = [
                            Effect(
                                type=effect.type,
                                payload=effect.payload,
                                plugin_name=base_plugin_name,
                                classname=classname,
                                handler_name=handler_name,
                                actor=event.actor.id,
                                source=event.source,
                            )
                            for effect in _effects
                        ]
                        effects = validate_effects(effects)

                        apply_effects_to_context(effects, event=event)

                        log.info(f"{plugin_name}.compute() completed.")

                except Exception as e:
                    log.exception(f"Encountered exception in plugin {plugin_name}")
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
        log.info("Reloading all plugins...")

        message = {"action": "reload"}

        try:
            publish_message(message=message)
        except ImportError:
            yield ReloadPluginsResponse(success=False)
        else:
            yield ReloadPluginsResponse(success=True)

    def ReloadPlugin(
        self, request: ReloadPluginRequest, context: Any
    ) -> Iterable[ReloadPluginResponse]:
        """This is invoked when we need to reload a specific plugin."""
        log.info(f'Reloading plugin "{request.plugin}"...')

        message = {
            "action": "reload",
            "plugin": request.plugin,
        }
        try:
            publish_message(message=message)
        except ImportError:
            yield ReloadPluginResponse(success=False)
        else:
            yield ReloadPluginResponse(success=True)

    def UnloadPlugin(
        self, request: UnloadPluginRequest, context: Any
    ) -> Iterable[UnloadPluginResponse]:
        """This is invoked when we need to reload a specific plugin."""
        log.info(f'Unloading plugin "{request.plugin}"...')

        message = {
            "action": "unload",
            "plugin": request.plugin,
        }
        try:
            publish_message(message=message)
        except ImportError:
            yield UnloadPluginResponse(success=False)
        else:
            yield UnloadPluginResponse(success=True)


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

        # clear the template engine cache so that any template changes
        # from plugins are picked up
        _engine_for_plugin.cache_clear()
        plugin_name = data.get("plugin", None)
        try:
            if data["action"] == "reload":
                if plugin_name:
                    plugin = enabled_plugins([plugin_name]).get(plugin_name, None)

                    if plugin:
                        log.info(
                            f'synchronize_plugins: installing/reloading plugin "{plugin_name}" for action=reload'
                        )
                        unload_plugin(plugin_name)
                        install_plugin(plugin_name, attributes=plugin)
                        plugin_dir = pathlib.Path(PLUGIN_DIRECTORY) / plugin_name
                        load_plugin(plugin_dir.resolve())
                else:
                    log.info("synchronize_plugins: installing/reloading plugins for action=reload")
                    install_plugins()
                    load_plugins()
            elif data["action"] == "unload" and plugin_name:
                log.info(f'synchronize_plugins: uninstalling plugin "{plugin_name}"')
                unload_plugin(plugin_name)
                uninstall_plugin(plugin_name)
        except Exception as e:
            if isinstance(e, PluginInstallationError):
                message = "install_plugins failed"
            elif isinstance(e, PluginUninstallationError):
                message = "uninstall_plugin failed"
            else:
                message = "load_plugins failed"

            if plugin_name:
                message += f' for plugin "{plugin_name}"'

            log.exception(f"synchronize_plugins: {message}")
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
            log.exception("synchronize_plugins: error")
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


def resolve_namespace_secret(
    plugin_name: str,
    namespace_name: str,
    declared_access: str,
    secrets_json: dict[str, Any],
) -> str:
    """Determine and retrieve the access key secret for namespace verification.

    Maps declared_access to the appropriate secret name and retrieves it from
    secrets_json. Raises NamespaceAccessError if the secret is not configured.

    Returns the secret value.
    """
    secret_name = "read_write_access_key" if declared_access == "read_write" else "read_access_key"

    secret_value = secrets_json.get(secret_name)
    if not secret_value:
        raise NamespaceAccessError(
            f"Plugin '{plugin_name}' declares namespace '{namespace_name}' with '{declared_access}' access "
            f"but secret '{secret_name}' is not configured. "
            f"Ensure the secret is listed in the manifest's 'secrets' array and has a value set."
        )

    return secret_value


def verify_plugin_namespace_access(
    plugin_name: str,
    custom_data: CustomData,
    secrets_json: dict[str, Any],
) -> dict[str, str]:
    """Verify a plugin's namespace access and return the namespace config.

    Parses namespace declaration from custom_data, resolves the access key secret,
    verifies it against the namespace's auth table, and checks access level sufficiency.

    Returns {"namespace": ..., "access_level": ...} on success.
    Raises NamespaceAccessError on any verification failure.
    """
    from plugin_runner.installation import check_namespace_auth_key

    namespace_name = custom_data["namespace"]
    declared_access = custom_data["access"]

    try:
        secret_value = resolve_namespace_secret(
            plugin_name, namespace_name, declared_access, secrets_json
        )

        # Verify access against namespace's auth table
        granted_access = check_namespace_auth_key(namespace_name, secret_value)
        if granted_access is None:
            raise NamespaceAccessError(
                f"Plugin '{plugin_name}' denied access to namespace '{namespace_name}': "
                f"the secret value is not a valid access key for this namespace. "
                f"Verify the key matches what was generated when the namespace was created."
            )

        # Check that declared access doesn't exceed granted access
        if declared_access == "read_write" and granted_access == "read":
            raise NamespaceAccessError(
                f"Plugin '{plugin_name}' requests 'read_write' access to namespace '{namespace_name}' "
                f"but the provided key only grants 'read' access. "
                f"Use the 'read_write_access_key' secret for write access."
            )
    except NamespaceAccessError:
        raise
    except Exception as e:
        log.exception(f"Failed to verify namespace access for plugin '{plugin_name}'")
        sentry_sdk.capture_exception(e)
        raise NamespaceAccessError(
            f"Unexpected error verifying namespace access for plugin '{plugin_name}': {e}"
        ) from e

    return {
        "namespace": namespace_name,
        "access_level": declared_access,
    }


def load_or_reload_plugin(path: pathlib.Path) -> bool:
    """Given a path, load or reload a plugin."""
    log.info(f'Loading plugin at "{path}"')

    # the name is the folder name underneath the plugins directory
    name = path.name

    manifest_file = path / MANIFEST_FILE_NAME

    # If installed via `canvas install` we can rely on the manifest file
    # existing. If installed via another method we still need to avoid crashing
    # the entire runner if there's no manifest.
    if not manifest_file.exists():
        log.exception(f'Unable to load plugin "{name}", missing {MANIFEST_FILE_NAME}')
        return False

    manifest_json_str = manifest_file.read_text()

    try:
        manifest_json: PluginManifest = json.loads(manifest_json_str)
    except Exception as e:
        log.exception(f'Unable to load plugin "{name}"')
        sentry_sdk.capture_exception(e)

        return False

    secrets_file = path / SECRETS_FILE_NAME
    secrets_json = {}

    if secrets_file.exists():
        try:
            secrets_json = json.load(secrets_file.open())
        except Exception as e:
            log.exception(f'Unable to load secrets for plugin "{name}"')
            sentry_sdk.capture_exception(e)

    # Process custom_data configuration
    namespace_config: dict | None = None
    custom_data = manifest_json.get("custom_data")
    if custom_data:
        namespace_config = verify_plugin_namespace_access(name, custom_data, secrets_json)
        log.info(
            f"Plugin '{name}' authorized for namespace '{namespace_config['namespace']}' "
            f"with '{namespace_config['access_level']}' access"
        )

    # TODO add existing schema validation from Michela here
    try:
        components = manifest_json["components"]
        handlers = (
            cast(list, components.get("protocols", []))
            + cast(list, components.get("applications", []))
            + cast(list, components.get("handlers", []))
        )
    except Exception as e:
        log.exception(f'Unable to load plugin "{name}"')
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
            log.exception(f'Unable to parse class for plugin "{name}": "{handler["class"]}"')
            sentry_sdk.capture_exception(e)

            any_failed = True

            continue

        try:
            sandbox = sandbox_from_module(path.parent, handler_module)
            result = sandbox.execute()

            if name_and_class in LOADED_PLUGINS:
                log.info(f"Reloading handler '{name_and_class}'")

                LOADED_PLUGINS[name_and_class]["active"] = True

                LOADED_PLUGINS[name_and_class]["class"] = result[handler_class]
                LOADED_PLUGINS[name_and_class]["sandbox"] = result
                LOADED_PLUGINS[name_and_class]["secrets"] = secrets_json
                LOADED_PLUGINS[name_and_class]["namespace_config"] = namespace_config
            else:
                log.info(f'Loading handler "{name_and_class}"')

                LOADED_PLUGINS[name_and_class] = {
                    "active": True,
                    "class": result[handler_class],
                    "sandbox": result,
                    "handler": handler,
                    "secrets": secrets_json,
                    "namespace_config": namespace_config,
                }
        except Exception as e:
            log.exception(f"Error importing module '{name_and_class}'")
            sentry_sdk.capture_exception(e)
            any_failed = True

    return not any_failed


def unload_plugin(name: str) -> None:
    """Unload a plugin by its name."""
    handlers_removed = False

    for handler_name in LOADED_PLUGINS.copy():
        if handler_name.startswith(f"{name}:"):
            log.info(f'Unloading handler "{handler_name}"')
            del LOADED_PLUGINS[handler_name]
            handlers_removed = True

    if handlers_removed:
        # Refresh the event type map to remove any handlers for the unloaded plugin
        refresh_event_type_map()
    else:
        log.warning(f"No handlers found for plugin '{name}' to unload.")


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
        # Add plugin directory to path only when actually loading plugins (not at module import time)
        # to avoid polluting Python's import cache during test collection
        if PLUGIN_DIRECTORY not in sys.path:
            sys.path.append(PLUGIN_DIRECTORY)

        candidates = os.listdir(PLUGIN_DIRECTORY)

        # convert to Paths
        plugin_paths = [pathlib.Path(os.path.join(PLUGIN_DIRECTORY, name)) for name in candidates]

    # get all directories under the plugin directory
    plugin_paths = [path for path in plugin_paths if path.is_dir()]

    # load or reload each plugin
    for plugin_path in plugin_paths:
        try:
            load_or_reload_plugin(plugin_path)
        except NamespaceAccessError as e:
            log.error(f"Namespace access error loading plugin from '{plugin_path}': {e}")
            sentry_sdk.capture_exception(e)
        except Exception as e:
            log.exception(f"Unexpected error loading plugin from '{plugin_path}'")
            sentry_sdk.capture_exception(e)

    # if a plugin has been uninstalled/disabled remove it from LOADED_PLUGINS
    for name, plugin in LOADED_PLUGINS.copy().items():
        if not plugin["active"]:
            del LOADED_PLUGINS[name]

    refresh_event_type_map()


@measured
def load_plugin(path: pathlib.Path) -> None:
    """Load a plugin from the specified path."""
    try:
        load_or_reload_plugin(path)
    except NamespaceAccessError as e:
        log.error(f"Namespace access error loading plugin from '{path}': {e}")
        sentry_sdk.capture_exception(e)
    except Exception as e:
        log.exception(f"Unexpected error loading plugin from '{path}'")
        sentry_sdk.capture_exception(e)
    refresh_event_type_map()


# NOTE: specified_plugin_paths powers the `canvas run-plugins` command
def main(specified_plugin_paths: list[str] | None = None) -> None:
    """Run the server and the synchronize_plugins loop."""
    port = "50051"

    executor = ThreadPoolExecutor(max_workers=settings.PLUGIN_RUNNER_MAX_WORKERS)
    server = grpc.server(
        thread_pool=executor,
        options=(
            # set max message lengths to 64mb
            ("grpc.max_receive_message_length", 64 * 1024 * 1024),
            ("grpc.max_send_message_length", 64 * 1024 * 1024),
        ),
    )
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
