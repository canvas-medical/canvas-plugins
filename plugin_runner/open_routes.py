"""Find plugin API handlers whose ``authenticate`` admits every caller.

Canvas forwards every request under ``/plugin-io/api/<plugin>/`` to the plugin and lets the
handler class's ``authenticate`` decide. The SDK default refuses, so a route is open only when
a plugin overrides ``authenticate`` with something that cannot fail:

  * ``return True``
  * ``return self.event.actor is not None``: the SDK always attaches an ``Actor``, even to an
    anonymous request
  * a check that a credential merely exists (``return bool(credentials.token)``), which any
    ``Authorization: Bearer x`` value passes

Both ``canvas validate`` (``canvas_cli/apps/plugin/plugin_lint.py``) and the plugin runner's
load path call :func:`open_routes_in_module`, so the developer-side error and the server-side
report cannot disagree. This module uses only the standard library so the runner can import it
without the CLI.

A handler that is public on purpose (a booking page, an intake form, a webhook that verifies a
signature inside the handler) sets ``PUBLIC_ACCESS = True`` on the class.
"""

from __future__ import annotations

import ast
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

PUBLIC_ACCESS = "PUBLIC_ACCESS"

_ROUTE_BASES = {"SimpleAPI", "SimpleAPIRoute"}
_WEBSOCKET_BASES = {"WebSocketAPI"}
_REQUEST_READS = {"headers", "query_params", "path_params", "json", "form_data", "body", "text"}
_CREDENTIAL_FIELDS = {"token", "key", "username", "password"}

# Directories that never hold plugin source the runner loads.
_SKIP_DIRS = {
    "__pycache__",
    "tests",
    ".venv",
    "node_modules",
    "site-packages",
    "build",
    "dist",
}


@dataclass(frozen=True)
class OpenRoute:
    """A handler class whose ``authenticate`` admits every caller."""

    class_name: str
    line: int
    kind: str  # "always-true", "actor-exists" or "credential-exists"
    route: str | None  # the first method that reads request input or Canvas data

    def describe(self) -> str:
        """Say why ``authenticate`` admits everyone, in one clause."""
        why = {
            "always-true": "always returns True",
            "actor-exists": (
                "only checks `self.event.actor is not None`, which is true for every request"
            ),
            "credential-exists": (
                "only checks that a credential is present, so any `Authorization` value passes"
            ),
        }[self.kind]

        return f"`{self.class_name}.authenticate` {why}"


def _base_names(node: ast.ClassDef) -> set[str]:
    names: set[str] = set()

    for base in node.bases:
        if isinstance(base, ast.Name):
            names.add(base.id)
        elif isinstance(base, ast.Attribute):
            names.add(base.attr)

    return names


def _is_self_attr(node: ast.expr, *chain: str) -> bool:
    """Whether ``node`` is ``self.<chain[0]>.<chain[1]>...``."""
    for attr in reversed(chain):
        if not isinstance(node, ast.Attribute) or node.attr != attr:
            return False
        node = node.value

    return isinstance(node, ast.Name) and node.id == "self"


def _is_credential(node: ast.expr) -> bool:
    """``credentials`` or ``credentials.<field>``."""
    if isinstance(node, ast.Name):
        return node.id == "credentials"

    return (
        isinstance(node, ast.Attribute)
        and node.attr in _CREDENTIAL_FIELDS
        and isinstance(node.value, ast.Name)
        and node.value.id == "credentials"
    )


def _admits(node: ast.expr) -> str | None:
    """Return the kind of check ``node`` is if every caller passes it, else None."""
    if isinstance(node, ast.Constant) and node.value is True:
        return "always-true"

    # bool(x) and len(x) > 0 are the same test as x
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "bool"
        and len(node.args) == 1
    ):
        return _admits(node.args[0])

    if _is_self_attr(node, "event", "actor"):
        return "actor-exists"

    if _is_credential(node):
        return "credential-exists"

    if isinstance(node, ast.Compare) and len(node.ops) == 1:
        left, op, right = node.left, node.ops[0], node.comparators[0]
        is_none = isinstance(right, ast.Constant) and right.value is None
        is_empty = isinstance(right, ast.Constant) and right.value in ("", 0)

        if (isinstance(op, ast.IsNot) and is_none) or (isinstance(op, ast.NotEq) and is_empty):
            return _admits(left)

    if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And):
        kinds = [_admits(value) for value in node.values]

        if all(kinds):
            return next((k for k in kinds if k != "always-true"), "always-true")

    return None


