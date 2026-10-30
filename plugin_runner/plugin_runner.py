import base64
import json
import os
import pathlib
import pkgutil
import signal
import sys
import threading
import warnings
from collections import defaultdict
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from contextlib import nullcontext
from dataclasses import dataclass
from http import HTTPStatus
from time import monotonic, sleep
from typing import TYPE_CHECKING, Any, NotRequired, TypedDict, cast

import anthropic
import grpc
import redis
import sentry_sdk
from django.apps import apps as django_apps
from django.core.signals import request_finished, request_started
from redis.backoff import ExponentialBackoff
from redis.exceptions import ConnectionError, TimeoutError
from redis.retry import Retry
from sentry_sdk.integrations.logging import ignore_logger

import settings
from canvas_generated.messages.effects_pb2 import Effect, EffectType
from canvas_generated.messages.events_pb2 import AgentRunSummary, AgentToolCall
from canvas_generated.messages.plugins_pb2 import (
    GetRegisteredEventTypesRequest,
    GetRegisteredEventTypesResponse,
    ReloadPluginRequest,
    ReloadPluginResponse,
    ReloadPluginsRequest,
    ReloadPluginsResponse,
    RunAgentRequest,
    UnloadPluginRequest,
    UnloadPluginResponse,
)
from canvas_generated.services.plugin_runner_pb2_grpc import (
    PluginRunnerServicer,
    add_PluginRunnerServicer_to_server,
)
from canvas_sdk.agents.run_record import RunDeadlineExceeded
from canvas_sdk.effects.simple_api import Response
from canvas_sdk.events import Event, EventRequest, EventResponse, EventType
from canvas_sdk.handlers.simple_api.websocket import DenyConnection
from canvas_sdk.protocols import ClinicalQualityMeasure
from canvas_sdk.templates.utils import _engine_for_plugin
from canvas_sdk.utils import metrics
from canvas_sdk.utils.metrics import measured
from canvas_sdk.v1.data.base import IS_SQLITE
from canvas_sdk.v1.plugin_database_context import plugin_database_context
from logger import log
from logger.logger import plugin_context
from plugin_runner.authentication import token_for_plugin
from plugin_runner.ddl import generate_plugin_migrations
from plugin_runner.event_registry import EventRegistry
from plugin_runner.exceptions import (
    NamespaceAccessError,
    PluginInstallationError,
    PluginUninstallationError,
)
from plugin_runner.installation import (
    enabled_plugins,
    install_plugin,
    install_plugins,
    register_plugin_app_config,
    uninstall_plugin,
)
from plugin_runner.sandbox import EvaluatedModules, Sandbox, SandboxMode, sandbox_from_module
from plugin_runner.sandbox_allowlists import (
    AllowlistUnavailable,
    is_allowlisted,
    is_always_legacy,
)
from plugin_runner.sandbox_compatibility import find_legacy_constructs
from plugin_runner.usage import permitted_usage, usage_units
from settings import (
    CHANNEL_NAME,
    CUSTOMER_IDENTIFIER,
    ENV,
    INSTALLATION_TIME_ZONE,
    IS_PRODUCTION_CUSTOMER,
    MANIFEST_FILE_NAME,
    PLUGIN_DIRECTORY,
    PLUGIN_RUNNER_EVENT_REGISTRY_PATH,
    PLUGIN_RUNNER_MAX_AGENT_RUNS,
    REDIS_ENDPOINT,
    SECRETS_FILE_NAME,
    SENTRY_DSN,
)

if TYPE_CHECKING:
    from canvas_sdk.agents.run_record import RunRecorder

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
        "usage_units": NotRequired[frozenset[str]],
    },
)

# a global dictionary of loaded plugins
LOADED_PLUGINS: dict[str, Plugin] = {}

# a global dictionary of values made available to all plugins
ENVIRONMENT: dict = {
    "CUSTOMER_IDENTIFIER": CUSTOMER_IDENTIFIER,
    "INSTALLATION_TIME_ZONE": INSTALLATION_TIME_ZONE,
}

# a global dictionary of events to handler class names
EVENT_HANDLER_MAP: dict[str, list] = defaultdict(list)

# the event types in EVENT_HANDLER_MAP, published to home-app so it can skip the rest
EVENT_REGISTRY = EventRegistry(PLUGIN_RUNNER_EVENT_REGISTRY_PATH)


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


_sqlite_schema_initialized = False


def _ensure_sqlite_schema() -> None:
    """Create the framework tables (custom_attribute, attribute_hub) in the
    SQLite database if they don't already exist.

    Same as the test database setup and the --reset-db path in run_plugins.
    Must be called while the writable connection is the default.
    """
    global _sqlite_schema_initialized
    if _sqlite_schema_initialized:
        return

    from django.core.management import call_command

    call_command("migrate", run_syncdb=True, verbosity=0)
    _sqlite_schema_initialized = True


def llm_error_kind(exc: anthropic.APIError) -> str:
    """Whether a failed gateway call is worth retrying.

    ``LLM_UNAVAILABLE`` is an outage: the gateway or Anthropic answered 5xx or 429,
    or the connection failed. ``LLM_REFUSED`` is everything the same request would
    hit again: a budget or ceiling (402), a model not enabled (404), a bad key
    (401), or a refused feature (400).
    """
    if isinstance(exc, anthropic.APIConnectionError):
        return "LLM_UNAVAILABLE"
    if isinstance(exc, anthropic.APIStatusError) and (
        exc.status_code >= 500 or exc.status_code == 429
    ):
        return "LLM_UNAVAILABLE"
    return "LLM_REFUSED"


AGENT_RUN_SLOTS = threading.BoundedSemaphore(PLUGIN_RUNNER_MAX_AGENT_RUNS)


