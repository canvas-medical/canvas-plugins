import ast
import builtins
from _ast import AnnAssign
from functools import cached_property
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
        "canvas_sdk.utils",
        "canvas_sdk.v1",
        "canvas_sdk.value_set",
        "canvas_sdk.views",
        "contextlib",
        "datetime",
        "dateutil",
        "enum",
        "functools",
        "hashlib",
        "hmac",
        "http",
        "json",
        "logger",
        "math",
        "operator",
        "pickletools",
        "random",
        "re",
        "requests",
        "string",
        "time",
        "traceback",
        "typing",
        "urllib",
        "uuid",
    ]
)


def _is_known_module(name: str) -> bool:
    return any(name.startswith(m) for m in ALLOWED_MODULES)


def _safe_import(name: str, *args: Any, **kwargs: Any) -> Any:
    if not _is_known_module(name):
        raise ImportError(f"{name!r} is not an allowed import.")
    return __import__(name, *args, **kwargs)


def _unrestricted(_ob: Any, *args: Any, **kwargs: Any) -> Any:
    """Return the given object, unmodified."""
    return _ob


def _apply(_ob: Any, *args: Any, **kwargs: Any) -> Any:
    """Call the bound method with args, support calling super().__init__()."""
    return _ob(*args, **kwargs)


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
            self, node: ast.ImportFrom, name: str | None, allow_magic_methods: bool = False
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
                    '"{name}" is an invalid variable name because it '
                    'starts with "_"'.format(name=name),
                )
            elif name.endswith("__roles__"):
                self.error(
                    node,
                    '"%s" is an invalid variable name because ' 'it ends with "__roles__".' % name,
                )
            elif name in FORBIDDEN_FUNC_NAMES:
                self.error(node, f'"{name}" is a reserved name.')

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
                    '"{name}" is an invalid attribute name because it starts '
                    'with "_".'.format(name=node.attr),
                )

            if node.attr.endswith("__roles__"):
                self.error(
                    node,
                    '"{name}" is an invalid attribute name because it ends '
                    'with "__roles__".'.format(name=node.attr),
                )

            if isinstance(node.ctx, ast.Load):
                node = self.node_contents_visit(node)
                new_node = ast.Call(
                    func=ast.Name("_getattr_", ast.Load()),
                    args=[node.value, ast.Str(node.attr)],
                    keywords=[],
                )

                copy_locations(new_node, node)
                return new_node

            elif isinstance(node.ctx, (ast.Store, ast.Del)):
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

    def __init__(self, source_code: str, namespace: str | None = None) -> None:
        if source_code is None:
            raise TypeError("source_code may not be None")
        self.namespace = namespace or "protocols"
        self.source_code = source_code

    @cached_property
    def scope(self) -> dict[str, Any]:
        """Return the scope used for evaluation."""
        return {
            "__builtins__": {
                **safe_builtins.copy(),
                **utility_builtins.copy(),
                "__import__": _safe_import,
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

    def execute(self) -> dict:
        """Execute the given code in a restricted sandbox."""
        if self.errors:
            raise RuntimeError(f"Code is invalid: {self.errors}")

        exec(self.compile_result.code, self.scope)

        return self.scope
