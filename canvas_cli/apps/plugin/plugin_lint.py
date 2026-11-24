"""Static pre-load lint for ``canvas validate``.

Scans a plugin for five classes of problem the sandbox handler-load can't surface
on its own (the fourth reads every shipped file, not just the source):

  * RestrictedPython constructs that fail at *runtime* inside a method body
    (``compile_restricted`` accepts them, so they load clean and only blow up
    when the line executes on the instance).
  * Custom Data setup mistakes the runner silently tolerates at load but that
    leave tables uncreated or relations dropped.
  * Request-handling mistakes that run fine but weaken the plugin: a route whose
    ``authenticate`` admits every caller (an error; the check itself lives in
    ``plugin_runner/open_routes.py``, which the runner also runs at load), a
    secret compared with ``==``, or a ``requests`` call with no timeout.
  * Credentials written into a file the package ships.
  * Queries that run once per item of a loop, which slow the handler as data grows.

The runner's sandbox (``plugin_runner/sandbox.py``) and model loader
(``plugin_runner/ddl.py``) are the source of truth; every rule here is pinned to
observed sandbox/loader behavior by a tripwire test in ``test_plugin_lint.py`` so
the lint can't drift the way a hand-maintained allowlist mirror would.
"""

from __future__ import annotations

import ast
import codecs
import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path

import pathspec

from plugin_runner.open_routes import PUBLIC_ACCESS, open_routes_in_module

CANVAS_IGNORE_FILENAME = ".canvasignore"
_DEFAULT_IGNORE = ["__pycache__", "*.pyc", "*.pyo", "node_modules"]

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


def shipped_files(package: Path) -> Iterator[tuple[Path, Path]]:
    """``(path, path inside the package)`` for every entry ``canvas install`` packages: nothing
    hidden or symlinked, and nothing the working directory's ``.canvasignore`` excludes.
    """
    ignore_file = Path.cwd() / CANVAS_IGNORE_FILENAME
    ignore_lines = _DEFAULT_IGNORE + (
        ignore_file.read_text().splitlines() if ignore_file.exists() else []
    )
    ignore = pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, ignore_lines)
    for path in package.rglob("*"):
        relative = path.relative_to(package)
        if any(part.startswith(".") for part in relative.parts):
            continue
        if path.is_symlink() or ignore.match_file(relative):
            continue
        yield path, relative


def _iter_python_files(root: Path) -> Iterator[tuple[Path, ast.Module]]:
    """Yield ``(path, parsed_ast)`` for every lintable .py file under ``root``."""
    if not root.is_dir():
        return
    for py_file in sorted(root.rglob("*.py")):
        # Match on the path *inside* the plugin. Matching absolute parts meant a
        # plugin that merely lived under a directory named tests/, build/, dist/
        # or similar had every file skipped, so the lint silently passed having
        # examined nothing.
        rel_parts = py_file.relative_to(root).parts
        if set(rel_parts) & SKIP_DIRS:
            continue
        # Skip anything under a dot-directory (e.g. .cache/uv/...).
        if any(part.startswith(".") and part not in (".", "..") for part in rel_parts[:-1]):
            continue
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        # ValueError: bytes that are not UTF-8, or a NUL byte on Python 3.11. A macOS `._`
        # AppleDouble file beside a module holds both, and the runner never imports it.
        except (OSError, SyntaxError, ValueError):
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
            elif isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Attribute):
                findings.append(
                    LintFinding(
                        "error",
                        f"{rel}:{node.lineno}",
                        "augmented-attribute",
                        "Augmented assignment to an attribute (e.g. `obj.attr += v`) is "
                        "rejected by the RestrictedPython sandbox, including on classes "
                        "the plugin defines itself. Rewrite as explicit reassignment: "
                        "`obj.attr = obj.attr + v`.",
                    )
                )
            elif isinstance(node, ast.Call):
                name = _call_name(node)
                if (
                    name == "type"
                    and isinstance(node.func, ast.Name)
                    and (len(node.args) != 1 or node.keywords)
                ):
                    # The sandbox's `type` takes one argument; the three-argument
                    # form that builds a class raises TypeError.
                    findings.append(
                        LintFinding(
                            "error",
                            f"{rel}:{node.lineno}",
                            "type-blocked",
                            "`type()` takes one argument in the sandbox. Declare classes "
                            "with `class … :` rather than `type(name, bases, dict)`.",
                        )
                    )
    return findings