def _agent_run_summary(
    recorder: "RunRecorder",
    *,
    effects_returned: int = 0,
    effects_dropped: int = 0,
) -> AgentRunSummary:
    """What a run did, for home-app's run record."""
    return AgentRunSummary(
        model_calls=recorder.model_calls,
        stop_reason=recorder.stop_reason,
        effects_returned=effects_returned,
        effects_dropped=effects_dropped,
        tool_calls=[
            AgentToolCall(
                name=call.name,
                ok=call.ok,
                error_type=call.error_type,
                duration_ms=call.duration_ms,
            )
            for call in recorder.tool_calls
        ],
    )


def _invoke_agent_hook(agent: Any, hook_name: str, *args: Any) -> None:
    """Invoke an :class:`AgentPlugin` lifecycle hook, swallowing any exception.

    Lifecycle hooks (``on_run_start``, ``on_run_end``, ``on_run_error``) are
    observability seams — they emit telemetry, log timings, etc. — not core
    logic. A hook that raises is a bug in the plugin's *observability* code,
    and must not prevent the agent's actual ``load_state`` → ``run`` →
    ``save_state`` lifecycle from completing (or its error from propagating).
    Anything thrown by the hook is logged and discarded.
    """
    try:
        getattr(agent, hook_name)(*args)
    except Exception:
        log.exception(f"RunAgent: agent hook {hook_name!r} raised; ignoring")


