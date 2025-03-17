import ast
import builtins
import importlib
import sys
from _ast import AnnAssign
from functools import cached_property
from pathlib import Path
from typing import Any, cast

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
    copy_locations,
)

##
# ALLOWED_MODULES
#
# The modules in this list are the only ones that can be imported in a sandboxed
# runtime.
#
ALLOWED_MODULES = frozenset(
    [
        "__future__",
        "_strptime",
        "arrow",
        "base64",
        "cached_property",
        "canvas_sdk.commands",
        "canvas_sdk.data",
        "canvas_sdk.effects",
        "canvas_sdk.events",
        "canvas_sdk.handlers",
        "canvas_sdk.protocols",
        "canvas_sdk.questionnaires",
        "canvas_sdk.utils",
        "canvas_sdk.templates",
        "canvas_sdk.v1",
        "canvas_sdk.value_set",
        "canvas_sdk.views",
        "contextlib",
        "dataclasses",
        "datetime",
        "dateutil",
        "decimal",
        "django.db.models",
        "django.utils.functional",
        "enum",
        "functools",
        "hashlib",
        "hmac",
        "http",
        "json",
        "jwt",
        "logger",
        "math",
        "operator",
        "pickletools",
        "pydantic",
        "random",
        "rapidfuzz",
        "re",
        "requests",
        "secrets",
        "string",
        "time",
        "traceback",
        "typing",
        "urllib",
        "uuid",
    ]
)


##
# FORBIDDEN_ASSIGNMENTS
#
# The names in this list are forbidden to be assigned to in a sandboxed runtime.
#
FORBIDDEN_ASSIGNMENTS = frozenset(["__name__", "__is_plugin__"])


def _is_known_module(name: str) -> bool:
    return any(name.startswith(m) for m in ALLOWED_MODULES)


def _unrestricted(_ob: Any, *args: Any, **kwargs: Any) -> Any:
    """Return the given object, unmodified."""
    return _ob


def _apply(_ob: Any, *args: Any, **kwargs: Any) -> Any:
    """Call the bound method with args, support calling super().__init__()."""
    return _ob(*args, **kwargs)


def _find_folder_in_path(file_path: Path, target_folder_name: str) -> Path | None:
    """Recursively search for a folder with the specified name in the hierarchy of the given file path."""
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
            self.source_code = source_code.read_text()
            package_path = _find_folder_in_path(source_code, self.package_name)
            self.base_path = package_path.parent if package_path else None
            self._evaluated_modules: dict[str, bool] = evaluated_modules or {}
        else:
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
                "type": builtins.type,
            },
            "__metaclass__": type,
            "__name__": self.namespace,
            "__is_plugin__": True,
            "_write_": _unrestricted,
            "_getiter_": _unrestricted,
            "_getitem_": default_guarded_getitem,
            "_getattr_": getattr,
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
        return compile_restricted_exec(self.source_code, policy=self.Transformer)

    @property
    def errors(self) -> tuple[str, ...]:
        """Return errors encountered when compiling the source code."""
        return cast(tuple[str, ...], self.compile_result.errors)

    @property
    def warnings(self) -> tuple[str, ...]:
        """Return warnings encountered when compiling the source code."""
        return cast(tuple[str, ...], self.compile_result.warnings)

    def _is_known_module(self, name: str) -> bool:
        return bool(
            _is_known_module(name)
            or (self.package_name and name.split(".")[0] == self.package_name and self.base_path)
        )

    def _get_module(self, module_name: str) -> Path:
        """Get the module path for the given module name."""
        module_relative_path = module_name.replace(".", "/")
        module = Path(cast(Path, self.base_path) / f"{module_relative_path}.py")

        if not module.exists():
            module = Path(cast(Path, self.base_path) / f"{module_relative_path}/__init__.py")

        return module

    def _evaluate_module(self, module_name: str) -> None:
        """Evaluate the given module in the sandbox.
        If the module to import belongs to the same package as the current module, evaluate it inside a sandbox.
        """
        if not module_name.startswith(self.package_name) or module_name in self._evaluated_modules:
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

        # Skip evaluation if the parent module is outside the base path or already the source code root.
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

    def _safe_import(self, name: str, *args: Any, **kwargs: Any) -> Any:
        if not self._is_known_module(name):
            raise ImportError(f"{name!r} is not an allowed import.")

        self._evaluate_module(name)

        return __import__(name, *args, **kwargs)

    def execute(self) -> dict:
        """Execute the given code in a restricted sandbox."""
        if self.errors:
            raise RuntimeError(f"Code is invalid: {self.errors}")

        exec(self.compile_result.code, self.scope)

        return self.scope
