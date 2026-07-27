"""Static pre-load lint for ``canvas validate``.

AST-scans a plugin's source for two classes of problem the sandbox handler-load
can't surface on its own:

  * RestrictedPython constructs that fail at *runtime* inside a method body
    (``compile_restricted`` accepts them, so they load clean and only blow up
    when the line executes on the instance).
  * Custom Data setup mistakes the runner silently tolerates at load but that
    leave tables uncreated or relations dropped.

The runner's sandbox (``plugin_runner/sandbox.py``) and model loader
(``plugin_runner/ddl.py``) are the source of truth; every rule here is pinned to
observed sandbox/loader behavior by a tripwire test in ``test_plugin_lint.py`` so
the lint can't drift the way a hand-maintained allowlist mirror would.
"""

from __future__ import annotations

import ast
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

# Directories that never hold plugin source we should lint — build scratch,
# virtualenvs, caches, tests, VCS.
SKIP_DIRS = {
    "__pycache__",
    "tests",
    ".venv",
    ".cache",
    ".canvas",
    ".npm",
    ".git",
    "node_modules",
    "site-packages",
    ".pytest_cache",
    ".mypy_cache",
    ".uv",
    "build",
    "dist",
}


@dataclass
class LintFinding:
    """A single lint result. ``severity`` is ``"error"`` (blocks the install —
    the runner will reject or silently misbehave) or ``"warning"`` (very likely
    a bug, but not guaranteed to break).
    """

    severity: str
    location: str
    code: str
    message: str


def _iter_python_files(root: Path) -> Iterator[tuple[Path, ast.Module]]:
    """Yield ``(path, parsed_ast)`` for every lintable .py file under ``root``."""
    if not root.is_dir():
        return
    for py_file in sorted(root.rglob("*.py")):
        if set(py_file.parts) & SKIP_DIRS:
            continue
        # Skip anything under a dot-directory (e.g. .cache/uv/...).
        if any(part.startswith(".") and part not in (".", "..") for part in py_file.parts[:-1]):
            continue
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        except (OSError, SyntaxError):
            continue
        yield py_file, tree


def _rel(py_file: Path, root: Path) -> Path:
    return py_file.relative_to(root) if py_file.is_relative_to(root) else py_file


def _base_names(node: ast.ClassDef) -> list[str]:
    """Return the simple names of a class's bases (``Foo`` and ``pkg.Foo`` → ``Foo``)."""
    names: list[str] = []
    for base in node.bases:
        if isinstance(base, ast.Name):
            names.append(base.id)
        elif isinstance(base, ast.Attribute):
            names.append(base.attr)
    return names


def _call_name(node: ast.Call) -> str:
    """Return the simple callable name for a call (``foo()`` / ``x.foo()`` → ``foo``)."""
    fn = node.func
    if isinstance(fn, ast.Name):
        return fn.id
    if isinstance(fn, ast.Attribute):
        return fn.attr
    return ""


# ── Construct rules ───────────────────────────────────────────────────────────
# Each construct below was verified to fail in the runner's sandbox
# (see test_plugin_lint.py). @dataclass(frozen=True/slots=True) is intentionally
# NOT flagged: it loads and runs fine in the current sandbox.


def _construct_findings(plugin_dir: Path) -> list[LintFinding]:
    findings: list[LintFinding] = []
    for py_file, tree in _iter_python_files(plugin_dir):
        rel = _rel(py_file, plugin_dir)
        for node in ast.walk(tree):
            if isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Subscript):
                findings.append(
                    LintFinding(
                        "error",
                        f"{rel}:{node.lineno}",
                        "augmented-subscript",
                        "Augmented assignment on a dict item / list item / slice "
                        "(e.g. `d[k] += v`) is rejected by the RestrictedPython "
                        "sandbox. Rewrite as explicit reassignment: `d[k] = d[k] + v`.",
                    )
                )
            elif isinstance(node, ast.Call):
                name = _call_name(node)
                if name == "setattr" and isinstance(node.func, ast.Name):
                    findings.append(
                        LintFinding(
                            "error",
                            f"{rel}:{node.lineno}",
                            "setattr-blocked",
                            "`setattr()` is blocked by the sandbox. Use direct "
                            "attribute assignment (`obj.attr = value`) instead.",
                        )
                    )
                elif name == "delattr" and isinstance(node.func, ast.Name):
                    findings.append(
                        LintFinding(
                            "error",
                            f"{rel}:{node.lineno}",
                            "delattr-blocked",
                            "`delattr()` is blocked by the sandbox. Use `del obj.attr`.",
                        )
                    )
                elif name == "bytearray" and isinstance(node.func, ast.Name):
                    findings.append(
                        LintFinding(
                            "error",
                            f"{rel}:{node.lineno}",
                            "bytearray-blocked",
                            "`bytearray` is not available in the sandbox. Use `bytes` "
                            "for binary data.",
                        )
                    )
                elif name == "type" and isinstance(node.func, ast.Name) and len(node.args) >= 3:
                    findings.append(
                        LintFinding(
                            "error",
                            f"{rel}:{node.lineno}",
                            "type-3arg-blocked",
                            "`type(name, bases, dict)` dynamic class creation is not "
                            "available in the sandbox. Declare the class normally with "
                            "`class … :`.",
                        )
                    )
    return findings