class PluginRunner(PluginRunnerServicer):
    """This process runs provided plugins that register interest in incoming events."""

    sandbox: Sandbox

    def HandleEvent(self, request: EventRequest, context: Any) -> Iterable[EventResponse]:
        """This is invoked when an event comes in."""
        event = Event(request)
        # Only time events a loaded handler responds to: an event-tagged series for
        # every no-op event type would dominate plugins.timings cardinality.
        timing = (
            metrics.measure(
                metrics.get_qualified_name(self.HandleEvent), extra_tags={"event": event.name}
            )
            if EVENT_HANDLER_MAP.get(event.name)
            else nullcontext()
        )

        with timing:
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
                plugin = LOADED_PLUGINS[plugin_name]
                handler_class = plugin["class"]
                base_plugin_name, handler_path, handler_classname = plugin_name.split(":")

                sentry_sdk.set_tag("plugin-name", plugin_name)

                with plugin_context(f"{handler_path}.{handler_classname}"):
                    log.debug(f"Processing {plugin_name}")

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
                                track_memory_usage=True,
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
                            if _effects is None:
                                # Plugin authors sometimes forget to return their
                                # effects list. Treat as empty with a warning so
                                # the author can fix it, instead of raising
                                # ``TypeError: 'NoneType' object is not iterable``
                                # (KOALA-5365 / HOME-APP-RT8).
                                log.warning(
                                    f"{handler_name} returned None from compute(); "
                                    "expected an iterable of effects. Treating as "
                                    "an empty list."
                                )
                                _effects = []
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
                            effects = permitted_usage(
                                effects, plugin.get("usage_units", frozenset())
                            )
                            effects = validate_effects(effects)

                            apply_effects_to_context(effects, event=event)

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
                    effect_list = [Response(status_code=HTTPStatus.NOT_FOUND).apply().to_proto()]
                elif len(relevant_plugin_handlers) > 1:
                    log.error(
                        f"Multiple handlers responded to {EventType.Name(EventType.SIMPLE_API_REQUEST)}"
                        f" {event.context['path']}"
                    )
                    effect_list = [
                        Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR).apply().to_proto()
                    ]
            if event.type == EventType.SIMPLE_API_WEBSOCKET_AUTHENTICATE:
                if len(relevant_plugin_handlers) == 0:
                    effect_list = [DenyConnection().apply().to_proto()]
                elif len(relevant_plugin_handlers) > 1:
                    log.error(
                        f"Multiple handlers responded to {EventType.Name(EventType.SIMPLE_API_WEBSOCKET_AUTHENTICATE)}"
                        f" {event.context['channel_name']}"
                    )
                    effect_list = [DenyConnection().apply().to_proto()]

            # Only bookend the request if a plugin handler actually ran.
            if relevant_plugins:
                # Send the Django request_finished signal
                request_finished.send(sender=self.__class__)

            yield EventResponse(success=True, effects=effect_list)

    def RunAgent(self, request: RunAgentRequest, context: Any) -> Iterable[EventResponse]:
        """Invoke an AgentPlugin subclass and stream its emitted effects.

        Called by home-app's ``run_agent`` Celery task in response to a
        ``RunAgentEffect`` from a plugin trigger handler. Resolves the agent
        class from :data:`LOADED_PLUGINS`, drives
        ``load_state`` → ``run`` → ``save_state`` inside the plugin's
        database context, and yields the emitted effects in a single
        ``EventResponse``.

        home-app serializes runs on one scope with a lease it holds until the
        run's effects are dispatched, and bounds the call with a deadline the
        lease outlives. A run whose call is no longer active once ``run()``
        returns has passed that deadline, so it neither saves state nor
        returns effects. LLM access goes
        through Canvas's inference gateway: the gateway is built from the
        instance's ``INFERENCE_GATEWAY_URL`` and the plugin's own
        ``INFERENCE_GATEWAY_KEY`` secret, attributed to the plugin, agent, and run.
        Gateway refusals and outages come back as
        ``LLM_REFUSED`` and ``LLM_UNAVAILABLE`` so home-app retries only the latter.
        """
        with metrics.measure(
            metrics.get_qualified_name(self.RunAgent),
            extra_tags={"agent_id": request.agent_id},
        ):
            module_path, _, class_name = request.agent_id.partition(":")
            if not module_path or not class_name:
                log.error(f"RunAgent: invalid agent_id={request.agent_id!r}")
                yield EventResponse(success=False, effects=[])
                return

            base_plugin_name = module_path.split(".", 1)[0]
            registry_key = f"{base_plugin_name}:{module_path}:{class_name}"

            # `plugin_name` is the plugin whose handler emitted the RunAgentEffect,
            # stamped by this runner when the handler ran. An agent runs with its own
            # plugin's gateway key, data namespace, and tool grants, so only that
            # plugin may run it.
            if request.plugin_name != base_plugin_name:
                log.error(
                    f"RunAgent: plugin {request.plugin_name!r} cannot run agent "
                    f"{request.agent_id!r}, which belongs to {base_plugin_name!r}"
                )
                yield EventResponse(success=False, effects=[])
                return

            if registry_key not in LOADED_PLUGINS:
                log.error(
                    f"RunAgent: agent class not loaded — "
                    f"agent_id={request.agent_id} registry_key={registry_key}"
                )
                yield EventResponse(success=False, effects=[])
                return

            plugin = LOADED_PLUGINS[registry_key]
            agent_class = plugin["class"]
            namespace_config = plugin.get("namespace_config")

            # Late import: canvas_sdk.agents and the SDK Effect wrapper are
            # only meaningful once plugin modules have loaded.
            from canvas_sdk.agents import LLMGatewayConfigurationError
            from canvas_sdk.agents.gateway import gateway_from_plugin_secrets

            try:
                gateway = gateway_from_plugin_secrets(
                    plugin.get("secrets") or {},
                    instance=CUSTOMER_IDENTIFIER,
                    plugin=base_plugin_name,
                    agent=request.agent_id,
                    run_id=request.run_id,
                )
            except LLMGatewayConfigurationError as exc:
                log.error(f"RunAgent: cannot dispatch agent — {exc}")
                yield EventResponse(success=False, effects=[], error_kind="LLM_NOT_CONFIGURED")
                return

            try:
                trigger_payload = (
                    json.loads(request.trigger_payload) if request.trigger_payload else {}
                )
            except json.JSONDecodeError as exc:
                log.error(
                    f"RunAgent: invalid trigger_payload JSON for agent_id={request.agent_id}: {exc}"
                )
                yield EventResponse(success=False, effects=[])
                return

            db_namespace = namespace_config["namespace"] if namespace_config else None
            db_access_level = namespace_config["access_level"] if namespace_config else "read"

            sentry_sdk.set_tag("agent-id", request.agent_id)
            log.info(
                f"RunAgent: invoking agent_id={request.agent_id} "
                f"scope_key={request.scope_key} run_id={request.run_id} "
                f"trigger={request.handler_name}"
            )

            from canvas_sdk.agents import RunSubject
            from canvas_sdk.agents.grant import apply_tool_grant, split_granted_effects
            from canvas_sdk.agents.run_record import RunRecorder, current_recorder

            if not AGENT_RUN_SLOTS.acquire(blocking=False):
                log.warning(
                    f"RunAgent: {PLUGIN_RUNNER_MAX_AGENT_RUNS} agent run(s) already in progress; "
                    f"turning away agent_id={request.agent_id} run_id={request.run_id} to retry"
                )
                sentry_sdk.set_tag("agent-id", None)
                yield EventResponse(success=False, effects=[], error_kind="RUNNER_BUSY")
                return

            failure: EventResponse | None = None
            # run_tool_loop records model and tool calls here for home-app's run record.
            recorder = RunRecorder()
            # The tool loop stops making model calls short of home-app's deadline, after
            # which the run's lease can go to the next run of the same scope.
            remaining = context.time_remaining() if context is not None else None
            if remaining is not None:
                recorder.deadline = monotonic() + remaining
            recorder_token = current_recorder.set(recorder)
            try:
                with (
                    plugin_context(f"{module_path}.{class_name}"),
                    plugin_database_context(
                        base_plugin_name,
                        namespace=db_namespace,
                        access_level=db_access_level,
                    ),
                ):
                    agent = agent_class()
                    recorder.max_model_calls = agent.max_model_calls
                    # The manifest's components.agents[].tools grant is what the
                    # agent may do. `allowed` holds tool names and
                    # `@category` references, `denied` is subtracted after
                    # expansion, and an agent whose manifest grants nothing gets
                    # no tools. The agent's registry is swapped for the scoped
                    # view, and the effect types the granted tools declare bound
                    # what the agent may return below.
                    granted_effect_types = apply_tool_grant(
                        agent, (plugin.get("handler") or {}).get("tools") or {}
                    )
                    # home-app validated the subject before enqueuing the run.
                    agent.subject = RunSubject(
                        patient_id=request.patient_id or None,
                        staff_id=request.staff_id or None,
                        note_id=request.note_id or None,
                    )
                    agent.run_id = request.run_id
                    # Lifecycle hooks: on_run_start before
                    # load_state, on_run_end after a successful save_state,
                    # on_run_error if anything in between raises. Hook
                    # failures are swallowed by `_invoke_agent_hook` so a
                    # botched hook can't crash the underlying run.
                    _invoke_agent_hook(agent, "on_run_start", request.scope_key)
                    try:
                        state = agent.load_state(request.scope_key)
                        result = agent.run(state, gateway, trigger_payload)
                        if context is not None and not context.is_active():
                            raise RunDeadlineExceeded(
                                "the RunAgent call ended before run() returned; "
                                "its state and effects are discarded"
                            )
                        agent.save_state(request.scope_key, result.state)
                        _invoke_agent_hook(agent, "on_run_end", result)
                    except Exception as run_exc:
                        _invoke_agent_hook(agent, "on_run_error", run_exc)
                        raise
            except anthropic.APIError as exc:
                # The gateway refused the call or could not complete it. Only an
                # outage is worth retrying: a refusal (budget, model, auth,
                # request shape) would be refused again.
                error_kind = llm_error_kind(exc)
                log.warning(
                    f"RunAgent: agent {request.agent_id} LLM call failed ({error_kind}): {exc}"
                )
                failure = EventResponse(
                    success=False,
                    effects=[],
                    error_kind=error_kind,
                    agent_run=_agent_run_summary(recorder),
                )
            except RunDeadlineExceeded as exc:
                log.warning(
                    f"RunAgent: agent {request.agent_id} run {request.run_id} stopped: {exc}"
                )
                failure = EventResponse(
                    success=False, effects=[], agent_run=_agent_run_summary(recorder)
                )
            except Exception as exc:
                log.exception(f"RunAgent: agent {request.agent_id} raised")
                sentry_sdk.capture_exception(exc)
                failure = EventResponse(
                    success=False, effects=[], agent_run=_agent_run_summary(recorder)
                )
            finally:
                current_recorder.reset(recorder_token)
                # Released before anything is yielded, so the slot frees as soon as
                # the agent finishes rather than when the caller drains the stream.
                AGENT_RUN_SLOTS.release()
                sentry_sdk.set_tag("agent-id", None)

            if failure is not None:
                yield failure
                return

            # Agent effects carry no classname. home-app reads a classname as a CQM
            # protocol identifier: ProtocolCardEffectInterpreter keys a card on
            # `{classname}|{plugin_name}` when one is set, ignoring the effect's own
            # `key`, which would put every card an agent emits for a patient in one row.
            granted_effects, ungranted = split_granted_effects(result.effects, granted_effect_types)
            for effect in ungranted:
                log.warning(
                    f"RunAgent: dropping {EffectType.Name(effect.type)} from agent "
                    f"{request.agent_id}; no tool its manifest grants stages that effect"
                )
            emitted_effects = [
                Effect(
                    type=effect.type,
                    payload=effect.payload,
                    plugin_name=base_plugin_name,
                    # The agent, not the trigger handler that started it, so the
                    # security audit names the agent behind each write.
                    handler_name=class_name,
                    actor=request.actor,
                    source=request.source or "agent",
                )
                for effect in granted_effects
            ]
            emitted_effects = permitted_usage(
                emitted_effects, plugin.get("usage_units", frozenset())
            )
            emitted_effects = validate_effects(emitted_effects)

            log.info(
                f"RunAgent: agent_id={request.agent_id} run_id={request.run_id} "
                f"completed with {len(emitted_effects)} effect(s)"
            )

            yield EventResponse(
                success=True,
                effects=emitted_effects,
                agent_run=_agent_run_summary(
                    recorder,
                    effects_returned=len(result.effects),
                    effects_dropped=len(result.effects) - len(emitted_effects),
                ),
            )

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

    def GetRegisteredEventTypes(
        self, request: GetRegisteredEventTypesRequest, context: Any
    ) -> GetRegisteredEventTypesResponse:
        """Return the event types that have at least one registered handler."""
        snapshot = EVENT_REGISTRY.snapshot()

        return GetRegisteredEventTypesResponse(
            event_types=sorted(snapshot.event_types),
            registry_version=snapshot.version,
            ready=snapshot.ready,
        )


