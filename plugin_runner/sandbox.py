import ast
import builtins
import importlib
import pkgutil
import sys
import types
from _ast import AnnAssign
from collections.abc import Iterable
from functools import cached_property
from pathlib import Path
from typing import Any, cast

from frozendict import frozendict
from RestrictedPython import (
    CompileResult,
    PrintCollector,
    RestrictingNodeTransformer,
    compile_restricted_exec,
    safe_builtins,
    utility_builtins,
)
from RestrictedPython.Eval import default_guarded_getitem
from RestrictedPython.Guards import (
    guarded_iter_unpack_sequence,
    guarded_unpack_sequence,
)
from RestrictedPython.transformer import (
    ALLOWED_FUNC_NAMES,
    FORBIDDEN_FUNC_NAMES,
    INSPECT_ATTRIBUTES,
    copy_locations,
)


def find_submodules(starting_modules: Iterable[str]) -> list[str]:
    """
    Given a list of modules, return a list of those modules and their submodules.
    """
    submodules = set(starting_modules)

    for module_path in starting_modules:
        try:
            module = importlib.import_module(module_path)

            if not hasattr(module, "__path__"):
                continue

            for _, name, _ in pkgutil.walk_packages(module.__path__, prefix=module.__name__ + "."):
                submodules.add(name)
        except Exception as e:
            print(f"could not import {module_path}: {e}")

    return sorted(submodules)


CANVAS_TOP_LEVEL_MODULES = (
    "canvas_sdk.commands",
    "canvas_sdk.effects",
    "canvas_sdk.events",
    "canvas_sdk.handlers",
    "canvas_sdk.protocols",
    "canvas_sdk.questionnaires",
    "canvas_sdk.templates",
    "canvas_sdk.utils",
    "canvas_sdk.v1",
    "canvas_sdk.value_set",
    "canvas_sdk.views",
    "logger",
)

CANVAS_SUBMODULE_NAMES = [
    found_module
    for found_module in find_submodules(CANVAS_TOP_LEVEL_MODULES)
    # tests are excluded from the built and distributed module in pyproject.toml
    if "tests" not in found_module and "test_" not in found_module
]

CANVAS_MODULES: dict[str, set[str]] = {}

for module_name in CANVAS_SUBMODULE_NAMES:
    module = importlib.import_module(module_name)

    exports = getattr(module, "__exports__", None)

    if not exports:
        continue

    if module_name not in CANVAS_MODULES:
        CANVAS_MODULES[module_name] = set()

    CANVAS_MODULES[module_name].update(exports)

# In use by a current plugin...
CANVAS_MODULES["canvas_sdk.commands"].add("*")


STANDARD_LIBRARY_MODULES = {
    "__future__": {
        "annotations",
    },
    "_strptime": set(),  # gets imported at runtime via datetime.datetime.strptime()
    "base64": {
        "b64decode",
        "b64encode",
    },
    "datetime": {
        "date",
        "datetime",
        "timedelta",
        "timezone",
        "UTC",
    },
    "dateutil": {
        "relativedelta",
    },
    "dateutil.relativedelta": {
        "relativedelta",
    },
    "decimal": {
        "Decimal",
    },
    "enum": {
        "Enum",
        "StrEnum",
    },
    "functools": {
        "reduce",
    },
    "hashlib": {
        "sha256",
    },
    "hmac": {
        "compare_digest",
        "new",
    },
    "http": {
        "HTTPStatus",
    },
    "json": {
        "dumps",
        "loads",
    },
    "operator": {
        "and_",
    },
    "random": {
        "choices",
        "uniform",
        "randint",
    },
    "re": {
        "compile",
        "DOTALL",
        "IGNORECASE",
        "match",
        "search",
        "split",
        "sub",
    },
    "string": {
        "ascii_lowercase",
        "digits",
    },
    "time": {
        "time",
        "sleep",
    },
    "typing": {
        "Any",
        "Dict",
        "Final",
        "Iterable",
        "List",
        "NamedTuple",
        "NotRequired",
        "Protocol",
        "Sequence",
        "Tuple",
        "Type",
        "TypedDict",
    },
    "urllib.parse": {
        "urlencode",
        "quote",
    },
    "uuid": {
        "uuid4",
        "UUID",
    },
}


THIRD_PARTY_MODULES = {
    "arrow": {
        "get",
        "now",
        "utcnow",
    },
    "django.db.models": {
        "BigIntegerField",
        "Case",
        "CharField",
        "IntegerField",
        "Model",  # remove when hyperscribe no longer needs it
        "Q",
        "Value",
        "When",
    },
    "django.db.models.expressions": {
        "Case",
        "Value",
        "When",
    },
    "django.db.models.query": {
        "QuerySet",
    },
    "django.utils.functional": {
        "cached_property",
    },
    "jwt": {
        "decode",
        "encode",
    },
    "pydantic": {
        "ValidationError",
    },
    "rapidfuzz": {
        "fuzz",
        "process",
        "utils",
    },
    "requests": {
        "delete",
        "get",
        "patch",
        "post",
        "put",
        "request",
        "RequestException",
        "Response",
    },
}