# ── Custom Data rules ─────────────────────────────────────────────────────────
# Grounded in the runner: models are discovered only from `<plugin>/models/`
# (plugin_runner/ddl.py), table creation is gated on the manifest `custom_data`
# block (plugin_runner/plugin_runner.py), and CustomModel's primary key is
# `dbid`, not `id` (canvas_sdk/v1/data/base.py).

_FK_FIELDS = {"ForeignKey", "OneToOneField", "ManyToManyField"}


def _custom_data_findings(plugin_dir: Path, manifest: dict) -> list[LintFinding]:
    findings: list[LintFinding] = []

    # Collect CustomModel subclasses and where they're defined.
    custom_model_names: set[str] = set()
    definition_files: list[Path] = []
    for py_file, tree in _iter_python_files(plugin_dir):
        for node in tree.body:
            if not isinstance(node, ast.ClassDef) or "CustomModel" not in _base_names(node):
                continue
            custom_model_names.add(node.name)
            definition_files.append(py_file)
            rel = _rel(py_file, plugin_dir)
            if rel.parts and rel.parts[0] != "models":
                findings.append(
                    LintFinding(
                        "error",
                        f"{rel}:{node.lineno}",
                        "custom-model-wrong-dir",
                        f"`class {node.name}(CustomModel)` lives under `{rel.parts[0]}/` "
                        "— Canvas only loads models from `<plugin>/models/`. Move the "
                        "file into `<plugin>/models/` (alongside an `__init__.py`) or "
                        "the table will silently never be created.",
                    )
                )

    if not custom_model_names:
        return findings

    # Models present but no `custom_data` block → no namespace, no tables.
    if not manifest.get("custom_data"):
        sample = _rel(definition_files[0], plugin_dir)
        first_class = sorted(custom_model_names)[0]
        namespace_hint = f"your_org__{manifest.get('name', 'plugin')}"
        findings.append(
            LintFinding(
                "error",
                "CANVAS_MANIFEST.json",
                "missing-custom-data-block",
                f"Plugin defines CustomModel subclass(es) (e.g. `{first_class}` in "
                f"`{sample}`) but the manifest has no `custom_data` block — without it "
                "no tables are created and queries fail at runtime. Add a top-level "
                f'entry such as: "custom_data": {{"namespace": "{namespace_hint}", '
                '"access": "read_write"}',
            )
        )

    # `.filter(id=…)` / `.get(id=…)` on a local CustomModel is almost always a
    # dbid confusion (CustomModels key on `dbid`, not `id`).
    # Lazy string-ref relations to a local CustomModel can silently drop.
    for py_file, tree in _iter_python_files(plugin_dir):
        rel = _rel(py_file, plugin_dir)
        for call in ast.walk(tree):
            if not isinstance(call, ast.Call):
                continue
            # id-vs-dbid
            if isinstance(call.func, ast.Attribute) and call.func.attr in ("filter", "get"):
                receiver = call.func.value
                if (
                    isinstance(receiver, ast.Attribute)
                    and receiver.attr == "objects"
                    and isinstance(receiver.value, ast.Name)
                    and receiver.value.id in custom_model_names
                    and any(kw.arg == "id" for kw in call.keywords)
                ):
                    findings.append(
                        LintFinding(
                            "warning",
                            f"{rel}:{call.lineno}",
                            "custom-model-id-vs-dbid",
                            f"`{receiver.value.id}.objects.{call.func.attr}(id=…)` — "
                            "CustomModels use `dbid` as their primary key (only core "
                            "SDK models have `id`). Use `dbid=…` instead.",
                        )
                    )
            # lazy-fk-string-ref
            if _call_name(call) in _FK_FIELDS and call.args:
                first = call.args[0]
                if isinstance(first, ast.Constant) and isinstance(first.value, str):
                    bare = first.value.split(".", 1)[-1]
                    if bare in custom_model_names:
                        fn_name = _call_name(call)
                        findings.append(
                            LintFinding(
                                "warning",
                                f"{rel}:{call.lineno}",
                                "lazy-fk-string-ref",
                                f'`{fn_name}("{first.value}", …)` uses a lazy string '
                                "reference to a CustomModel defined in this plugin. "
                                "Canvas resolves plugin models eagerly; string refs to "
                                f"local classes can silently drop. Import the class and "
                                f"pass it directly: `{fn_name}({bare}, …)`.",
                            )
                        )

    return findings


def lint_plugin(plugin_dir: Path, manifest: dict) -> list[LintFinding]:
    """Return all construct + Custom Data findings for a plugin, most-blocking
    first (errors before warnings).
    """
    findings = _construct_findings(plugin_dir) + _custom_data_findings(plugin_dir, manifest)
    findings.sort(key=lambda f: 0 if f.severity == "error" else 1)
    return findings