STOP_SYNCHRONIZER = threading.Event()

# HOME-APP-11Y5 / KOALA-5359 — set after the synchronizer has successfully
# psubscribed at least once. Distinguishes startup race (redis DNS not yet
# resolvable on container cold start) from genuine mid-run failure.
SYNCHRONIZER_HAS_CONNECTED = threading.Event()

# Cap on connection-error retries before escalating to Sentry even during
# startup. 60 retries x ~0.5s sleep ≈ 30s grace window — enough for any
# realistic CI cold-start DNS race; short enough that a real misconfiguration
# still surfaces.
STARTUP_RETRY_LIMIT = 60


SYNC_ACTIONS = frozenset({"reload", "unload"})


def parse_sync_message(raw: Any) -> dict[str, str | None] | None:
    """Return the action and plugin a sync message names, or None if it names neither.

    Messages on the sync channel are JSON objects; anything else is ignored rather than
    deserialized.
    """
    try:
        data = json.loads(raw)
    except (TypeError, ValueError):
        return None

    if not isinstance(data, dict) or data.get("action") not in SYNC_ACTIONS:
        return None

    plugin = data.get("plugin")

    if plugin is not None and not isinstance(plugin, str):
        return None

    return {"action": data["action"], "plugin": plugin}


def synchronize_plugins(run_once: bool = False) -> None:
    """
    Listen for messages on the pubsub channel that will indicate it is
    necessary to reinstall and reload plugins.
    """
    log.info(f'synchronize_plugins: listening for messages on pubsub channel "{CHANNEL_NAME}"')

    _, pubsub = get_client()

    pubsub.psubscribe(CHANNEL_NAME)
    SYNCHRONIZER_HAS_CONNECTED.set()

    while not STOP_SYNCHRONIZER.is_set():
        message = pubsub.get_message(ignore_subscribe_messages=True, timeout=5.0)

        if message is None:
            continue

        log.info(f'synchronize_plugins: received message from pubsub channel "{CHANNEL_NAME}"')

        message_type = message.get("type", "")

        if message_type != "pmessage":
            continue

        data = parse_sync_message(message.get("data"))

        if data is None:
            log.warning("synchronize_plugins: ignoring a message that is not a known JSON action")

            if run_once:
                break

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
                        # Install the new package before touching the running handlers, so
                        # the current version keeps serving requests during the slow download
                        # and namespace wait. reload_plugin then swaps it in atomically, so a
                        # reload never leaves the plugin's routes returning 404.
                        install_plugin(plugin_name, attributes=plugin)
                        plugin_dir = pathlib.Path(PLUGIN_DIRECTORY) / plugin_name
                        reload_plugin(plugin_dir.resolve())
                else:
                    log.info("synchronize_plugins: installing/reloading plugins for action=reload")
                    install_plugins()
                    reconcile_plugins()
            elif data["action"] == "unload" and plugin_name:
                log.info(f'synchronize_plugins: uninstalling plugin "{plugin_name}"')
                remove_plugin(plugin_name)
                uninstall_plugin(plugin_name)
        except Exception as e:
            if isinstance(e, PluginInstallationError):
                message = "install_plugins failed"
            elif isinstance(e, PluginUninstallationError):
                message = "uninstall_plugin failed"
            else:
                message = "reconcile_plugins failed"

            if plugin_name:
                message += f' for plugin "{plugin_name}"'

            log.exception(f"synchronize_plugins: {message}")
            sentry_sdk.capture_exception(e)

        if run_once:
            break