# ── Request-handling rules ────────────────────────────────────────────────────
# Tripwires in test_plugin_lint.py pin the SDK behavior each rule relies on.

_REQUESTS_METHODS = {"get", "post", "put", "patch", "delete", "head", "options", "request"}
_REQUEST_INPUTS = {"headers", "query_params", "path_params"}


def _is_secret_read(node: ast.expr) -> bool:
    """``self.secrets[...]`` or ``self.secrets.get(...)``."""
    if isinstance(node, ast.Subscript):
        node = node.value
    elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        if node.func.attr != "get":
            return False
        node = node.func.value
    else:
        return False
    return isinstance(node, ast.Attribute) and node.attr == "secrets"


def _is_request_value(node: ast.expr) -> bool:
    """A value the caller sent: ``credentials.<field>``, or a request header or parameter."""
    while isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        node = node.func.value  # .get(...) / .encode() / .strip()
    if isinstance(node, ast.Subscript):
        node = node.value
    if not isinstance(node, ast.Attribute):
        return False
    is_credentials_field = isinstance(node.value, ast.Name) and node.value.id == "credentials"
    return is_credentials_field or node.attr in _REQUEST_INPUTS


def _secret_names(function: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    """Local names assigned straight from ``self.secrets`` in ``function``."""
    return {
        target.id
        for node in ast.walk(function)
        if isinstance(node, ast.Assign) and _is_secret_read(node.value)
        for target in node.targets
        if isinstance(target, ast.Name)
    }


def _open_data_route_findings(rel: Path, tree: ast.Module) -> list[LintFinding]:
    findings: list[LintFinding] = []
    for open_route in open_routes_in_module(tree):
        reached = (
            f"anyone who can reach the URL can call `{open_route.route}`"
            if open_route.route
            else "anyone who can reach the URL can open the socket"
        )
        findings.append(
            LintFinding(
                "error",
                f"{rel}:{open_route.line}",
                "unauthenticated-data-route",
                f"{open_route.describe()}, so {reached}. Use `StaffSessionAuthMixin`, "
                "`PatientSessionAuthMixin` or `APIKeyAuthMixin`, or set "
                f"`{PUBLIC_ACCESS} = True` on the class if the route is public on purpose.",
            )
        )
    return findings


def _request_findings(plugin_dir: Path) -> list[LintFinding]:
    findings: list[LintFinding] = []
    for py_file, tree in _iter_python_files(plugin_dir):
        rel = _rel(py_file, plugin_dir)
        findings += _open_data_route_findings(rel, tree)
        # A nested function is walked again inside its enclosing one; report each comparison once.
        reported: set[int] = set()
        for function in ast.walk(tree):
            if not isinstance(function, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            secrets = _secret_names(function)
            for node in ast.walk(function):
                if id(node) in reported or not (
                    isinstance(node, ast.Compare)
                    and len(node.ops) == 1
                    and isinstance(node.ops[0], ast.Eq | ast.NotEq)
                ):
                    continue
                sides = (node.left, node.comparators[0])
                is_secret = [
                    _is_secret_read(side) or (isinstance(side, ast.Name) and side.id in secrets)
                    for side in sides
                ]
                if (is_secret[0] and _is_request_value(sides[1])) or (
                    is_secret[1] and _is_request_value(sides[0])
                ):
                    reported.add(id(node))
                    findings.append(
                        LintFinding(
                            "warning",
                            f"{rel}:{node.lineno}",
                            "secret-compared-with-eq",
                            "A secret is compared with `==`, which takes longer the more "
                            "leading characters match, so a caller can guess it one "
                            "character at a time. Use `APIKeyAuthMixin` (it uses "
                            "`compare_digest`) or `hmac.compare_digest(a.encode(), b.encode())`.",
                        )
                    )
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in _REQUESTS_METHODS
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "requests"
                and not any(kw.arg in ("timeout", None) for kw in node.keywords)
            ):
                findings.append(
                    LintFinding(
                        "warning",
                        f"{rel}:{node.lineno}",
                        "requests-no-timeout",
                        f"`requests.{node.func.attr}(...)` has no `timeout`, so a slow "
                        "server holds the handler with no limit. Pass `timeout=` or use "
                        "`canvas_sdk.utils.Http`, which always sets one.",
                    )
                )
    return findings


# ── Credential rules ──────────────────────────────────────────────────────────
# Each API-key shape was a live credential in every shipped file it appeared in across
# installed plugins, so it is an error anywhere but a Markdown or reST document.

_PRIVATE_KEY = re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----")
# A downloaded service-account file: a key with a body in a JSON `private_key` field.
_SERVICE_ACCOUNT_KEY = re.compile(
    r'"private_key"\s*:\s*"-----BEGIN (?:RSA )?PRIVATE KEY-----\\n[A-Za-z0-9+/]{40,}'
)
_API_KEYS = {
    "An Anthropic API key": re.compile(r"\bsk-ant-(?:api|admin)\d{2}-[A-Za-z0-9_-]{80,}"),
    "A Slack token": re.compile(r"\bxox[bp]-\d+-\d+-[A-Za-z0-9-]{20,}"),
    "A Stripe live key": re.compile(r"\b[rs]k_live_[0-9A-Za-z]{24,}"),
    "A GitHub token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{60,})"),
    "An OpenAI key": re.compile(r"\bsk-proj-[A-Za-z0-9_-]{40,}"),
}
_SECRET_ASSIGNMENT = re.compile(
    r"(?i)(?:api_?key|secret|token|passw(?:or)?d|private_key)\w*[\"']?\s*[:=]\s*"
    r"[\"']([^\"'\s]{20,})[\"']"
)
_DOC_SUFFIXES = {".md", ".rst"}
_HEX_TOKEN = re.compile(r"[0-9a-f]{32,}")