def _authenticate_admits(function: ast.FunctionDef | ast.AsyncFunctionDef) -> str | None:
    """Return the kind of check if ``authenticate`` lets every caller in, else None.

    Looks at the first statement past a docstring and any bare calls (logging), so a body that
    starts with ``return True`` counts even when dead code follows it.
    """
    for statement in function.body:
        if isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Constant | ast.Call):
            continue

        if isinstance(statement, ast.Return) and statement.value is not None:
            return _admits(statement.value)

        return None

    return None


def _declares_public_access(cls: ast.ClassDef) -> bool:
    return any(
        isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == PUBLIC_ACCESS for t in node.targets)
        and isinstance(node.value, ast.Constant)
        and node.value.value is True
        for node in cls.body
    )


def _reads_request(node: ast.AST) -> bool:
    return any(
        isinstance(n, ast.Attribute)
        and n.attr in _REQUEST_READS
        and _is_self_attr(n.value, "request")
        for n in ast.walk(node)
    )


def _reads_data(node: ast.AST, helpers: dict[str, ast.FunctionDef], follow: bool = True) -> bool:
    """Whether ``node`` queries Canvas data (``.objects``, ``for_patient``), directly or through
    one module-level helper in the same file.
    """
    for n in ast.walk(node):
        if isinstance(n, ast.Attribute) and n.attr in ("objects", "for_patient"):
            return True

        if (
            follow
            and isinstance(n, ast.Call)
            and isinstance(n.func, ast.Name)
            and n.func.id in helpers
            and _reads_data(helpers[n.func.id], helpers, follow=False)
        ):
            return True

    return False


def open_routes_in_module(tree: ast.Module) -> list[OpenRoute]:
    """Return every handler class in ``tree`` that admits all callers to a route that matters.

    A ``SimpleAPI``/``SimpleAPIRoute`` class counts when one of its methods reads request input
    or Canvas data; a route that serves only a fixed asset is left alone. A ``WebSocketAPI``
    class always counts, since its channel is the data.
    """
    helpers = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    found: list[OpenRoute] = []

    for cls in ast.walk(tree):
        if not isinstance(cls, ast.ClassDef) or _declares_public_access(cls):
            continue

        bases = _base_names(cls)
        is_route = bool(_ROUTE_BASES & bases)
        is_websocket = bool(_WEBSOCKET_BASES & bases)

        if not is_route and not is_websocket:
            continue

        methods = [n for n in cls.body if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef)]
        authenticate = next((m for m in methods if m.name == "authenticate"), None)
        kind = _authenticate_admits(authenticate) if authenticate else None

        if authenticate is None or kind is None:
            continue

        route = next(
            (
                m.name
                for m in methods
                if m is not authenticate and (_reads_request(m) or _reads_data(m, helpers))
            ),
            None,
        )

        if is_route and route is None:
            continue

        found.append(OpenRoute(cls.name, authenticate.lineno, kind, route))

    return found


def _iter_plugin_modules(root: Path) -> Iterator[tuple[Path, ast.Module]]:
    for py_file in sorted(root.rglob("*.py")):
        rel_parts = py_file.relative_to(root).parts

        if set(rel_parts) & _SKIP_DIRS or any(p.startswith(".") for p in rel_parts[:-1]):
            continue

        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        except (OSError, SyntaxError, ValueError):
            continue

        yield py_file.relative_to(root), tree


def find_open_routes(root: Path) -> list[tuple[Path, OpenRoute]]:
    """Return ``(path relative to root, OpenRoute)`` for every open handler in a plugin."""
    return [
        (rel, route)
        for rel, tree in _iter_plugin_modules(root)
        for route in open_routes_in_module(tree)
    ]