def synchronize_plugins_and_report_errors() -> None:
    """
    Run synchronize_plugins() in perpetuity and report any encountered errors.

    HOME-APP-11Y5 / KOALA-5359: connection errors before the synchronizer has
    ever connected are an expected race during container cold start — redis
    DNS is briefly unresolvable while the docker network attaches. Suppress
    them from Sentry until either the synchronizer connects successfully or
    STARTUP_RETRY_LIMIT retries have elapsed. After that, escalate as before.
    """
    log.info("synchronize_plugins: starting loop...")

    startup_retries = 0

    while not STOP_SYNCHRONIZER.is_set():
        try:
            synchronize_plugins()
        except Exception as e:
            in_startup_grace = (
                not SYNCHRONIZER_HAS_CONNECTED.is_set()
                and isinstance(e, ConnectionError)
                and startup_retries < STARTUP_RETRY_LIMIT
            )
            if in_startup_grace:
                startup_retries += 1
                log.warning(
                    "synchronize_plugins: redis not yet reachable "
                    f"(startup retry {startup_retries}/{STARTUP_RETRY_LIMIT})"
                )
            else:
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

    client.publish(CHANNEL_NAME, json.dumps(message))


def get_client() -> tuple[redis.Redis, redis.client.PubSub]:
    """Return a Redis client and pubsub object."""
    client = redis.from_url(
        REDIS_ENDPOINT,
        retry=Retry(backoff=ExponentialBackoff(), retries=10),
        retry_on_error=[ConnectionError, TimeoutError, ConnectionResetError],
        health_check_interval=1,
        socket_keepalive=True,
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
    secret_name = (
        "namespace_read_write_access_key"
        if declared_access == "read_write"
        else "namespace_read_access_key"
    )

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
    from plugin_runner.namespace import check_namespace_auth_key, is_valid_namespace_name

    namespace_name = custom_data["namespace"]
    declared_access = custom_data["access"]

    if not is_valid_namespace_name(namespace_name):
        raise NamespaceAccessError(
            f"Plugin '{plugin_name}' declares {namespace_name!r}, which is not a valid "
            f"namespace name (expected org__name in lowercase letters, digits and underscores)."
        )

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
                f"Use the 'namespace_read_write_access_key' secret for write access."
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


@dataclass
class HandlerLoadResult:
    """Outcome of sandbox-loading a single declared handler.

    Pure data — carries either the executed sandbox ``scope`` (success) or the
    ``error`` that was raised. ``report`` indicates whether the error warrants
    Sentry reporting at runtime (false for developer-fault cases like a handler
    declared from a foreign package). ``sandbox_mode`` is the rule set the handler
    actually loaded under.
    """

    handler: dict[str, Any]
    name_and_class: str | None
    handler_class: str | None
    scope: dict[str, Any] | None
    error: Exception | None
    report: bool
    sandbox_mode: SandboxMode = SandboxMode.STRICT


def _purge_plugin_modules(name: str) -> None:
    """Drop every ``sys.modules`` entry the sandbox published for this plugin.

    A sandbox load registers each plugin module it evaluates. Those entries have to go
    before the plugin is loaded again under a different rule set, or the second pass
    reuses modules built by the first.
    """
    prefix = f"{name}."

    for module_name in [m for m in sys.modules if m == name or m.startswith(prefix)]:
        del sys.modules[module_name]


def sandbox_plugin_handlers(
    name: str,
    path: pathlib.Path,
    handlers: list[dict[str, Any]],
    evaluated_modules: EvaluatedModules | None = None,
) -> list[HandlerLoadResult]:
    """Sandbox-load each declared handler for a plugin.

    Runs the exact sandbox path used at runtime (``sandbox_from_module`` +
    ``execute``) plus the Django model-registration reset, but mutates no global
    plugin state (``LOADED_PLUGINS``) and does no logging or Sentry reporting —
    callers decide what to do with the returned results. Shared by
    ``import_plugin`` and the ``canvas validate`` pre-flight so the two
    cannot drift on sandbox semantics.

    Picks the rule set before loading. Most of the difference between the two is felt at
    request time rather than load time: under the deprecated rules a plugin's imported
    submodules are executed by the real import system and the functions they define carry
    none of the sandbox's guards, so a plugin can load cleanly under the current rules and
    then fail inside a handler. ``find_legacy_constructs`` reads that difference
    statically, and a plugin that depends on it is loaded under
    ``SandboxMode.LEGACY_PERMISSIVE`` rather than left to break in production.

    Only a plugin already on ``sandbox_allowlists`` may load under the deprecated
    rules. One that depends on them without being listed is refused outright, naming each
    construct, so the dependency cannot be newly acquired: the allowlist only shrinks.

    A plugin with no such dependency loads under ``SandboxMode.STRICT``. If it fails there
    and is on the allowlist, the whole plugin is retried under the deprecated rules, and
    those results are kept only when they actually recover a handler. The generator
    finds these plugins by loading them, so the list covers load-time dependencies as
    well as the constructs read statically.

    A plugin on the always list loads under the deprecated rules before any of this: its
    incompatibility only surfaces when its code runs, which neither the static read nor
    the load-time retry can see.

    Either way the deprecated rules are reported to Sentry at fatal level. They will be
    removed, at which point a plugin that depends on them stops working. ``sandbox_mode``
    on each result says which rule set that handler used, so callers can tell developers
    what needs updating.
    """
    if is_always_legacy(CUSTOMER_IDENTIFIER, name):
        results = _load_plugin_handlers(
            name, path, handlers, evaluated_modules, SandboxMode.LEGACY_PERMISSIVE
        )
        _report_legacy_sandbox(name, ["code the current sandbox rules refuse when it runs"], {})

        return results

    entry_modules = {
        handler["class"].split(":")[0]
        for handler in handlers
        if handler.get("class") and ":" in handler["class"]
    }

    try:
        legacy_constructs = find_legacy_constructs(path, entry_modules)
    except OSError:
        legacy_constructs = []

    if legacy_constructs:
        reasons = [str(construct) for construct in legacy_constructs]

        if _on_legacy_allowlist(name):
            results = _load_plugin_handlers(
                name, path, handlers, evaluated_modules, SandboxMode.LEGACY_PERMISSIVE
            )
            _report_legacy_sandbox(name, reasons[:20], {})

            return results

        return _refuse_unlisted_plugin(name, handlers, reasons)

    strict_results = _load_plugin_handlers(
        name, path, handlers, evaluated_modules, SandboxMode.STRICT
    )

    # A handler that failed before the sandbox ran (unparseable "class", foreign
    # package) fails identically under either mode, so it is not worth a retry.
    if not any(
        result.error is not None and result.name_and_class is not None for result in strict_results
    ):
        return strict_results

    if not _on_legacy_allowlist(name):
        return strict_results

    permissive_results = _load_plugin_handlers(
        name, path, handlers, None, SandboxMode.LEGACY_PERMISSIVE
    )

    recovered = sorted(
        {
            strict.name_and_class
            for strict, permissive in zip(strict_results, permissive_results, strict=True)
            if strict.error is not None
            and permissive.error is None
            and strict.name_and_class is not None
        }
    )

    if not recovered:
        # The legacy pass changed nothing, so leave the plugin loaded strictly.
        return _load_plugin_handlers(name, path, handlers, evaluated_modules, SandboxMode.STRICT)

    _report_legacy_sandbox(
        name,
        recovered,
        {
            strict.name_and_class: repr(strict.error)
            for strict in strict_results
            if strict.error is not None
        },
    )

    return permissive_results


def _on_legacy_allowlist(name: str) -> bool:
    """Whether this plugin may load under the deprecated sandbox rules.

    Without a readable allowlist the answer is no, and the plugin is reported against the
    current rules: its own errors, naming what to fix, and nothing else. That is what
    `canvas validate` shows a developer, who has no key.
    """
    try:
        return is_allowlisted(CUSTOMER_IDENTIFIER, name)
    except AllowlistUnavailable:
        return False


def _refuse_unlisted_plugin(
    name: str,
    handlers: list[dict[str, Any]],
    reasons: list[str],
) -> list[HandlerLoadResult]:
    """Refuse a plugin that depends on the deprecated sandbox rules without being listed.

    Nothing is executed. The same constructs would have loaded and then failed part-way
    through a handler at request time, so refusing here trades a broken instance for an
    error the plugin's author can read.
    """
    detail = "\n".join(f"  {reason}" for reason in reasons)
    error = PluginInstallationError(
        f'Plugin "{name}" uses constructs that are not permitted under the current '
        f"sandbox rules:\n{detail}"
    )

    log.error(str(error))

    return [
        HandlerLoadResult(
            handler,
            f"{name}:{handler['class']}" if handler.get("class") else None,
            (handler.get("class") or ":").split(":")[-1] or None,
            None,
            error,
            report=False,
        )
        for handler in handlers
    ]


def _report_legacy_sandbox(name: str, reasons: list[str], errors: dict[str | None, str]) -> None:
    """Record that a plugin was loaded under the deprecated sandbox rules."""
    log.critical(
        f'Plugin "{name}" loaded under the deprecated sandbox rules, which will be '
        f"removed in a future release; needs updating: {', '.join(reasons)}"
    )

    with sentry_sdk.new_scope() as scope:
        scope.set_tag("plugin-name", name)
        scope.set_tag("sandbox-mode", SandboxMode.LEGACY_PERMISSIVE.value)
        scope.set_context(
            "sandbox_fallback",
            {"plugin": name, "reasons": reasons, "errors": errors},
        )
        sentry_sdk.capture_message(
            f'Plugin "{name}" depends on the deprecated sandbox rules and was loaded '
            "under them; it will stop working when those are removed",
            level="fatal",
        )


def _load_plugin_handlers(
    name: str,
    path: pathlib.Path,
    handlers: list[dict[str, Any]],
    evaluated_modules: EvaluatedModules | None,
    mode: SandboxMode,
) -> list[HandlerLoadResult]:
    """Sandbox-load every declared handler for a plugin under one set of sandbox rules."""
    # The deprecated rules resolve a plugin's submodules through the real import system,
    # which needs the package's parent importable. The runner puts PLUGIN_DIRECTORY on
    # the path when it loads plugins; doing it here too means any caller gets the same
    # behavior without having to know that.
    parent_directory = str(path.parent)

    if parent_directory not in sys.path:
        sys.path.insert(0, parent_directory)

    # Start from a clean module state. Modules published by an earlier load of this
    # plugin are built for whichever rule set was in force then, so reusing them across
    # a reload — or across the retry below — resolves imports against the wrong ones.
    _purge_plugin_modules(name)

    if evaluated_modules is None:
        # Share evaluated_modules across all handlers in this plugin so that
        # common submodules (like constants.py) are only evaluated and reloaded
        # once, not once per handler.
        evaluated_modules = {}

    # Clear stale model registrations before handler sandboxes re-execute model
    # files.  Without this, lazy_related_operation resolves string references
    # (e.g. through="StaffSpecialty") to class objects from the prior execution,
    # causing model-identity mismatches in ManyToManyField through-model resolution.
    django_apps.all_models.pop(name, None)
    django_apps.app_configs.pop(name, None)
    django_apps.clear_cache()

    results: list[HandlerLoadResult] = []

    # A plugin may declare many handlers from one module. Executing that module
    # once per handler recompiles and re-runs the same file N times, which
    # dominates load time for handler-dense plugins. Key the outcome — scope or
    # the exception it raised — on the module so each file costs one execution
    # and every handler in it still gets its own result.
    module_outcomes: dict[str, dict[str, Any] | Exception] = {}

    for handler in handlers:
        # TODO add class colon validation to existing schema validation
        try:
            handler_module, handler_class = handler["class"].split(":")
        except ValueError as e:
            results.append(HandlerLoadResult(handler, None, None, None, e, report=True))
            continue

        handler_package = handler_module.split(".")[0]
        if handler_package != name:
            results.append(
                HandlerLoadResult(
                    handler,
                    None,
                    handler_class,
                    None,
                    ValueError(
                        f'Plugin "{name}" declares handler from foreign package "{handler_package}"'
                    ),
                    report=False,
                )
            )
            continue

        name_and_class = f"{name}:{handler_module}:{handler_class}"

        if handler_module not in module_outcomes:
            try:
                # Suppress Django's "Model was already registered" RuntimeWarning.
                # When importlib.reload re-imports model modules, Django's metaclass
                # calls apps.register_model() again for each model class.
                with warnings.catch_warnings():
                    warnings.filterwarnings(
                        "ignore",
                        message=r"Model '.*' was already registered",
                        category=RuntimeWarning,
                    )
                    sandbox = sandbox_from_module(
                        path.parent, handler_module, evaluated_modules, mode
                    )
                    module_outcomes[handler_module] = sandbox.execute()
            except Exception as e:
                module_outcomes[handler_module] = e

        outcome = module_outcomes[handler_module]

        if isinstance(outcome, Exception):
            results.append(
                HandlerLoadResult(
                    handler,
                    name_and_class,
                    handler_class,
                    None,
                    outcome,
                    report=True,
                    sandbox_mode=mode,
                )
            )
            continue

        results.append(
            HandlerLoadResult(
                handler,
                name_and_class,
                handler_class,
                outcome,
                None,
                report=False,
                sandbox_mode=mode,
            )
        )

    # Re-register the AppConfig so that the freshly-created model classes are
    # visible to Django's relation graph (needed for select_related, etc.).
    register_plugin_app_config(name)

    return results


def import_plugin(path: pathlib.Path) -> bool:
    """Import a plugin's handlers into LOADED_PLUGINS, returning True if all loaded.

    Leaves EVENT_HANDLER_MAP untouched, so a caller must follow with
    rebuild_event_routes() before the plugin's routes reflect this import.
    """
    log.info(f'Loading plugin at "{path}"')

    # the name is the folder name underneath the plugins directory
    name = path.name

    with metrics.measure(
        "import_plugin",
        track_memory_usage=True,
        extra_tags={"plugin": name},
    ):
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
            if IS_SQLITE:
                # Local development mode: skip namespace auth verification and
                # schema creation (no PostgreSQL, no secrets, no namespace_auth table).
                namespace_name = custom_data["namespace"]
                namespace_config = {
                    "namespace": namespace_name,
                    "access_level": custom_data.get("access", "read"),
                }
                log.info(
                    f"Plugin '{name}' granted local '{namespace_config['access_level']}' "
                    f"access to namespace '{namespace_name}' (SQLite mode, auth skipped)"
                )

                # The default SQLite connection is read-only; swap to the writable
                # one for schema initialisation and plugin migrations.
                import django.db

                original_default = django.db.connections["default"]
                try:
                    temp_handler = django.db.utils.ConnectionHandler(
                        {"default": settings.SQLITE_WRITE_MODE_DATABASE}
                    )
                    django.db.connections["default"] = temp_handler["default"]

                    # Ensure the framework tables exist (custom_attribute,
                    # attribute_hub) — same as the test database setup and the
                    # --reset-db path in run_plugins.
                    _ensure_sqlite_schema()

                    # install_plugins() is skipped in local mode, so custom data
                    # tables are never created. Run plugin-specific migrations here.
                    if namespace_config["access_level"] == "read_write":
                        generate_plugin_migrations(name, path, schema_name=namespace_name)
                finally:
                    django.db.connections["default"] = original_default
            else:
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
                + cast(list, components.get("agents", []))
            )
        except Exception as e:
            log.exception(f'Unable to load plugin "{name}"')
            sentry_sdk.capture_exception(e)

            return False

        # TODO when we encounter an exception here, disable the plugin in response
        results = sandbox_plugin_handlers(name, path, handlers)
        units = usage_units(manifest_json)

        any_failed = False
        loaded_handler_count = 0

        for r in results:
            if r.error is not None:
                any_failed = True
                if not r.report:
                    log.error(f"{r.error} — skipping")
                elif r.name_and_class is None:
                    log.error(
                        f'Unable to parse class for plugin "{name}": "{r.handler["class"]}"',
                        exc_info=r.error,
                    )
                    sentry_sdk.capture_exception(r.error)
                else:
                    log.error(f"Error importing module '{r.name_and_class}'", exc_info=r.error)
                    sentry_sdk.capture_exception(r.error)
                continue

            name_and_class = cast(str, r.name_and_class)
            handler_class = cast(str, r.handler_class)
            result = cast(dict, r.scope)

            if name_and_class in LOADED_PLUGINS:
                log.info(f"Reloading handler '{name_and_class}'")

                LOADED_PLUGINS[name_and_class]["active"] = True

                LOADED_PLUGINS[name_and_class]["class"] = result[handler_class]
                LOADED_PLUGINS[name_and_class]["sandbox"] = result
                # The manifest entry carries an agent's tool grant, which an update can narrow.
                LOADED_PLUGINS[name_and_class]["handler"] = r.handler
                LOADED_PLUGINS[name_and_class]["secrets"] = secrets_json
                LOADED_PLUGINS[name_and_class]["namespace_config"] = namespace_config
                LOADED_PLUGINS[name_and_class]["usage_units"] = units
            else:
                log.info(f'Loading handler "{name_and_class}"')

                LOADED_PLUGINS[name_and_class] = {
                    "active": True,
                    "class": result[handler_class],
                    "sandbox": result,
                    "handler": r.handler,
                    "secrets": secrets_json,
                    "namespace_config": namespace_config,
                    "usage_units": units,
                }

            loaded_handler_count += 1

        plugin_version = manifest_json.get("plugin_version", "unknown")
        total_handlers = len(handlers)
        if any_failed:
            log.warning(
                f'Plugin "{name}" version {plugin_version} loaded with errors '
                f"({loaded_handler_count}/{total_handlers} handlers loaded successfully)"
            )
        else:
            log.info(
                f'Successfully loaded plugin "{name}", version {plugin_version} '
                f"({loaded_handler_count}/{total_handlers} handlers loaded)"
            )

        return not any_failed


