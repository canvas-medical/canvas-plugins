"""Sandbox-load a plugin's declared handlers.

The plugin runner loads installed plugins through this module, and `canvas validate` and
`canvas deploy` load a plugin under development through it, so the two apply the same
sandbox rules. It imports none of the runner's server packages, so it runs on a base
`canvas` install.
"""

import pathlib
import sys
import warnings
from dataclasses import dataclass
from typing import Any

from django.apps import apps as django_apps

from canvas_sdk.utils import reporting
from logger import log
from plugin_runner.exceptions import PluginInstallationError
from plugin_runner.installation import register_plugin_app_config
from plugin_runner.sandbox import EvaluatedModules, SandboxMode, sandbox_from_module
from plugin_runner.sandbox_allowlists import (
    AllowlistUnavailable,
    is_allowlisted,
    is_always_legacy,
)
from plugin_runner.sandbox_compatibility import find_legacy_constructs
from settings import CUSTOMER_IDENTIFIER


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

    reporting.capture_message(
        f'Plugin "{name}" depends on the deprecated sandbox rules and was loaded '
        "under them; it will stop working when those are removed",
        level="fatal",
        tags={"plugin-name": name, "sandbox-mode": SandboxMode.LEGACY_PERMISSIVE.value},
        context={"sandbox_fallback": {"plugin": name, "reasons": reasons, "errors": errors}},
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