# The modules in this list are the only ones that can be imported in a sandboxed runtime.
ALLOWED_MODULES = frozendict(
    {
        **CANVAS_MODULES,
        **STANDARD_LIBRARY_MODULES,
        **THIRD_PARTY_MODULES,
    }
)


# The names in this list are forbidden to be assigned to in a sandboxed runtime.
FORBIDDEN_ASSIGNMENTS = frozenset(["__name__", "__is_plugin__"])


def _is_known_module(name: str) -> bool:
    return any(name == module for module in ALLOWED_MODULES)


def _unrestricted(_ob: Any, *args: Any, **kwargs: Any) -> Any:
    """Return the given object, unmodified."""
    return _ob


def _apply(_ob: Any, *args: Any, **kwargs: Any) -> Any:
    """Call the bound method with args, support calling super().__init__()."""
    return _ob(*args, **kwargs)


def _find_folder_in_path(file_path: Path, target_folder_name: str) -> Path | None:
    """
    Recursively search for a folder with the specified name in the hierarchy of the given file path.
    """
    file_path = file_path.resolve()

    if file_path.name == target_folder_name:
        return file_path

    # If we've reached the root of the file system, return None
    if file_path.parent == file_path:
        return None

    return _find_folder_in_path(file_path.parent, target_folder_name)