def remove_plugin(name: str) -> None:
    """Tear a plugin down by name: drop its handlers and rebuild its routes.

    This is the disable/uninstall path. A version swap goes through
    reload_plugin, which keeps the plugin's routes served throughout.
    """
    handlers_removed = False

    for handler_name in LOADED_PLUGINS.copy():
        if handler_name.startswith(f"{name}:"):
            log.info(f'Unloading handler "{handler_name}"')
            del LOADED_PLUGINS[handler_name]
            handlers_removed = True

    # Remove stale sys.modules entries for this plugin's package so that subsequent
    # loads do a clean import instead of calling importlib.reload on stale module
    # objects (which can leave modules in a partially-initialized state).
    stale_modules = [mod for mod in sys.modules if mod == name or mod.startswith(f"{name}.")]
    for mod in stale_modules:
        del sys.modules[mod]

    if handlers_removed:
        # Refresh the event type map to remove any handlers for the unloaded plugin
        rebuild_event_routes()
    else:
        log.warning(f"No handlers found for plugin '{name}' to unload.")


def rebuild_event_routes() -> None:
    """Ensure the event subscriptions are up to date, then republish the event registry."""
    with EVENT_REGISTRY.rebuilding(EVENT_HANDLER_MAP):
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
def reconcile_plugins(specified_plugin_paths: list[str] | None = None) -> None:
    """Reconcile LOADED_PLUGINS against what is on disk, then rebuild the routes.

    Disk is the source of truth: plugins present are imported, and plugins that
    have gone are dropped. This is the only path that removes in bulk.
    """
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
            import_plugin(plugin_path)
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

    rebuild_event_routes()


