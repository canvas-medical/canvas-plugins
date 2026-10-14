"""Find plugin code whose behavior depends on which sandbox rule set is in force.

Under `SandboxMode.LEGACY_PERMISSIVE` a plugin's imported submodules are executed by the
real import system, so the functions they define carry none of the sandbox's guards.
Under `SandboxMode.STRICT` those same modules are sandbox-compiled and their function
bodies are guarded like any other plugin code. A plugin can therefore load cleanly under
strict and then fail inside a handler at request time, which no load-time check can see.

This module reads the difference statically so the plugin runner can decide the rule set
before running anything, instead of discovering it in production.

Only function bodies in non-entry modules are reported. A construct at a submodule's top
level runs during the sandboxed evaluation under both rule sets, and a declared handler
module is sandbox-compiled under both, so neither changes behavior between them.
"""

from __future__ import annotations

import ast
import importlib.util
import string
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from plugin_runner.sandbox import ALLOWED_MODULES, RESTRICTED_METHOD_NAMES
from plugin_runner.sandbox_allowlists import is_blessed_import

# Attribute names the sandbox's `_safe_getattr` refuses. `__dict__` is only wrapped off
# plugin-owned code and `raw` only on a manager, but the receiver's type is not knowable
# here — reporting them is the safe direction, since the cost of a false report is a
# plugin kept on the previous rules rather than a plugin that breaks.
#
# `format` is not here: the sandbox supplies a formatter that substitutes normally and
# only refuses to traverse into its arguments, so ordinary formatting behaves the same
# under both rule sets. `_traverses` finds the form that does not.
GUARDED_ATTRIBUTES = frozenset({"__dict__", "raw"}) | RESTRICTED_METHOD_NAMES


@dataclass(frozen=True)
class LegacyConstruct:
    """One place a plugin depends on the previous sandbox rules."""

    module: str
    line: int
    construct: str

    def __str__(self) -> str:
        """Render as a location a plugin author can act on."""
        return f"{self.module}:{self.line} {self.construct}"


def _deferred_nodes(tree: ast.Module) -> set[int]:
    """Return the ids of nodes that sit inside a function body."""
    deferred: set[int] = set()

    def walk(node: ast.AST, inside: bool) -> None:
        for child in ast.iter_child_nodes(node):
            child_inside = inside or isinstance(
                node, ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda
            )

            if child_inside:
                deferred.add(id(child))

            walk(child, child_inside)

    walk(tree, False)

    return deferred


def _traverses(node: ast.Attribute) -> bool:
    """Whether a `.format` call walks into its arguments from inside the format string.

    `"{0.__class__.__init__.__globals__}".format(x)` reaches through the value without
    passing the sandbox's attribute guard, so the sandbox's formatter refuses it while
    the real one allows it. Only a literal template can be read here; a template built
    at runtime is rare and is also the deliberate form.
    """
    if node.attr not in ("format", "format_map"):
        return False

    if not (isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)):
        return False

    try:
        fields = [field for _, field, _, _ in string.Formatter().parse(node.value.value)]
    except ValueError:
        return False

    return any(field and ("." in field or "[" in field) for field in fields)


@cache
def _is_importable(module: str) -> bool:
    """Whether the runtime can resolve this module at all.

    A module that is not installed fails under both rule sets, so it is not a difference
    between them and forcing a plugin onto the previous rules for it would be wrong. The
    question is asked of the environment the plugin runs in, which is why a sibling
    plugin counts: the plugin directory is on the path there.
    """
    try:
        return importlib.util.find_spec(module) is not None
    except (ImportError, AttributeError, ValueError):
        return False


def _imported_names(node: ast.Import | ast.ImportFrom) -> list[str]:
    """Return the module names an import statement resolves."""
    if isinstance(node, ast.ImportFrom):
        # A relative import always names plugin-owned code.
        return [] if node.level else [node.module or ""]

    return [alias.name for alias in node.names]


def _module_bindings(tree: ast.Module) -> dict[str, str]:
    """Local names bound to outside modules by the imports anywhere in a module.

    `import a.b` binds `a`, `import a.b as x` binds `x` to `a.b`, and `from a import b`
    binds `b` to `a.b` when that is an allowlisted module rather than a name in one.
    """
    bindings: dict[str, str] = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname:
                    bindings[alias.asname] = alias.name
                else:
                    root = alias.name.split(".")[0]
                    bindings[root] = root
        elif isinstance(node, ast.ImportFrom) and not node.level and node.module:
            for alias in node.names:
                submodule = f"{node.module}.{alias.name}"

                if submodule in ALLOWED_MODULES:
                    bindings[alias.asname or alias.name] = submodule

    return bindings


def _module_read(node: ast.Attribute, bindings: dict[str, str]) -> str | None:
    """The module an attribute read is taken from, when the receiver names one."""
    parts: list[str] = []
    receiver: ast.expr = node.value

    while isinstance(receiver, ast.Attribute):
        parts.append(receiver.attr)
        receiver = receiver.value

    if not isinstance(receiver, ast.Name) or receiver.id not in bindings:
        return None

    return ".".join([bindings[receiver.id], *reversed(parts)])


def _granted(module: str, name: str) -> bool:
    """Whether the allowlist lets plugin code reach `name` on `module`."""
    return name in ALLOWED_MODULES.get(module, ()) or f"{module}.{name}" in ALLOWED_MODULES