def _looks_random(value: str) -> bool:
    """Lower, upper and digit characters, or a long lowercase hex run (a Twilio-style token),
    and not a URL: unlike a CONSTANT_NAME or a link.
    """
    if value.startswith(("http://", "https://")):
        return False
    return bool(_HEX_TOKEN.fullmatch(value)) or (
        any(c.islower() for c in value)
        and any(c.isupper() for c in value)
        and any(c.isdigit() for c in value)
    )


def file_text(content: bytes) -> str | None:
    """The text a file holds, or None when it is binary.

    UTF-16 (what Windows PowerShell's ``>`` and ``Out-File`` write) and UTF-32 hold NUL bytes
    beside every ASCII character, so a byte-order mark is read before git's own binary test, a
    NUL byte near the start. UTF-32's little-endian mark starts with UTF-16's, so it goes first.
    Anything else is read as UTF-8, so one byte that is not UTF-8 does not hide the rest of the
    file.
    """
    if content.startswith((codecs.BOM_UTF32_LE, codecs.BOM_UTF32_BE)):
        return content.decode("utf-32", errors="replace")
    if content.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)):
        return content.decode("utf-16", errors="replace")
    if b"\0" in content[:8000]:
        return None
    return content.decode("utf-8", errors="replace")


def _file_texts(files: Iterable[tuple[Path, Path]]) -> Iterator[tuple[Path, str]]:
    """``(path inside the package, text)`` for each text file in ``files``."""
    for path, rel in files:
        if not path.is_file():
            continue
        text = file_text(path.read_bytes())
        if text is not None:
            yield rel, text