@measured
def reload_plugin(path: pathlib.Path) -> None:
    """Load a single plugin in place, keeping its routes served throughout.

    The plugin's currently-loaded handlers stay registered and keep serving while
    the new version imports; the event map is rebuilt once, after the swap. If the
    new version fails to load, the previous one stays active.
    """
    # Derive the name the same way import_plugin does, so the handler-key
    # prefix always matches the keys that a load populates.
    name = path.name
    prefix = f"{name}:"

    # Mark the plugin's current handlers inactive but leave them registered, so
    # they keep serving while the new version imports.
    for handler_name, plugin in LOADED_PLUGINS.items():
        if handler_name.startswith(prefix):
            plugin["active"] = False

    # Drop stale module objects so the import picks up the new code instead of
    # reusing the already-imported (old) modules.
    stale_modules = [mod for mod in sys.modules if mod == name or mod.startswith(f"{name}.")]
    for mod in stale_modules:
        del sys.modules[mod]

    try:
        loaded = import_plugin(path)
    except NamespaceAccessError as e:
        loaded = False
        log.error(f"Namespace access error loading plugin from '{path}': {e}")
        sentry_sdk.capture_exception(e)
    except Exception as e:
        loaded = False
        log.exception(f"Unexpected error loading plugin from '{path}'")
        sentry_sdk.capture_exception(e)

    if loaded:
        # Remove handlers that existed in the previous version but are gone from
        # the new one.
        for handler_name, plugin in LOADED_PLUGINS.copy().items():
            if handler_name.startswith(prefix) and not plugin["active"]:
                del LOADED_PLUGINS[handler_name]
    else:
        # Keep the previous handlers live rather than dropping their routes.
        for handler_name, plugin in LOADED_PLUGINS.items():
            if handler_name.startswith(prefix):
                plugin["active"] = True

    # Rebuild the event map once, whichever branch ran. A partial load has already
    # swapped new handler classes into LOADED_PLUGINS, so the map has to reflect
    # them even when import_plugin reports failure.
    rebuild_event_routes()