def _scan_module(
    source: str, module: str, package: str, owned: frozenset[str]
) -> list[LegacyConstruct]:
    """Report constructs in one module whose behavior differs between the rule sets."""
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError):
        # Unparseable code fails to compile under either rule set; the load reports it.
        return []

    deferred = _deferred_nodes(tree)
    bindings = _module_bindings(tree)
    found: list[LegacyConstruct] = []

    for node in ast.walk(tree):
        if id(node) not in deferred:
            continue

        if isinstance(node, ast.Import | ast.ImportFrom):
            for name in _imported_names(node):
                root = name.split(".")[0]

                if not root or root in owned or name in ALLOWED_MODULES:
                    continue

                # A module this plugin is named as permitted to import resolves the same
                # way under both rule sets, so it is not a reason to fall back.
                if is_blessed_import(package, name):
                    continue

                # A module nothing can import fails the same way under both rule sets.
                if not _is_importable(name):
                    continue

                found.append(LegacyConstruct(module, node.lineno, f"import {name}"))

            # `from allowed import name`: the module is permitted, but strict code may only
            # take the names its entry grants. Run natively, any name resolves.
            from_module = (
                node.module if isinstance(node, ast.ImportFrom) and not node.level else None
            )

            if (
                from_module is not None
                and from_module in ALLOWED_MODULES
                and not is_blessed_import(package, from_module)
            ):
                for alias in node.names:
                    if alias.name != "*" and not _granted(from_module, alias.name):
                        found.append(
                            LegacyConstruct(
                                module, node.lineno, f"from {from_module} import {alias.name}"
                            )
                        )

        elif isinstance(node, ast.Attribute):
            source_module = _module_read(node, bindings)

            if node.attr in GUARDED_ATTRIBUTES:
                found.append(LegacyConstruct(module, node.lineno, f".{node.attr}"))
            elif _traverses(node):
                found.append(LegacyConstruct(module, node.lineno, f".{node.attr} traversal"))
            elif (
                # Reading a name off an outside module: strict code may only take the
                # names its allowlist entry grants. Run natively, any name resolves.
                source_module is not None
                and isinstance(node.ctx, ast.Load)
                and source_module in ALLOWED_MODULES
                and source_module.split(".")[0] not in owned
                and not node.attr.startswith("_")
                and not _granted(source_module, node.attr)
                and not is_blessed_import(package, source_module)
            ):
                found.append(LegacyConstruct(module, node.lineno, f"{source_module}.{node.attr}"))

        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "vars"
        ):
            found.append(LegacyConstruct(module, node.lineno, "vars()"))

    return found


def _module_path(plugin_dir: Path, module: str) -> Path | None:
    """Resolve a plugin module name to the file the runner would evaluate."""
    relative = module.split(".")[1:]

    if not relative:
        candidate = plugin_dir / "__init__.py"

        return candidate if candidate.exists() else None

    for candidate in (
        plugin_dir.joinpath(*relative).with_suffix(".py"),
        plugin_dir.joinpath(*relative, "__init__.py"),
    ):
        if candidate.exists():
            return candidate

    return None


def _absolute(module: str, node: ast.ImportFrom) -> str | None:
    """Resolve a relative import to an absolute module name, as the sandbox does."""
    package = module.rpartition(".")[0] if not module.endswith(".__init__") else module
    parts = package.split(".") if package else []

    if node.level > 1:
        parts = parts[: -(node.level - 1)]

    if not parts:
        return None

    return ".".join([*parts, node.module]) if node.module else ".".join(parts)


def _reachable_modules(plugin_dir: Path, entry_modules: set[str]) -> set[str]:
    """Return the plugin modules the runner evaluates when it loads the plugin.

    Only modules an entry module imports, directly or transitively, are ever compiled,
    along with the `__init__.py` of every package along the way. Anything else in the
    directory — tests, tooling, dead code — is never executed and so cannot change
    behavior between the rule sets.
    """
    package = plugin_dir.name
    seen: set[str] = set()
    queue = list(entry_modules)

    while queue:
        module = queue.pop()

        if module in seen or not module.startswith(f"{package}."):
            continue

        seen.add(module)

        # The runner evaluates each ancestor package's __init__.py on the way in.
        parts = module.split(".")
        queue.extend(".".join(parts[:depth]) for depth in range(2, len(parts)))

        path = _module_path(plugin_dir, module)

        if path is None:
            continue

        try:
            tree = ast.parse(path.read_text())
        except (OSError, SyntaxError, ValueError):
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                queue.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                target = _absolute(module, node) if node.level else node.module

                if not target:
                    continue

                queue.append(target)
                # `from pkg import sub` names a submodule when one exists on disk.
                queue.extend(f"{target}.{alias.name}" for alias in node.names)

    return {module for module in seen if _module_path(plugin_dir, module) is not None}


def find_legacy_constructs(
    plugin_dir: Path,
    entry_modules: set[str],
) -> list[LegacyConstruct]:
    """Report every place a plugin's submodules depend on the previous sandbox rules.

    An empty result means the strict rules cannot change how this plugin behaves at
    request time, so it is safe to load strictly.
    """
    package = plugin_dir.name
    owned = frozenset(
        {package}
        | {child.name for child in plugin_dir.iterdir() if child.is_dir()}
        | {child.stem for child in plugin_dir.glob("*.py")}
    )

    found: list[LegacyConstruct] = []

    for module in sorted(_reachable_modules(plugin_dir, entry_modules)):
        if module in entry_modules:
            continue

        source_path = _module_path(plugin_dir, module)

        if source_path is None:
            continue

        try:
            source = source_path.read_text()
        except OSError:
            continue

        found.extend(_scan_module(source, module, package, owned))

    return found