def credential_findings(texts: Iterable[tuple[Path, str]]) -> list[LintFinding]:
    """The credential findings in each ``(path inside the package, text)``."""
    findings: list[LintFinding] = []
    for rel, text in texts:
        is_doc = rel.suffix.lower() in _DOC_SUFFIXES
        # Placeholder values belong in docs and tests, so a value matched by its shape alone is
        # not reported there.
        is_example = is_doc or bool({"test", "tests"} & set(rel.parts))
        for number, line in enumerate(text.split("\n"), start=1):
            where = f"{rel}:{number}"
            has_private_key = bool(_PRIVATE_KEY.search(line))
            if _SERVICE_ACCOUNT_KEY.search(line):
                findings.append(
                    LintFinding(
                        "warning" if is_doc else "error",
                        where,
                        "hardcoded-credential",
                        "A service-account private key ships inside the plugin package, where "
                        "anyone with the package can read it. Store the service-account JSON as a "
                        "manifest secret read with `self.secrets[...]`, sign with "
                        '`jwt.encode(claims, key, algorithm="RS256")`, and rotate the key.',
                    )
                )
            elif has_private_key:
                # A warning until the SDK can load an mTLS client key from a secret: `requests`
                # takes the key only as a file path, which the sandbox cannot create.
                findings.append(
                    LintFinding(
                        "warning",
                        where,
                        "hardcoded-credential",
                        "A private key ships inside the plugin package, where anyone with the "
                        "package can read it. Move it to a manifest secret read with "
                        "`self.secrets[...]` and rotate it, unless it is a mutual-TLS client "
                        "key, which plugins can only load from a file today.",
                    )
                )
            api_key = next(
                ((name, match) for name, p in _API_KEYS.items() if (match := p.search(line))),
                None,
            )
            if api_key:
                name, match = api_key
                findings.append(
                    LintFinding(
                        "warning" if is_doc else "error",
                        where,
                        "hardcoded-credential",
                        f"{name} (`{match.group(0)[:4]}…`, {len(match.group(0))} characters) "
                        "ships inside the plugin package, where anyone with the package can read "
                        "it. Move it to a manifest secret read with `self.secrets[...]`, and "
                        "rotate it.",
                    )
                )
                continue
            for value in [] if is_example or has_private_key else _SECRET_ASSIGNMENT.finditer(line):
                if _looks_random(value.group(1)):
                    findings.append(
                        LintFinding(
                            "warning",
                            where,
                            "possible-credential",
                            f"A secret-like value ({len(value.group(1))} characters) ships inside "
                            "the plugin package. If it is a real credential, move it to a manifest "
                            "secret read with `self.secrets[...]`, and rotate it.",
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
        first_class = min(custom_model_names)
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


# ── Query rules ───────────────────────────────────────────────────────────────
# A loop over a queryset or an HTTP response that runs a query per item. Only loops whose
# iterable is visibly one of those count, so a loop over a plain list stays quiet.

_RELATED_READS = {
    "all",
    "filter",
    "exclude",
    "first",
    "last",
    "exists",
    "order_by",
    "values_list",
    "aggregate",
    "latest",
    "earliest",
    "count",
}
_SERVED_BY_PREFETCH = {"all", "count", "exists"}
_QUERY_IN_LOOP = (
    "This query runs once per item of the loop, so N items cost N database round trips and "
    "the handler slows as data grows. Fetch the rows before the loop (`prefetch_related(...)`, "
    "or one `filter(<field>__in=[...])` read into a dict) and look them up inside it."
)
_PREFETCH_BYPASSED = (
    "The loop's queryset already prefetches this relation, but this read starts its own query "
    "for every item: only `all()`, `count()` and `exists()` read the prefetch. Read `.all()` "
    "and pick from it in Python, such as `next(iter(item.codings.all()), None)` for `first()`."
)
_WRITES = {
    "create",
    "bulk_create",
    "bulk_update",
    "update",
    "delete",
    "get_or_create",
    "update_or_create",
}
_COMPREHENSIONS = (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)
_ITERABLE_WRAPPERS = {"list", "tuple", "sorted", "reversed", "enumerate"}


def _chain(node: ast.expr) -> Iterator[ast.expr]:
    """Each link of a call and attribute chain, outermost first (``a.b().c`` … ``a``)."""
    while isinstance(node, ast.Call | ast.Attribute | ast.Subscript):
        yield node
        node = node.func if isinstance(node, ast.Call) else node.value
    yield node


def _reaches_objects(node: ast.expr) -> bool:
    return any(isinstance(link, ast.Attribute) and link.attr == "objects" for link in _chain(node))


def _calls_json(node: ast.expr) -> bool:
    return any(isinstance(link, ast.Call) and _call_name(link) == "json" for link in _chain(node))


def _local_values(function: ast.FunctionDef | ast.AsyncFunctionDef) -> dict[str, list[ast.expr]]:
    """Every value assigned to each plain local name in ``function``."""
    values: dict[str, list[ast.expr]] = {}
    for node in ast.walk(function):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    values.setdefault(target.id, []).append(node.value)
    return values


def _sources(node: ast.expr, local_values: dict[str, list[ast.expr]]) -> list[ast.expr]:
    """``node`` plus, when its chain starts at a local name, every value that name was assigned,
    looking through ``list(...)``, ``sorted(...)`` and the other wrappers in ``_ITERABLE_WRAPPERS``.
    """
    found, pending, seen = [], [node], set()
    while pending:
        expr = pending.pop()
        found.append(expr)
        if (
            isinstance(expr, ast.Call)
            and isinstance(expr.func, ast.Name)
            and expr.func.id in _ITERABLE_WRAPPERS
            and expr.args
        ):
            pending.append(expr.args[0])
            continue
        root = list(_chain(expr))[-1]
        if isinstance(root, ast.Name) and root.id not in seen:
            seen.add(root.id)
            pending.extend(local_values.get(root.id, []))
    return found


def _prefetched(sources: list[ast.expr]) -> set[str]:
    """Relations named in a ``prefetch_related(...)`` anywhere in ``sources``."""
    names: set[str] = set()
    for source in sources:
        for link in _chain(source):
            if not (isinstance(link, ast.Call) and _call_name(link) == "prefetch_related"):
                continue
            for arg in link.args:
                if isinstance(arg, ast.Call) and _call_name(arg) == "Prefetch" and arg.args:
                    if any(keyword.arg == "to_attr" for keyword in arg.keywords):
                        continue  # the rows land on `to_attr`; the relation's manager is uncached
                    arg = arg.args[0]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    names.add(arg.value.split("__")[0])
    return names


def _loops(function: ast.AST) -> Iterator[tuple[ast.expr, ast.expr, list[ast.AST]]]:
    """``(target, iterable, body)`` for each for-loop and comprehension in ``function``."""
    for node in ast.walk(function):
        if isinstance(node, ast.For | ast.AsyncFor):
            yield node.target, node.iter, list(node.body)
        elif isinstance(node, _COMPREHENSIONS):
            first, *rest = node.generators
            results = [node.key, node.value] if isinstance(node, ast.DictComp) else [node.elt]
            yield first.target, first.iter, [*results, *first.ifs, *rest]


def _is_related_read(call: ast.Call, loop_name: str) -> str | None:
    """The relation name when ``call`` is ``<loop_name>.<relation>.<read>(...)``."""
    fn = call.func
    if not (
        isinstance(fn, ast.Attribute)
        and fn.attr in _RELATED_READS
        and isinstance(fn.value, ast.Attribute)
        and isinstance(fn.value.value, ast.Name)
        and fn.value.value.id == loop_name
    ):
        return None
    if fn.attr == "count" and (call.args or call.keywords):
        return None  # str.count / list.count take an argument; a queryset's count does not
    return fn.value.attr


def _query_in_loop_findings(plugin_dir: Path) -> list[LintFinding]:
    findings: list[LintFinding] = []
    for py_file, tree in _iter_python_files(plugin_dir):
        rel = _rel(py_file, plugin_dir)
        # A call reached from two enclosing loops, or a call inside another call's chain, is
        # reported at most once.
        seen: set[int] = set()
        for function in ast.walk(tree):
            if not isinstance(function, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            local_values = _local_values(function)
            for target, iterable, body in _loops(function):
                sources = _sources(iterable, local_values)
                over_queryset = any(_reaches_objects(s) for s in sources)
                if not (over_queryset or any(_calls_json(s) for s in sources)):
                    continue
                loop_name = target.id if isinstance(target, ast.Name) else None
                prefetched = _prefetched(sources) if over_queryset else set()
                for part in body:
                    for call in ast.walk(part):
                        if not isinstance(call, ast.Call) or id(call) in seen:
                            continue
                        relation = None
                        if _reaches_objects(call):
                            seen.update(id(link) for link in _chain(call))
                            if _call_name(call) in _WRITES:
                                continue
                        elif over_queryset and loop_name:
                            relation = _is_related_read(call, loop_name)
                            if relation is None or (
                                relation in prefetched and _call_name(call) in _SERVED_BY_PREFETCH
                            ):
                                continue
                            seen.add(id(call))
                        else:
                            continue
                        message = _PREFETCH_BYPASSED if relation in prefetched else _QUERY_IN_LOOP
                        findings.append(
                            LintFinding("warning", f"{rel}:{call.lineno}", "query-in-loop", message)
                        )
    return findings


def lint_plugin(
    plugin_dir: Path, manifest: dict, files: Iterable[tuple[Path, Path]] | None = None
) -> list[LintFinding]:
    """Return all construct, request-handling, credential, Custom Data and query findings for
    a plugin, most-blocking first (errors before warnings). The credential rule reads ``files``
    (``(path, path inside the package)``), by default what ``canvas install`` packages.
    """
    findings = (
        _construct_findings(plugin_dir)
        + _request_findings(plugin_dir)
        + credential_findings(_file_texts(shipped_files(plugin_dir) if files is None else files))
        + _custom_data_findings(plugin_dir, manifest)
        + _query_in_loop_findings(plugin_dir)
    )
    findings.sort(key=lambda f: 0 if f.severity == "error" else 1)
    return findings