# NOTE: specified_plugin_paths powers the `canvas run-plugins` command
def main(specified_plugin_paths: list[str] | None = None) -> None:
    """Run the server and the synchronize_plugins loop."""
    port = "50051"

    # A stamp left by a previous runner process describes routes this process has
    # not loaded yet, so home-app sends every event until the first rebuild.
    EVENT_REGISTRY.mark_not_ready()

    # Agent runs get their own threads, so a full set of agent runs leaves every worker to events.
    executor = ThreadPoolExecutor(
        max_workers=settings.PLUGIN_RUNNER_MAX_WORKERS + settings.PLUGIN_RUNNER_MAX_AGENT_RUNS
    )
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

    reconcile_plugins(specified_plugin_paths)

    server.start()

    shutdown_reason = "unknown"

    def handle_signal(signum: int, _frame: object) -> None:
        nonlocal shutdown_reason
        shutdown_reason = signal.Signals(signum).name
        server.stop(grace=0)

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        shutdown_reason = "SIGINT"
    except Exception as ex:
        shutdown_reason = f"exception: {ex}"
    finally:
        log.info(f"Server shutting down (reason: {shutdown_reason})")
        EVENT_REGISTRY.mark_not_ready()
        executor.shutdown(wait=True, cancel_futures=True)
        if synchronizer_thread.is_alive():
            STOP_SYNCHRONIZER.set()
            synchronizer_thread.join()
        log.info("Server stopped")


if __name__ == "__main__":
    main()