class Sandbox:
    """A restricted sandbox for safely executing arbitrary Python code."""

    source_code: str
    namespace: str

    class Transformer(RestrictingNodeTransformer):
        """A node transformer for customizing the sandbox compiler."""

        def visit_AnnAssign(self, node: AnnAssign) -> AnnAssign:
            """Allow type annotations."""
            return node

        def check_import_names(self, node: ast.ImportFrom) -> ast.AST:
            """Check the names being imported.

            This is a protection against rebinding dunder names like
            _getitem_, _write_ via imports.

            => 'from _a import x' is ok, because '_a' is not added to the scope.
            """
            for name in node.names:
                if "*" in name.name and node.module and not _is_known_module(node.module):
                    self.error(node, '"*" imports are not allowed.')

                self.check_name(node, name.name)

                if name.asname:
                    self.check_name(node, name.asname)

            return self.node_contents_visit(node)

        def check_name(
            self,
            node: ast.ImportFrom,
            name: str | None,
            allow_magic_methods: bool = False,
        ) -> None:
            """Check names if they are allowed.

            If ``allow_magic_methods is True`` names in `ALLOWED_FUNC_NAMES`
            are additionally allowed although their names start with `_`.

            Override to turn errors into warnings for leading underscores.
            """
            if name is None:
                return

            if (
                name.startswith("_")
                and name != "_"
                and not (
                    allow_magic_methods and name in ALLOWED_FUNC_NAMES and node.col_offset != 0
                )
            ):
                self.warn(
                    node,
                    f'"{name}" is an invalid variable name because it starts with "_"',
                )
            elif name.endswith("__roles__"):
                self.error(
                    node,
                    f'"{name}" is an invalid variable name because it ends with "__roles__".',
                )
            elif name in FORBIDDEN_FUNC_NAMES:
                self.error(node, f'"{name}" is a reserved name.')

        def visit_Assign(self, node: ast.Assign) -> ast.AST:
            """Check for forbidden assignments."""
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in FORBIDDEN_ASSIGNMENTS:
                    self.error(node, f"Assignments to '{target.id}' are not allowed.")
                elif isinstance(target, ast.Tuple | ast.List):
                    self.check_for_name_in_iterable(target)

            return super().visit_Assign(node)

        def check_for_name_in_iterable(self, iterable_node: ast.Tuple | ast.List) -> None:
            """Check if any element of an iterable is a forbidden assignment."""
            for elt in iterable_node.elts:
                if isinstance(elt, ast.Name) and elt.id in FORBIDDEN_ASSIGNMENTS:
                    self.error(iterable_node, f"Assignments to '{elt.id}' are not allowed.")
                elif isinstance(elt, ast.Tuple | ast.List):
                    self.check_for_name_in_iterable(elt)

        def visit_Attribute(self, node: ast.Attribute) -> ast.AST:
            """Checks and mutates attribute access/assignment.

            'a.b' becomes '_getattr_(a, "b")'
            'a.b = c' becomes '_write_(a).b = c'
            'del a.b' becomes 'del _write_(a).b'

            The _write_ function should return a security proxy.

            Override to turn errors into warnings for leading underscores.
            """
            if node.attr.startswith("_") and node.attr != "_":
                self.warn(
                    node,
                    f'"{node.attr}" is an invalid attribute name because it starts with "_".',
                )

            if node.attr.endswith("__roles__"):
                self.error(
                    node,
                    f'"{node.attr}" is an invalid attribute name because it ends with "__roles__".',
                )

            if isinstance(node.ctx, ast.Load):
                node = self.node_contents_visit(node)
                new_node = ast.Call(
                    func=ast.Name("_getattr_", ast.Load()),
                    args=[node.value, ast.Constant(node.attr)],
                    keywords=[],
                )

                copy_locations(new_node, node)
                return new_node

            elif isinstance(node.ctx, ast.Store | ast.Del):
                node = self.node_contents_visit(node)
                new_value = ast.Call(
                    func=ast.Name("_write_", ast.Load()), args=[node.value], keywords=[]
                )

                copy_locations(new_value, node.value)
                node.value = new_value
                return node

            else:  # pragma: no cover
                # Impossible Case only ctx Load, Store and Del are defined in ast.
                raise NotImplementedError(f"Unknown ctx type: {type(node.ctx)}")

    def __init__(
        self,
        source_code: str | Path | None,
        namespace: str | None = None,
        evaluated_modules: dict[str, bool] | None = None,
    ) -> None:
        if source_code is None:
            raise TypeError("source_code may not be None")

        self.namespace = namespace or "protocols"
        self.package_name = self.namespace.split(".")[0]

        if isinstance(source_code, Path):
            if not source_code.exists():
                raise FileNotFoundError(f"File not found: {source_code}")

            self.source_code_path = source_code.as_posix()
            self.source_code = source_code.read_text()
            package_path = _find_folder_in_path(source_code, self.package_name)
            self.base_path = package_path.parent if package_path else None
            self._evaluated_modules: dict[str, bool] = evaluated_modules or {}
        else:
            self.source_code_path = "<inline code>"
            self.source_code = source_code
            self.base_path = None

    @cached_property
    def scope(self) -> dict[str, Any]:
        """Return the scope used for evaluation."""
        return {
            "__builtins__": {
                **safe_builtins.copy(),
                **utility_builtins.copy(),
                "__import__": self._safe_import,
                "classmethod": builtins.classmethod,
                "staticmethod": builtins.staticmethod,
                "any": builtins.any,
                "all": builtins.all,
                "enumerate": builtins.enumerate,
                "property": builtins.property,
                "super": builtins.super,
                "dict": builtins.dict,
                "filter": builtins.filter,
                "max": builtins.max,
                "min": builtins.min,
                "list": builtins.list,
                "next": builtins.next,
                "iter": builtins.iter,
            },
            "__metaclass__": type,
            "__name__": self.namespace,
            "__is_plugin__": True,
            "_write_": self._safe_write,
            "_getattr_": self._safe_getattr,
            "_getiter_": _unrestricted,
            "_getitem_": default_guarded_getitem,
            "_print_": PrintCollector,
            "_apply_": _apply,
            "_inplacevar_": _unrestricted,
            "_iter_unpack_sequence_": guarded_iter_unpack_sequence,
            "_unpack_sequence_": guarded_unpack_sequence,
            "hasattr": hasattr,
        }

    @cached_property
    def compile_result(self) -> CompileResult:
        """Compile the source code into bytecode."""
        return compile_restricted_exec(
            source=self.source_code,
            policy=self.Transformer,
            filename=self.source_code_path,
        )

    @property
    def errors(self) -> tuple[str, ...]:
        """Return errors encountered when compiling the source code."""
        return cast(tuple[str, ...], self.compile_result.errors)

    @property
    def warnings(self) -> tuple[str, ...]:
        """Return warnings encountered when compiling the source code."""
        return cast(tuple[str, ...], self.compile_result.warnings)

    def _is_known_module(self, name: str) -> bool:
        return _is_known_module(name) or self._same_module(name)

    def _get_module(self, module_name: str) -> Path:
        """Get the module path for the given module name."""
        module_relative_path = module_name.replace(".", "/")
        module = Path(cast(Path, self.base_path) / f"{module_relative_path}.py")

        if not module.exists():
            module = Path(cast(Path, self.base_path) / f"{module_relative_path}/__init__.py")

        return module

    def _evaluate_module(self, module_name: str) -> None:
        """Evaluate the given module in the sandbox.

        If the module to import belongs to the same package as the current module,
        evaluate it inside a sandbox.
        """
        if not self._same_module(module_name) or module_name in self._evaluated_modules:
            return  # Skip modules outside the package or already evaluated.

        module = self._get_module(module_name)
        self._evaluate_implicit_imports(module)

        # Re-check after evaluating implicit imports to avoid duplicate evaluations.
        if module_name not in self._evaluated_modules:
            Sandbox(
                module, namespace=module_name, evaluated_modules=self._evaluated_modules
            ).execute()
            self._evaluated_modules[module_name] = True

        # Reload the module if already imported to ensure the latest version is used.
        if sys.modules.get(module_name):
            importlib.reload(sys.modules[module_name])

    def _evaluate_implicit_imports(self, module: Path) -> None:
        """Evaluate implicit imports in the sandbox."""
        # Determine the parent module to check for implicit imports.
        parent = module.parent.parent if module.name == "__init__.py" else module.parent
        base_path = cast(Path, self.base_path)

        # Skip evaluation if the parent module is outside the base path or
        # already the source code root.
        if not parent.is_relative_to(base_path) or parent == base_path:
            return

        module_name = parent.relative_to(base_path).as_posix().replace("/", ".")
        init_file = parent / "__init__.py"

        if module_name not in self._evaluated_modules:
            if init_file.exists():
                # Mark as evaluated to prevent infinite recursion.
                self._evaluated_modules[module_name] = True
                Sandbox(
                    init_file, namespace=module_name, evaluated_modules=self._evaluated_modules
                ).execute()
            else:
                # Mark as evaluated even if no init file exists to prevent redundant checks.
                self._evaluated_modules[module_name] = True

        self._evaluate_implicit_imports(parent)

    def _same_module(self, module: str) -> bool:
        """
        Return True if `module` is within the plugin code.
        """
        return bool(self.base_path) and (
            module == self.package_name or f"{module}.".startswith(f"{self.package_name}.")
        )

    def _safe_write(self, _ob: Any) -> Any:
        """Check if the given obj belongs to a protected resource."""
        is_module = isinstance(_ob, types.ModuleType)

        if is_module:
            full_name = _ob.__name__
        elif isinstance(_ob, type):
            full_name = f"{_ob.__module__}.{_ob.__qualname__}"
        else:
            full_name = f"{_ob.__module__}.{_ob.__class__.__qualname__}"

        if is_module:
            if not self._same_module(full_name):
                raise TypeError(f"Forbidden assignment to a module attribute: {full_name}.")
        elif not self._same_module(_ob.__module__):
            raise TypeError(f"Forbidden assignment to a non-module attribute: {full_name}.")

        return _ob

    def _safe_getattr(self, _ob: Any, name: Any, default: Any = None) -> Any:
        """
        Prevent access to several classes of attributes.

        Restricted attribute types:

        1. underscored attributes created outside of the defining namespace
        2. attributes used by the `inspect` module
        3. if a __exports__ module property is defined, any
           attribute not in that property's value
        """
        is_module = isinstance(_ob, types.ModuleType)

        if is_module:
            module = _ob.__name__.split(".")[0]
        elif isinstance(_ob, type):
            module = _ob.__module__.split(".")[0]
        else:
            module = _ob.__class__.__module__.split(".")[0]

        if type(name) is not str:
            raise TypeError("type(name) must be str")

        if name in ("format", "format_map") and (
            isinstance(_ob, str) or (isinstance(_ob, type) and issubclass(_ob, str))
        ):
            raise NotImplementedError(
                "Using the format and format_map methods of `str` is not safe"
            )

        if name in INSPECT_ATTRIBUTES:
            raise AttributeError(f'"{name}" is a restricted name.')

        # Code defined in the Sandbox namespace can access its own underscore variables
        if name.startswith("_") and module != self.namespace:
            raise AttributeError(
                f'"{name}" is an invalid attribute name because it starts with "_"'
            )

        exports = getattr(_ob, "__exports__", None)

        if exports:
            if name not in exports:
                raise AttributeError(f'"{name}" is an invalid attribute name (not in __exports__)')
        elif is_module and (module not in ALLOWED_MODULES or name not in ALLOWED_MODULES[module]):
            raise AttributeError(f'"{name}" is an invalid attribute name (not in ALLOWED_MODULES)')

        return getattr(_ob, name, default)

    def _safe_import(self, name: str, *args: Any, **kwargs: Any) -> Any:
        if not self._same_module(name):
            if name not in ALLOWED_MODULES:
                raise ImportError(f"{name!r} is not an allowed import.")

            # Disallow importing anything not explicitly allowed by ALLOWED_MODULES
            if len(args) >= 3:
                from_list = args[2]

                if from_list is not None:
                    for item in from_list:
                        if item not in ALLOWED_MODULES.get(name, set()):
                            raise ImportError(f"{item!r} is not an allowed import from {name!r}.")

        self._evaluate_module(name)

        return __import__(name, *args, **kwargs)

    def execute(self) -> dict:
        """Execute the given code in a restricted sandbox."""
        if self.errors:
            raise RuntimeError(f"Code is invalid: {self.errors}")

        exec(self.compile_result.code, self.scope)

        return self.scope
