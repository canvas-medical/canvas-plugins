from __future__ import annotations

import ast
import builtins
import importlib
import inspect
import json
import logging
import operator
import string
import sys
import traceback
import types
from _ast import AnnAssign
from collections.abc import Callable, Generator, Iterable, Mapping, Sequence
from contextlib import AbstractContextManager, contextmanager, nullcontext
from contextvars import ContextVar
from enum import StrEnum
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Any, NoReturn, TypedDict, cast

from frozendict import frozendict
from RestrictedPython import (
    CompileResult,
    PrintCollector,
    RestrictingNodeTransformer,
    safe_builtins,
    utility_builtins,
)
from RestrictedPython._types import T_pos_ast
from RestrictedPython.compile import syntax_error_template
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

from plugin_runner.sandbox_allowlists import is_blessed_import

logger = logging.getLogger("plugin_runner_logger")


class SandboxMode(StrEnum):
    """Which set of sandbox rules a `Sandbox` enforces.

    `STRICT` is the current rule set and the default. `LEGACY_PERMISSIVE` is the previous
    one, deprecated and kept only so that a plugin written against it keeps loading; the
    plugin runner uses it when a strict load fails and reports each use to Sentry. It
    will be removed, at which point a plugin that depends on it stops loading.
    """

    STRICT = "strict"
    LEGACY_PERMISSIVE = "legacy-permissive"


# The plugin modules one load has evaluated, shared by every sandbox in that load. Under
# `STRICT` each value is the module object the load built, which is what the load's
# imports resolve to; under `LEGACY_PERMISSIVE` it is `True`.
EvaluatedModules = dict[str, "bool | types.ModuleType"]


if TYPE_CHECKING:

    class ImportedNames(TypedDict):
        """
        Type the stored imported_names dicitionary for mypy.
        """

        names: list[str]
        names_to_module: dict[str, str]


try:
    allowed_module_imports_path = Path(__file__).parent / "allowed-module-imports.json"

    CANVAS_MODULES: dict[str, Iterable[str]] = json.loads(allowed_module_imports_path.read_text())

    for key in CANVAS_MODULES:
        CANVAS_MODULES[key] = set(CANVAS_MODULES[key])

except FileNotFoundError:
    print("Error: Unable to load plugin_runner/allowed-module-imports.json, aborting")
    sys.exit(1)


@contextmanager
def suppress_model_registration() -> Generator[None, None, None]:
    """Temporarily replace Django's model registration with no-ops.

    Prevents ModelBase.__new__ and ForeignKey.contribute_to_class from
    polluting apps.all_models during sandbox validation or DDL extraction,
    avoiding the "shadow model registry" problem where two class objects
    exist for the same model.
    """
    from django.apps import apps

    _orig_register = apps.register_model
    _orig_lazy = apps.lazy_model_operation
    apps.register_model = lambda *a, **kw: None  # type: ignore[method-assign]
    apps.lazy_model_operation = lambda *a, **kw: None  # type: ignore[method-assign]
    try:
        yield
    finally:
        apps.register_model = _orig_register  # type: ignore[method-assign]
        apps.lazy_model_operation = _orig_lazy  # type: ignore[method-assign]


# The rounding methods numbers define; `math.floor` and friends call the same ones.
_NUMERIC_ROUNDING_METHODS = {"__ceil__", "__floor__", "__round__", "__trunc__"}

# Private names plugin code reads on SDK objects, by the class that defines them.
_READABLE_SDK_PRIVATE_NAMES = {
    "canvas_sdk.clients.canvas_fhir.client.CanvasFhir": frozenset({"_base_url", "_get_headers"}),
}


def _is_readable_sdk_private(ob: Any, name: str) -> bool:
    """Whether `name` is a private name plugin code may read on `ob`."""
    return any(
        name in _READABLE_SDK_PRIVATE_NAMES.get(f"{cls.__module__}.{cls.__qualname__}", ())
        for cls in type(ob).__mro__
    )


# Every builtin exception and warning class, so an except clause naming one works.
_BUILTIN_EXCEPTIONS = {
    name: value
    for name, value in vars(builtins).items()
    if not name.startswith("_") and isinstance(value, type) and issubclass(value, BaseException)
}


# Names the sandbox injects into the execution scope to enforce its policy.
# RestrictedPython rewrites attribute access, item access, writes, unpacking and
# printing into calls to these, binds `_print` in each function that prints, and
# compiles class bodies against `__metaclass__`, so they belong to the sandbox
# rather than to plugin code and are reserved: binding one is an error in any
# syntax.
PROTECTED_SCOPE_NAMES = frozenset(
    {
        "__metaclass__",
        "_apply_",
        "_getattr_",
        "_getitem_",
        "_getiter_",
        "_inplacevar_",
        "_iter_unpack_sequence_",
        "_print_",
        "_print",
        "_unpack_sequence_",
        "_write_",
    }
)


SAFE_INTERNAL_DUNDER_READ_ATTRIBUTES = {
    "__annotations__",
    "__args__",
    "__class__",
    "__dict__",
    "__doc__",
    "__eq__",
    "__init__",
    "__members__",
    "__name__",
    "__origin__",
    "__traceback__",
    *_NUMERIC_ROUNDING_METHODS,
}


SAFE_EXTERNAL_DUNDER_READ_ATTRIBUTES = {
    "__annotations__",
    "__args__",
    "__class__",
    "__dict__",
    "__doc__",
    "__eq__",
    "__init__",
    "__members__",
    "__name__",
    "__origin__",
    "__traceback__",
    *_NUMERIC_ROUNDING_METHODS,
}


_NO_DEFAULT: Any = object()


#: Names read as None because nothing defines them, collected while `canvas validate` loads a
#: plugin.
_missing_attribute_reads: ContextVar[list[str] | None] = ContextVar(
    "missing_attribute_reads", default=None
)

#: Names already logged, by plugin, so each is logged once per process.
_logged_missing_attributes: dict[str, set[str]] = {}

#: How many missing names are logged per plugin, and how much of each name.
_MAX_LOGGED_MISSING_ATTRIBUTES = 200
_MAX_MISSING_ATTRIBUTE_LABEL_LENGTH = 100


@contextmanager
def collect_missing_attribute_reads() -> Generator[list[str], None, None]:
    """Collect each name read as None because nothing defines it, in the order first read."""
    reads: list[str] = []
    token = _missing_attribute_reads.set(reads)

    try:
        yield reads
    finally:
        _missing_attribute_reads.reset(token)


def _note_missing_attribute(plugin: str, ob: Any, name: str) -> None:
    """Record that `plugin` read `name`, which nothing on `ob` defines."""
    owner = ob.__name__ if isinstance(ob, type | types.ModuleType) else type(ob).__name__
    label = f"{owner}.{name}"

    if len(label) > _MAX_MISSING_ATTRIBUTE_LABEL_LENGTH:
        label = f"{label[:_MAX_MISSING_ATTRIBUTE_LABEL_LENGTH]}..."

    if (reads := _missing_attribute_reads.get()) is not None and label not in reads:
        reads.append(label)

    logged = _logged_missing_attributes.setdefault(plugin, set())

    if label not in logged and len(logged) < _MAX_LOGGED_MISSING_ATTRIBUTES:
        logged.add(label)
        logger.warning(
            'Plugin "%s" read %r, which does not exist; it reads as None today and will '
            "raise an AttributeError in a future release.",
            plugin,
            label,
        )


def _getattr_or_default(_ob: Any, name: str, default: Any, plugin: str) -> Any:
    """`getattr`, falling back to `default` when the caller supplied one.

    Without a default, an AttributeError from an attribute the object defines, such as a
    property raising Django's RelatedObjectDoesNotExist, propagates as plain attribute
    access does. A name nothing defines reads as None, as it always has in the sandbox,
    and is reported so plugins can stop relying on it.
    """
    if default is not _NO_DEFAULT:
        return getattr(_ob, name, default)

    try:
        return getattr(_ob, name)
    except AttributeError:
        if inspect.getattr_static(_ob, name, _NO_DEFAULT) is not _NO_DEFAULT:
            raise

        _note_missing_attribute(plugin, _ob, name)

        return None


class _SafeClass:
    """A read-only proxy for a class that only exposes its name and its ancestors' names."""

    __slots__ = ("__name__", "_ancestor_names")

    _ancestor_names: tuple[str, ...]

    def __init__(self, name: str, ancestor_names: tuple[str, ...] = ()) -> None:
        object.__setattr__(self, "__name__", name)
        object.__setattr__(self, "_ancestor_names", ancestor_names)

    @classmethod
    def of(cls, klass: type) -> _SafeClass:
        """The proxy for `klass`."""
        return cls(klass.__name__, tuple(ancestor.__name__ for ancestor in klass.__mro__))

    @property
    def __mro__(self) -> tuple[_SafeClass, ...]:
        """The class and its ancestors, each as a name-only proxy."""
        return tuple(_SafeClass(name) for name in self._ancestor_names)

    def __getattr__(self, name: str) -> NoReturn:
        raise AttributeError(f'Access to "{name}" on external __class__ is restricted')

    def __setattr__(self, name: str, value: Any) -> NoReturn:
        raise AttributeError("Cannot set attributes on external __class__")

    def __repr__(self) -> str:
        return f"<SafeClass '{self.__name__}'>"


class _SafeType:
    """The `type` plugin code sees.

    Called with one argument it answers exactly what reading `__class__` does; the
    three-argument form that builds a class is refused. `isinstance(x, type)` and
    `issubclass(x, type)` answer as they do in Python.
    """

    __slots__ = ("_class_of",)

    _class_of: Callable[[Any, str], Any]

    def __init__(self, safe_getattr: Callable[[Any, str], Any]) -> None:
        self._class_of = safe_getattr

    def __call__(self, *args: Any) -> Any:
        if len(args) != 1:
            raise TypeError("type() takes exactly one argument in plugin code")

        return self._class_of(args[0], "__class__")

    def __instancecheck__(self, instance: Any) -> bool:
        return isinstance(instance, type)

    def __subclasscheck__(self, subclass: Any) -> bool:
        return issubclass(subclass, type)


class _SafeCode:
    """A read-only proxy for a code object that only exposes filename and function name.

    Does not expose bytecode, constants, variable names, or other internals
    that could be used to reverse-engineer or escape the sandbox.

    Uses ``__exports__`` so the sandbox's ``_safe_getattr`` blocks everything else.
    """

    __exports__ = ("co_filename", "co_name")
    __slots__ = ("co_filename", "co_name")
    co_filename: str
    co_name: str

    def __init__(self, code: types.CodeType) -> None:
        object.__setattr__(self, "co_filename", code.co_filename)
        object.__setattr__(self, "co_name", code.co_name)

    def __setattr__(self, attr: str, value: Any) -> NoReturn:
        raise AttributeError("Cannot set attributes on code object")

    def __repr__(self) -> str:
        return f'<SafeCode file="{self.co_filename}" name="{self.co_name}">'


class _SafeFrame:
    """A read-only proxy for a frame object that only exposes a safe code object.

    Does not expose ``f_locals``, ``f_globals``, ``f_builtins``, or ``f_back``,
    which would allow full sandbox escape.

    Uses ``__exports__`` so the sandbox's ``_safe_getattr`` blocks everything else.
    """

    __exports__ = ("f_code", "f_lineno")
    __slots__ = ("f_code", "f_lineno")
    f_code: _SafeCode
    f_lineno: int

    def __init__(self, frame: types.FrameType) -> None:
        object.__setattr__(self, "f_code", _SafeCode(frame.f_code))
        object.__setattr__(self, "f_lineno", frame.f_lineno)

    def __setattr__(self, attr: str, value: Any) -> NoReturn:
        raise AttributeError("Cannot set attributes on frame object")

    def __repr__(self) -> str:
        return f"<SafeFrame {self.f_code!r}>"


class _SafeField:
    """A read-only view of a model field for introspection.

    Uses ``__exports__`` so the sandbox's ``_safe_getattr`` blocks everything else.
    """

    __exports__ = (
        "attname",
        "blank",
        "choices",
        "column",
        "concrete",
        "default",
        "get_internal_type",
        "is_relation",
        "many_to_many",
        "many_to_one",
        "max_length",
        "name",
        "null",
        "one_to_many",
        "one_to_one",
        "related_model",
    )
    __slots__ = ("_field",)

    def __init__(self, field: Any) -> None:
        object.__setattr__(self, "_field", field)

    def __getattr__(self, name: str) -> Any:
        if name not in _SafeField.__exports__:
            raise AttributeError(name)

        field = object.__getattribute__(self, "_field")

        if name == "get_internal_type":
            internal_type = field.get_internal_type()
            return lambda: internal_type

        if name == "default":
            default = getattr(field, "default", None)
            return None if callable(default) else default

        return getattr(field, name, None)

    def __setattr__(self, attr: str, value: Any) -> NoReturn:
        raise AttributeError("Cannot set attributes on a model field")

    def __repr__(self) -> str:
        return f"<SafeField {object.__getattribute__(self, '_field').name}>"


class _SafeModelMeta:
    """A read-only view of an SDK model's ``_meta`` for field introspection.

    Uses ``__exports__`` so the sandbox's ``_safe_getattr`` blocks everything else.
    """

    __exports__ = (
        "app_label",
        "concrete_fields",
        "db_table",
        "fields",
        "get_field",
        "get_fields",
        "local_fields",
        "model_name",
        "pk",
        "verbose_name",
        "verbose_name_plural",
    )
    __slots__ = ("_options",)

    def __init__(self, options: Any) -> None:
        object.__setattr__(self, "_options", options)

    def __getattr__(self, name: str) -> Any:
        if name not in _SafeModelMeta.__exports__:
            raise AttributeError(name)

        options = object.__getattribute__(self, "_options")

        if name == "get_field":
            return lambda field_name: _SafeField(options.get_field(field_name))

        if name == "get_fields":
            return lambda include_parents=True, include_hidden=False: tuple(
                _SafeField(field)
                for field in options.get_fields(
                    include_parents=include_parents, include_hidden=include_hidden
                )
            )

        if name in ("concrete_fields", "fields", "local_fields"):
            return tuple(_SafeField(field) for field in getattr(options, name))

        if name == "pk":
            return _SafeField(options.pk) if options.pk is not None else None

        return str(getattr(options, name))

    def __setattr__(self, attr: str, value: Any) -> NoReturn:
        raise AttributeError("Cannot set attributes on model metadata")

    def __repr__(self) -> str:
        return f"<SafeModelMeta {object.__getattribute__(self, '_options').label}>"


def _is_model_options(value: Any) -> bool:
    """Whether `value` is a Django model's `_meta`, recognized without importing Django."""
    cls = type(value)
    return cls.__name__ == "Options" and cls.__module__ == "django.db.models.options"


class _SafeTraceback:
    """A read-only proxy for a traceback object that supports the standard traversal pattern.

    Exposes ``tb_frame`` (as a ``_SafeFrame``), ``tb_lineno``, and ``tb_next``
    (as another ``_SafeTraceback`` or ``None``).  Does not expose ``tb_lasti``
    or allow mutation.

    Uses ``__exports__`` so the sandbox's ``_safe_getattr`` blocks everything else.
    """

    __exports__ = ("tb_frame", "tb_lineno", "tb_next")
    __slots__ = ("tb_frame", "tb_lineno", "tb_next")
    tb_frame: _SafeFrame
    tb_lineno: int
    tb_next: _SafeTraceback | None

    def __init__(self, tb: types.TracebackType) -> None:
        object.__setattr__(self, "tb_frame", _SafeFrame(tb.tb_frame))
        object.__setattr__(self, "tb_lineno", tb.tb_lineno)
        object.__setattr__(self, "tb_next", _SafeTraceback(tb.tb_next) if tb.tb_next else None)

    def __setattr__(self, attr: str, value: Any) -> NoReturn:
        raise AttributeError("Cannot set attributes on traceback object")

    def __repr__(self) -> str:
        return f"<SafeTraceback line={self.tb_lineno}>"


class _SafeFrameSummary:
    """A read-only proxy for traceback FrameSummary that only exposes safe attributes.

    Exposes file name, line number, and function name. Does not expose
    source code lines or local variables, which could leak sandbox internals.

    Uses ``__exports__`` so the sandbox's ``_safe_getattr`` blocks everything else.
    """

    __exports__ = ("filename", "lineno", "name")
    __slots__ = ("filename", "lineno", "name")
    filename: str
    lineno: int | None
    name: str

    def __init__(self, frame: traceback.FrameSummary) -> None:
        object.__setattr__(self, "filename", frame.filename)
        object.__setattr__(self, "lineno", frame.lineno)
        object.__setattr__(self, "name", frame.name)

    def __setattr__(self, attr: str, value: Any) -> NoReturn:
        raise AttributeError("Cannot set attributes on frame summary")

    def __repr__(self) -> str:
        return f'<SafeFrameSummary file="{self.filename}" line={self.lineno} name="{self.name}">'


def _extract_exc_frames() -> list[_SafeFrameSummary]:
    """Extract frame summaries from the current exception's traceback.

    Returns a list of SafeFrameSummary objects with only filename, lineno,
    and function name. Must be called from within an except block.

    Returns an empty list if no exception is active.
    """
    exc_info = sys.exc_info()
    tb = exc_info[2]
    if tb is None:
        return []
    frames = traceback.extract_tb(tb)
    return [_SafeFrameSummary(frame) for frame in frames]


# Method names the sandbox does not expose, despite not starting with an underscore.
RESTRICTED_METHOD_NAMES = {
    # Loader methods, which resolve modules outside _safe_import
    "load_module",
    "exec_module",
    "create_module",
    "find_module",
    "find_spec",
    "find_loader",
    # Code execution
    "exec",
    "eval",
    # Type hierarchy traversal
    "mro",
}

STANDARD_LIBRARY_MODULES = {
    "__future__": {
        "annotations",
    },
    "_strptime": set(),  # gets imported at runtime via datetime.datetime.strptime()
    "abc": {
        "ABC",
        "abstractmethod",
    },
    "base64": {
        "b64decode",
        "b64encode",
        "urlsafe_b64decode",
        "urlsafe_b64encode",
    },
    "bisect": {
        "bisect_left",
        "bisect_right",
        "insort",
    },
    "collections": {
        "Counter",
        "defaultdict",
        "OrderedDict",
    },
    "dataclasses": {
        "asdict",
        "astuple",
        "dataclass",
        "field",
        "Field",
        "fields",
        "InitVar",
        "is_dataclass",
        "make_dataclass",
        "replace",
    },
    "copy": {
        "copy",
        "deepcopy",
    },
    "datetime": {
        "date",
        "datetime",
        "time",
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
    "email.mime.multipart": {
        "MIMEMultipart",
    },
    "email.mime.text": {
        "MIMEText",
    },
    "enum": {
        "Enum",
        "StrEnum",
    },
    "functools": {
        "reduce",
        "wraps",
    },
    "hashlib": {
        "sha1",
        "sha256",
    },
    "hmac": {
        "compare_digest",
        "new",
    },
    "http": {
        "HTTPStatus",
    },
    "html": {
        "escape",
        "HTML",
        "unescape",
    },
    "io": {
        "BytesIO",
        "StringIO",
    },
    "json": {
        "dump",
        "dumps",
        "load",
        "loads",
        "JSONDecodeError",
    },
    "operator": {
        "and_",
        "or_",
    },
    "random": {
        "choice",
        "choices",
        "Random",
        "random",
        "sample",
        "uniform",
        "randint",
    },
    "re": {
        "compile",
        "DOTALL",
        "escape",
        "I",
        "IGNORECASE",
        "findall",
        "finditer",
        "fullmatch",
        "M",
        "match",
        "MULTILINE",
        "S",
        "search",
        "split",
        "sub",
    },
    # Cryptographically secure randomness; `random` is predictable from its output
    "secrets": {
        "choice",
        "compare_digest",
        "randbelow",
        "token_bytes",
        "token_hex",
        "token_urlsafe",
    },
    "statistics": {
        "median",
    },
    "string": {
        "ascii_lowercase",
        "digits",
    },
    "time": {
        "monotonic",
        "perf_counter",
        "sleep",
        "time",
        "time_ns",
    },
    "traceback": {
        "format_exc",
    },
    "typing": {
        "Any",
        "Callable",
        "cast",
        "ClassVar",
        "Dict",
        "Final",
        "Iterable",
        "List",
        "Literal",
        "NamedTuple",
        "NotRequired",
        "Optional",
        "Pattern",
        "Protocol",
        "Sequence",
        "Tuple",
        "TYPE_CHECKING",
        "Type",
        "TypedDict",
        "TypeGuard",
        "Union",
    },
    "urllib": {
        "parse",
    },
    "urllib.parse": {
        "parse_qs",
        "urlencode",
        "urlparse",
        "quote",
        "unquote",
    },
    "uuid": {
        "NAMESPACE_URL",
        "uuid4",
        "uuid5",
        "UUID",
    },
    "defusedxml.ElementTree": {
        "fromstring",
    },
    "xml.etree": {
        "ElementTree",
    },
    # Parses untrusted input, but only expands internal entities: external entities are
    # not resolved, so it reads no files and makes no requests. Entity expansion can be
    # made costly, which a plugin can already do with a loop.
    "xml.etree.ElementTree": {
        "Element",
        "ElementTree",
        "QName",
        "SubElement",
        "fromstring",
        "indent",
        "iterparse",
        "parse",
        "register_namespace",
        "tostring",
    },
    # Compression is pure computation: no file, socket or process behind it.
    "zlib": {
        "MAX_WBITS",
        "adler32",
        "compress",
        "compressobj",
        "crc32",
        "decompress",
        "decompressobj",
        "error",
    },
    "zoneinfo": {
        "ZoneInfo",
    },
}


THIRD_PARTY_MODULES = {
    "arrow": {
        "Arrow",
        "get",
        "now",
        "parser",
        "utcnow",
    },
    "arrow.parser": {
        "ParserError",
        "ParserMatchError",
    },
    "certifi": {
        "where",
    },
    "django.contrib.postgres.indexes": {
        "GinIndex",
    },
    "django.core.exceptions": {
        "ObjectDoesNotExist",
        "PermissionDenied",
        "ValidationError",
    },
    "django.db": {
        "DatabaseError",
        "IntegrityError",
    },
    "django.db.transaction": {
        "atomic",
        "on_commit",
        "on_rollback",
    },
    "django.db.models": {
        "Avg",
        "BigIntegerField",
        "BooleanField",
        "CASCADE",
        "Case",
        "CharField",
        "Count",
        "DateField",
        "DateTimeField",
        "DecimalField",
        "DO_NOTHING",
        "F",
        "FloatField",
        "ForeignKey",
        "Func",
        "Index",
        "Exists",
        "IntegerField",
        "JSONField",
        "ManyToManyField",
        "Max",
        "Min",
        "Model",  # remove when hyperscribe no longer needs it
        "OneToOneField",
        "TextField",
        "OuterRef",
        "Prefetch",
        "Q",
        "RowRange",
        "SET_NULL",
        "Subquery",
        "Sum",
        "UniqueConstraint",
        "Value",
        "ValueRange",
        "When",
        "Window",
    },
    "django.db.models.expressions": {
        "Case",
        "Exists",
        "OuterRef",
        "Subquery",
        "Value",
        "When",
    },
    "django.db.models.functions": {
        "Coalesce",
        "CumeDist",
        "DenseRank",
        "FirstValue",
        "Lag",
        "LastValue",
        "Lead",
        "Length",
        "NthValue",
        "Ntile",
        "PercentRank",
        "Rank",
        "RowNumber",
        "Trim",
    },
    "django.db.models.query": {
        "Prefetch",
        "QuerySet",
    },
    "django.utils": {
        "timezone",
    },
    "django.utils.timezone": {
        "get_current_timezone",
        "localdate",
        "localtime",
        "make_aware",
        "now",
        "utc",
    },
    "django.utils.functional": {
        "cached_property",
    },
    "jwt": {
        "decode",
        "encode",
        "PyJWKClient",
        "ExpiredSignatureError",
        "InvalidTokenError",
    },
    "pydantic": {
        "BaseModel",
        "ConfigDict",
        "conint",
        "constr",
        "Field",
        "RootModel",
        "ValidationError",
    },
    "rapidfuzz": {
        "fuzz",
        "process",
        "utils",
    },
    "rapidfuzz.fuzz": {
        "partial_ratio",
        "partial_ratio_alignment",
        "partial_token_ratio",
        "partial_token_set_ratio",
        "partial_token_sort_ratio",
        "QRatio",
        "ratio",
        "token_ratio",
        "token_set_ratio",
        "token_sort_ratio",
        "WRatio",
    },
    "rapidfuzz.process": {
        "cdist",
        "cpdist",
        "extract",
        "extract_iter",
        "extractOne",
    },
    "rapidfuzz.utils": {
        "default_process",
    },
    "requests": {
        "codes",
        "delete",
        "exceptions",
        "get",
        "HTTPError",
        "patch",
        "post",
        "put",
        "request",
        "Request",
        "RequestException",
        "Response",
        "Session",
        "Timeout",
    },
    "requests.exceptions": {
        "ConnectionError",
        "HTTPError",
        "JSONDecodeError",
        "RequestException",
        "Timeout",
    },
    "snowflake.connector": {
        "apilevel",
        "connect",
        "DatabaseError",
        "DataError",
        "DictCursor",
        "Error",
        "IntegrityError",
        "InterfaceError",
        "InternalError",
        "NotSupportedError",
        "OperationalError",
        "paramstyle",
        "ProgrammingError",
        "SnowflakeConnection",
        "threadsafety",
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


def _is_known_module(name: str) -> bool:
    return name in ALLOWED_MODULES


def _safe_getitem(ob: Any, index: Any) -> Any:
    """
    Prevent access to underscore-prefixed item keys on external objects.

    Built-in containers and every dict, whatever its class, may hold underscore keys:
    they are the plugin's data, not an object's namespace.
    """
    if isinstance(index, str) and index.startswith("_") and not isinstance(ob, dict):
        if isinstance(ob, types.ModuleType):
            module = ob.__name__
        elif isinstance(ob, type):
            module = ob.__module__
        else:
            module = ob.__class__.__module__

        if module != "builtins" and module not in ALLOWED_MODULES:
            raise AttributeError(f'"{index}" is an invalid item name because it starts with "_"')

    return ob[index]


def _legacy_safe_getitem(ob: Any, index: Any) -> Any:
    """Reject every underscore-prefixed item key, including on plugin-owned containers.

    The `LEGACY_PERMISSIVE` counterpart to `_safe_getitem`.
    """
    if isinstance(index, str) and index.startswith("_"):
        raise AttributeError(f'"{index}" is an invalid item name because it starts with "_"')

    return ob[index]


def _public_attributes(namespace: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of an object's namespace without its underscore-prefixed names.

    A copy rather than a view, so nothing done to the result reaches the object, and
    the private names are never in it to be reached by any route.
    """
    return {
        key: value
        for key, value in namespace.items()
        if not (isinstance(key, str) and key.startswith("_"))
    }


class _SafeFormatter(string.Formatter):
    """A `str.format` that cannot traverse into the values it formats.

    The format mini-language performs its own attribute and item lookups inside
    CPython, so `"{0.__class__.__init__.__globals__}".format(x)` reaches the real
    builtins without ever passing through `_safe_getattr` or `_safe_getitem`.
    Substitution itself is harmless; only the traversal has to go, which leaves
    `"{} {name}".format(value, name=other)` working as written.
    """

    def get_field(self, field_name: str, args: Any, kwargs: Any) -> Any:
        """Resolve a replacement field, refusing to walk into the value."""
        if "." in field_name or "[" in field_name:
            raise NotImplementedError(
                f"Attribute and item access inside a format string is not allowed: "
                f'"{{{field_name}}}". Read the value out first, then format it.'
            )

        return super().get_field(field_name, args, kwargs)


_SAFE_FORMATTER = _SafeFormatter()


def _safe_format(template: str) -> Callable[..., str]:
    """Return a `format` bound to `template` that cannot traverse its arguments."""

    def format(*args: Any, **kwargs: Any) -> str:
        return _SAFE_FORMATTER.vformat(template, args, kwargs)

    return format


def _safe_format_map(template: str) -> Callable[[Any], str]:
    """Return a `format_map` bound to `template` that cannot traverse its mapping."""

    def format_map(mapping: Any) -> str:
        return _SAFE_FORMATTER.vformat(template, (), mapping)

    return format_map


def _unrestricted(_ob: Any, *args: Any, **kwargs: Any) -> Any:
    """Return the given object, unmodified."""
    return _ob


def _inplacevar(op: Any, val: Any, expr: Any) -> Any:
    """
    Apply the specified operation to the value and expression.

    NOTE: Does not yet support += concatenation for sequences.
    """
    ops = {
        "-=": operator.isub,
        "@=": operator.imatmul,
        "**=": operator.ipow,
        "*=": operator.imul,
        "//=": operator.ifloordiv,
        "/=": operator.itruediv,
        "&=": operator.iand,
        "%=": operator.imod,
        "^=": operator.ixor,
        "+=": operator.iadd,
        "<<=": operator.ilshift,
        ">>=": operator.irshift,
        "|=": operator.ior,
    }

    if op not in ops:
        raise ValueError(f"Invalid inplace operation: {op}")

    return ops[op](val, expr)


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


def node_name(node: ast.AST) -> str:
    """
    Given an AST node, return its name.
    """
    if isinstance(node, ast.Call):
        return ".".join(node_name(arg) for arg in node.args)

    if isinstance(node, ast.Constant):
        return str(node.value)

    if isinstance(node, ast.Name):
        return str(node.id)

    return "__unknown__"


class Sandbox:
    """A restricted sandbox for safely executing arbitrary Python code."""

    source_code: str
    namespace: str

    class Transformer(RestrictingNodeTransformer):
        """A node transformer for customizing the sandbox compiler."""

        imported_names: ImportedNames

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)

            # ids of the `def` statements directly in a class body
            self.method_ids: set[int] = set()

            self.imported_names = {"names": [], "names_to_module": {}}

        def handle_names(self, node: ast.Import | ast.ImportFrom) -> None:
            """
            Store imported names.
            """
            module = node.module if isinstance(node, ast.ImportFrom) else None

            for name in node.names:
                name_string = name.asname if name.asname else name.name

                self.imported_names["names"].append(name_string)

                if module:
                    self.imported_names["names_to_module"][name_string] = module

        def visit_Import(self, node: ast.Import) -> ast.Import:
            """
            Store imported names.
            """
            visited = cast(ast.Import, super().visit_Import(node))

            self.handle_names(visited)

            return visited

        def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.ImportFrom:
            """
            Store imported names.
            """
            visited = cast(ast.ImportFrom, super().visit_ImportFrom(node))

            self.handle_names(visited)

            return visited

        def visit_AnnAssign(self, node: AnnAssign) -> AnnAssign:
            """Allow type annotations."""
            return self.node_contents_visit(node)

        def visit_Constant(self, node: ast.Constant) -> ast.Constant:
            """Allow constants."""
            return self.node_contents_visit(node)

        def visit_Match(self, node: ast.Match) -> ast.Match:
            """Allow `match`."""
            return self.node_contents_visit(node)

        def visit_MatchAs(self, node: ast.MatchAs) -> ast.MatchAs:
            """Allow `match`, and check the name a capture pattern binds.

            A capture pattern assigns the subject to a plain `str` field on the
            pattern node rather than to an `ast.Name`, so the name reaches the
            check only from here.
            """
            self.check_binding(node, node.name)

            return self.node_contents_visit(node)

        def visit_MatchClass(self, node: ast.MatchClass) -> ast.MatchClass:
            """Allow `match`."""
            return self.node_contents_visit(node)

        def visit_MatchMapping(self, node: ast.MatchMapping) -> ast.MatchMapping:
            """Allow `match`, and check the name a `**rest` pattern binds."""
            self.check_binding(node, node.rest)

            return self.node_contents_visit(node)

        def visit_MatchOr(self, node: ast.MatchOr) -> ast.MatchOr:
            """Allow `match`."""
            return self.node_contents_visit(node)

        def visit_MatchSingleton(self, node: ast.MatchSingleton) -> ast.MatchSingleton:
            """Allow `match`."""
            return self.node_contents_visit(node)

        def visit_MatchSequence(self, node: ast.MatchSequence) -> ast.MatchSequence:
            """Allow `match`."""
            return self.node_contents_visit(node)

        def visit_MatchStar(self, node: ast.MatchStar) -> ast.MatchStar:
            """Allow `match`, and check the name a `*rest` pattern binds."""
            self.check_binding(node, node.name)

            return self.node_contents_visit(node)

        def visit_MatchValue(self, node: ast.MatchValue) -> ast.MatchValue:
            """Allow `match`."""
            return self.node_contents_visit(node)

        def visit_match_case(self, node: ast.match_case) -> ast.match_case:
            """Allow `match`."""
            return self.node_contents_visit(node)

        def check_import_names(self, node: ast.ImportFrom | ast.Import) -> ast.AST:
            """Check the names being imported.

            This is a protection against rebinding dunder names like
            _getitem_, _write_ via imports.

            => 'from _a import x' is ok, because '_a' is not added to the scope.
            """
            if getattr(node, "is_lazy", 0):
                # PEP 810's `lazy import` resolves through the `__lazy_import__`
                # builtin at first use, so it never reaches the `__import__` the
                # scope replaces with `_safe_import` and the module policy goes
                # unconsulted.
                self.error(node, "Lazy import statements are not allowed.")

            module = node.module if isinstance(node, ast.ImportFrom) else None

            for name in node.names:
                if "*" in name.name and module and not _is_known_module(module):
                    self.error(node, '"*" imports are not allowed.')

                self.check_name(node, name.name)

                if name.asname:
                    self.check_name(node, name.asname)

                self.check_binding(node, name.asname or name.name.split(".")[0])

            return self.node_contents_visit(node)

        def check_binding(
            self,
            node: ast.AST,
            name: str | None,
            allow_double_underscore: bool = False,
        ) -> None:
            """Refuse binding a name the sandbox provides, or a double-underscore name.

            `__all__` binds freely; other double-underscore names bind only where
            `allow_double_underscore` says so.
            """
            if name is None:
                return

            if name in PROTECTED_SCOPE_NAMES:
                self.error(node, f'"{name}" is a reserved name.')
            elif name.startswith("__") and name != "__all__" and not allow_double_underscore:
                self.error(node, f"Assignments to '{name}' are not allowed.")

        def check_function_argument_names(
            self, node: ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda
        ) -> None:
            """Check argument names; a double-underscore argument is a local, so it binds."""
            super().check_function_argument_names(node)

            arguments = node.args

            for arg in (
                *arguments.posonlyargs,
                *arguments.args,
                *arguments.kwonlyargs,
                arguments.vararg,
                arguments.kwarg,
            ):
                if arg is not None:
                    self.check_binding(node, arg.arg, allow_double_underscore=True)

        def visit_Name(self, node: ast.Name) -> ast.AST | Iterable[ast.AST] | None:
            """Check names bound or deleted."""
            if isinstance(node.ctx, ast.Store | ast.Del):
                self.check_binding(node, node.id)

            return super().visit_Name(node)

        def visit_ExceptHandler(
            self, node: ast.ExceptHandler
        ) -> ast.AST | Iterable[ast.AST] | None:
            """Check the name an exception binds."""
            self.check_binding(node, node.name)

            return super().visit_ExceptHandler(node)

        def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST | Iterable[ast.AST] | None:
            """Check the function's name; a method may have a double-underscore name."""
            self.check_binding(node, node.name, allow_double_underscore=id(node) in self.method_ids)

            return super().visit_FunctionDef(node)

        def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST | Iterable[ast.AST] | None:
            """Check the class's name, and note its methods."""
            self.check_binding(node, node.name)
            self.method_ids.update(
                id(child) for child in node.body if isinstance(child, ast.FunctionDef)
            )

            return super().visit_ClassDef(node)

        def check_name(
            self,
            node: T_pos_ast,
            name: str | None,
            allow_magic_methods: bool = False,
        ) -> None:
            """Check names if they are allowed.

            If ``allow_magic_methods is True`` names in `ALLOWED_FUNC_NAMES`
            are additionally allowed although their names start with `_`.

            A leading underscore is a warning rather than an error, so plugins
            can use private names. The names reserved for the sandbox's policy
            hooks are the exception, and are rejected outright.
            """
            if name is None:
                return

            if name in PROTECTED_SCOPE_NAMES:
                self.error(node, f'"{name}" is a reserved name.')
            elif (
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
                    func=ast.Name("_write_", ast.Load()),
                    args=[
                        node.value,
                        ast.Constant(node_name(node.value)),
                        ast.Constant(node.attr),
                    ],
                    keywords=[],
                )

                copy_locations(new_value, node.value)
                node.value = new_value
                return node

            else:  # pragma: no cover
                # Impossible Case only ctx Load, Store and Del are defined in ast.
                raise NotImplementedError(f"Unknown ctx type: {type(node.ctx)}")

        def visit_Subscript(self, node: ast.Subscript) -> ast.AST:
            """Transforms all kinds of subscripts.

            'foo[bar]' becomes '_getitem_(foo, bar)'
            'foo[:ab]' becomes '_getitem_(foo, slice(None, ab, None))'
            'foo[ab:]' becomes '_getitem_(foo, slice(ab, None, None))'
            'foo[a:b]' becomes '_getitem_(foo, slice(a, b, None))'
            'foo[a:b:c]' becomes '_getitem_(foo, slice(a, b, c))'
            'foo[a, b:c] becomes '_getitem_(foo, (a, slice(b, c, None)))'
            'foo[a] = c' becomes '_write_(foo)[a] = c'
            'del foo[a]' becomes 'del _write_(foo)[a]'

            The _write_ function should return a security proxy.
            """
            node = self.node_contents_visit(node)

            # 'AugStore' and 'AugLoad' are defined in 'Python.asdl' as possible
            # 'expr_context'. However, according to Python/ast.c
            # they are NOT used by the implementation => No need to worry here.
            # Instead ast.c creates 'AugAssign' nodes, which can be visited.
            if isinstance(node.ctx, ast.Load):
                # `node.slice` is already a plain `ast.expr` on Python 3.9+
                # (we require >=3.11), so no `transform_slice` wrapper is
                # needed — RestrictedPython 8.2 removed the helper for the
                # same reason. See the upstream `visit_Subscript` for parity.
                new_node = ast.Call(
                    func=ast.Name("_getitem_", ast.Load()),
                    args=[node.value, node.slice],
                    keywords=[],
                )

                copy_locations(new_node, node)

                return new_node
            elif isinstance(node.ctx, ast.Del | ast.Store):
                new_value = ast.Call(
                    func=ast.Name("_write_", ast.Load()),
                    args=[
                        node.value,
                        ast.Constant(node_name(node.value)),
                        ast.Constant(node_name(node.slice)),
                        ast.Constant(True),
                    ],
                    keywords=[],
                )

                copy_locations(new_value, node)
                node.value = new_value

                return node
            else:  # pragma: no cover
                # Impossible Case only ctx Load, Store and Del are defined in ast.
                raise NotImplementedError(f"Unknown ctx type: {type(node.ctx)}")

    def __init__(
        self,
        source_code: Path,
        namespace: str,
        evaluated_modules: EvaluatedModules | None = None,
        mode: SandboxMode = SandboxMode.STRICT,
    ) -> None:
        self.namespace = namespace or "handlers"
        self.package_name = self.namespace.split(".")[0]
        self.mode = mode

        if not source_code.exists():
            raise FileNotFoundError(f"File not found: {source_code}")

        self.source_code_path = source_code.as_posix()
        self.source_code = source_code.read_text()
        package_path = _find_folder_in_path(source_code, self.package_name)
        self.base_path = package_path.parent if package_path else None
        self._evaluated_modules: EvaluatedModules = (
            evaluated_modules if evaluated_modules is not None else {}
        )

    @cached_property
    def scope(self) -> dict[str, Any]:
        """Return the scope used for evaluation."""
        return {
            "__builtins__": {
                **safe_builtins.copy(),
                **utility_builtins.copy(),
                **_BUILTIN_EXCEPTIONS,
                "__import__": self._safe_import,
                "all": builtins.all,
                "any": builtins.any,
                "ascii": builtins.ascii,
                "bytearray": builtins.bytearray,
                "classmethod": builtins.classmethod,
                "dict": builtins.dict,
                "dir": self._safe_dir,
                "enumerate": builtins.enumerate,
                "filter": builtins.filter,
                "format": builtins.format,
                "getattr": self._safe_getattr,
                "setattr": self._safe_setattr,
                "delattr": self._safe_delattr,
                "hasattr": builtins.hasattr,
                "iter": builtins.iter,
                "list": builtins.list,
                "map": builtins.map,
                "max": builtins.max,
                "memoryview": builtins.memoryview,
                "min": builtins.min,
                "next": builtins.next,
                "NotImplemented": builtins.NotImplemented,
                "type": _SafeType(self._safe_getattr),
                "property": builtins.property,
                "reversed": builtins.reversed,
                "staticmethod": builtins.staticmethod,
                "sum": builtins.sum,
                "super": builtins.super,
                "vars": self._safe_vars if self._strict else builtins.vars,
                "extract_exc_frames": _extract_exc_frames,
            },
            "__is_plugin__": True,
            "__metaclass__": type,
            "__name__": self.namespace,
            "_apply_": _apply,
            "_getattr_": self._safe_getattr,
            "_getitem_": _safe_getitem if self._strict else _legacy_safe_getitem,
            "_getiter_": _unrestricted,
            "_inplacevar_": _inplacevar,
            "_iter_unpack_sequence_": guarded_iter_unpack_sequence,
            "_print_": PrintCollector,
            "_unpack_sequence_": guarded_unpack_sequence,
            "_write_": self._safe_write,
        }

    @cached_property
    def _compiled(self) -> tuple[CompileResult, ImportedNames]:
        """Compile the source code into bytecode, and collect the names it imports.

        This mirrors `RestrictedPython.compile.compile_restricted_exec` but
        compiles with `dont_inherit=True`. RestrictedPython's own wrapper
        leaves that at the default, so plugin code inherits the `__future__`
        flags of whichever module calls `compile()` — and RestrictedPython's
        `compile` module uses `from __future__ import annotations`, which
        stringifies plugin annotations (PEP 563) and breaks `dataclass` and
        anything else that reads `__annotations__` at runtime.
        """
        errors: list[str] = []
        warnings: list[str] = []
        used_names: dict[str, bool] = {}
        no_imports: ImportedNames = {"names": [], "names_to_module": {}}

        try:
            parsed = ast.parse(self.source_code, self.source_code_path, "exec")
        except SyntaxError as error:
            errors.append(
                syntax_error_template.format(
                    lineno=error.lineno,
                    type=error.__class__.__name__,
                    msg=error.msg,
                    statement=error.text.strip() if error.text else None,
                )
            )
            return CompileResult(None, tuple(errors), warnings, used_names), no_imports
        except (TypeError, ValueError) as error:
            errors.append(str(error))
            return CompileResult(None, tuple(errors), warnings, used_names), no_imports

        transformer = self.Transformer(errors, warnings, used_names)
        transformer.visit(parsed)

        code = (
            None
            if errors
            else compile(parsed, self.source_code_path, mode="exec", dont_inherit=True)
        )

        return (
            CompileResult(code, tuple(errors), warnings, used_names),
            transformer.imported_names,
        )

    @property
    def compile_result(self) -> CompileResult:
        """Return the result of compiling the source code."""
        return self._compiled[0]

    @property
    def imported_names(self) -> ImportedNames:
        """Return the names imported by the source code."""
        return self._compiled[1]

    @property
    def errors(self) -> tuple[str, ...]:
        """Return errors encountered when compiling the source code."""
        return cast(tuple[str, ...], self.compile_result.errors)

    @property
    def warnings(self) -> tuple[str, ...]:
        """Return warnings encountered when compiling the source code."""
        return cast(tuple[str, ...], self.compile_result.warnings)

    @property
    def _strict(self) -> bool:
        """Whether this sandbox enforces the current rule set."""
        return self.mode is SandboxMode.STRICT

    def _model_registration(self) -> AbstractContextManager[None]:
        """Suppress Django model registration when a later real import will do it instead.

        Under `LEGACY_PERMISSIVE`, `__import__` re-executes a plugin's model module and
        that execution registers the canonical model classes; registering the sandbox's
        copies as well would leave two class objects per model. Under `STRICT` the module
        is only ever executed in the sandbox, so those classes are the canonical ones and
        have to register themselves.
        """
        return nullcontext() if self._strict else suppress_model_registration()

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
        # Skip modules already evaluated
        if not self._same_module(module_name) or module_name in self._evaluated_modules:
            return

        module = self._get_module(module_name)
        self._evaluate_implicit_imports(module)

        # Re-check after evaluating implicit imports to avoid duplicate evaluations.
        if module_name not in self._evaluated_modules:
            self._evaluated_modules[module_name] = True

            if self._execute_plugin_module(module_name, module):
                return

        if not self._strict and sys.modules.get(module_name):
            importlib.reload(sys.modules[module_name])

    def _execute_plugin_module(self, module_name: str, path: Path) -> bool:
        """Evaluate a plugin module in its own sandbox, publishing it when strict.

        Returns whether the module was published to `sys.modules`.
        """
        # Publish before executing, the way the real import system does, so that a
        # module importing its own package (`from pkg import sub` inside pkg/__init__.py)
        # resolves to the partially-initialized module instead of not being found.
        published = self._register_sandboxed_module(module_name, path, {}) if self._strict else None

        try:
            with self._model_registration():
                sandbox = Sandbox(
                    path,
                    namespace=module_name,
                    evaluated_modules=self._evaluated_modules,
                    mode=self.mode,
                )

                if published is None:
                    sandbox.execute()
                else:
                    # Run the body in the module's own namespace so each name is
                    # visible to a circular importer as soon as it is defined.
                    published.__dict__.update(sandbox.scope)
                    sandbox.execute(published.__dict__)
        except BaseException:
            # A module that failed to execute must not stay visible half-built, and must
            # not stay marked as evaluated: the next handler to import it would skip
            # evaluation and report that the module is missing rather than why it failed.
            self._evaluated_modules.pop(module_name, None)

            if published is not None:
                sys.modules.pop(module_name, None)

            raise

        return published is not None

    def _register_sandboxed_module(
        self,
        module_name: str,
        path: Path | None,
        scope: dict[str, Any],
    ) -> types.ModuleType:
        """Record a sandbox-evaluated plugin module in this load and publish it.

        Functions defined in the module keep the sandbox's `__builtins__` (and so its
        `_safe_import`) in their `__globals__`, so a deferred import inside a method
        resolves through the sandbox like a module-level one. Letting `importlib.reload`
        or `__import__` populate the entry instead replaces it with a copy executed
        outside the sandbox.

        The load's own registry is what its imports resolve against. `sys.modules` gets
        a copy for code that looks a module up by name, but a handler kept serving
        after a refused reload has lost those entries and still has to find its modules.
        """
        module = types.ModuleType(module_name)

        if path is not None:
            module.__file__ = str(path)

        module.__dict__.update(scope)
        module.__is_plugin__ = True  # type: ignore[attr-defined]
        self._evaluated_modules[module_name] = module
        sys.modules[module_name] = module

        # Mirror what the real import system does for a submodule: bind it as an
        # attribute of its parent package so that `a.b.c` resolves by attribute
        # walk, not by a fresh import from disk. Packages are evaluated leaf-first,
        # so link in both directions rather than assuming the parent exists yet.
        parent_name, _, leaf = module_name.rpartition(".")

        if parent_name and (parent := self._published(parent_name)) is not None:
            setattr(parent, leaf, module)

        prefix = f"{module_name}."

        for evaluated in self._evaluated_modules:
            if not evaluated.startswith(prefix) or "." in evaluated[len(prefix) :]:
                continue

            if (child := self._published(evaluated)) is not None:
                setattr(module, evaluated[len(prefix) :], child)

        return module

    def _published(self, module_name: str) -> types.ModuleType | None:
        """Return the module this load built for `module_name`, if it built one."""
        entry = self._evaluated_modules.get(module_name)

        return entry if isinstance(entry, types.ModuleType) else None

    def _evaluate_implicit_imports(self, module: Path) -> None:
        """Evaluate implicit imports in the sandbox."""
        parent = module.parent.parent if module.name == "__init__.py" else module.parent
        base_path = cast(Path, self.base_path)

        if not parent.is_relative_to(base_path) or parent == base_path:
            return

        module_name = parent.relative_to(base_path).as_posix().replace("/", ".")
        init_file = parent / "__init__.py"

        if module_name not in self._evaluated_modules:
            if init_file.exists():
                self._evaluated_modules[module_name] = True

                self._execute_plugin_module(module_name, init_file)
            else:
                self._evaluated_modules[module_name] = True

                # A package directory with no __init__.py still has to exist as a
                # module for the strict path, which resolves plugin imports by
                # attribute walk instead of deferring to the import system.
                if self._strict and self._published(module_name) is None:
                    self._register_sandboxed_module(module_name, None, {})

        self._evaluate_implicit_imports(parent)

    def _same_module(self, module: str) -> bool:
        """
        Return True if `module` is within the plugin code.
        """
        return bool(self.base_path) and module.split(".")[0] == self.package_name

    def _safe_write(
        self,
        _ob: Any,
        name: str | None = None,
        attribute: str | int | None = None,
        item: bool = False,
    ) -> Any:
        """Check if the given obj belongs to a protected resource.

        `item` marks a subscript write (`obj[key] = value`), where `attribute` is the name of
        the key expression rather than an attribute of `obj`.
        """
        is_module = isinstance(_ob, types.ModuleType)

        if is_module:
            if not self._same_module(_ob.__name__):
                raise AttributeError(f"Forbidden assignment to a module attribute: {_ob.__name__}.")
        elif isinstance(_ob, type):
            full_name = f"{_ob.__module__}.{_ob.__qualname__}"
            module_name = _ob.__module__
        else:
            full_name = f"{_ob.__class__.__module__}.{_ob.__class__.__qualname__}"
            module_name = _ob.__class__.__module__

        if attribute is not None:
            if isinstance(_ob, dict):
                value = dict.get(_ob, attribute)
            elif isinstance(_ob, list | tuple) and isinstance(attribute, int):
                value = _ob.__getitem__(attribute)
            elif item and isinstance(_ob, list | tuple):
                # The key expression's name says nothing about the list's attributes.
                value = None
            elif isinstance(attribute, str):
                value = getattr(_ob, attribute, None)
            else:
                value = None
        else:
            value = None

        if not self._same_module(module_name) and (
            # deny if it was anything imported
            (name and name.split(".")[0] in self.imported_names["names"])
            # deny writes to an outside class through any name, as setattr does
            or isinstance(_ob, type)
            # deny if it's anything callable
            or callable(value)
            # deny writes to dictionary underscore keys; the strict path exempts
            # every dict, whose keys are the plugin's data rather than a foreign
            # object's namespace
            or (
                isinstance(_ob, dict)
                and isinstance(attribute, str)
                and attribute.startswith("_")
                and not self._strict
            )
        ):
            # Deprecated: allow plugins to override _MAX_REQUEST_TIMEOUT_SECONDS on
            # Http instances. This will be removed in a future release.
            if attribute == "_MAX_REQUEST_TIMEOUT_SECONDS" and self._is_http_instance(_ob):
                logger.warning(
                    "Plugin '%s' is overriding %s._MAX_REQUEST_TIMEOUT_SECONDS. "
                    "This is deprecated and will be forbidden in a future release. "
                    "Use the timeout parameter on individual requests instead.",
                    self.package_name,
                    type(_ob).__name__,
                )
                return _ob

            raise AttributeError(
                f"Forbidden assignment to a non-module attribute: {full_name} "
                f"at {name}.{attribute}."
            )

        return _ob

    @staticmethod
    def _is_http_instance(_ob: Any) -> bool:
        """Check if _ob is an SDK HTTP client: an `Http` or a `ServiceClient`."""
        from canvas_sdk.utils.http import Http, ServiceClient

        return isinstance(_ob, Http | ServiceClient)

    def _safe_vars(self, obj: Any = None) -> Any:
        """Restricted vars() that filters private attributes on external objects."""
        if obj is None:
            raise TypeError("vars() requires an argument in sandboxed code")

        if isinstance(obj, types.ModuleType):
            module = obj.__name__
        elif isinstance(obj, type):
            module = obj.__module__
        else:
            module = obj.__class__.__module__

        raw = builtins.vars(obj)

        # A class's namespace is a mappingproxy rather than a dict, so check for any
        # mapping, not only dicts.
        if not self._same_module(module) and isinstance(raw, Mapping):
            return self._external_namespace(obj, raw)

        return raw

    def _external_namespace(self, obj: Any, raw: Mapping[str, Any]) -> dict[str, Any]:
        """Return the part of an outside object's namespace plugin code may see.

        The same names `getattr` would allow, as a copy: for a module, the names its
        allowlist entry grants (all public names if this plugin is blessed for it); for an
        object declaring `__exports__`, those names; otherwise the public names.
        """
        namespace = _public_attributes(dict(raw))

        if isinstance(obj, types.ModuleType):
            if self._is_blessed_import(obj.__name__):
                return namespace

            allowed = ALLOWED_MODULES.get(obj.__name__, frozenset())

            return {key: value for key, value in namespace.items() if key in allowed}

        exports = getattr(obj, "__exports__", None)

        if exports:
            return {key: value for key, value in namespace.items() if key in exports}

        return namespace

    def _safe_getattr(self, _ob: Any, name: Any, default: Any = _NO_DEFAULT) -> Any:
        """
        Prevent access to several classes of attributes.

        Restricted attribute types:

        1. underscored attributes created outside of the defining namespace
        2. attributes used by the `inspect` module except those that we have safely wrapped
        3. dunder methods except for those we deem safe
        4. if a __exports__ module property is defined, any
           attribute not in that property's value
        """
        is_module = isinstance(_ob, types.ModuleType)

        if is_module:
            module = _ob.__name__
        elif isinstance(_ob, type):
            module = _ob.__module__.split(".")[0]
        elif (bound_class := getattr(_ob, "__self_class__", None)) is not None and isinstance(
            _ob, super
        ):
            # super() resolves attributes on the instance it is bound to, so it is held to
            # the same rules as that instance's class.
            module = bound_class.__module__.split(".")[0]
        else:
            module = _ob.__class__.__module__.split(".")[0]

        if type(name) is not str:
            raise TypeError("type(name) must be str")

        if name in ("format", "format_map"):
            if isinstance(_ob, type) and issubclass(_ob, str):
                # `str.format(template, ...)` reaches the real method through the type,
                # so there is no instance to bind a safe formatter to.
                raise NotImplementedError(
                    "Calling format through the `str` type is not allowed; "
                    "call it on the string itself."
                )

            if isinstance(_ob, str):
                return _safe_format(_ob) if name == "format" else _safe_format_map(_ob)

        # A class's ancestry is readable by name only.
        if name == "__mro__" and isinstance(_ob, type | _SafeClass):
            return (_SafeClass.of(_ob) if isinstance(_ob, type) else _ob).__mro__

        # Objects with __exports__ define their own allowlist — check it first
        # so that safe wrapper types (e.g. _SafeTraceback, _SafeFrame) can
        # expose attributes like tb_frame/f_code that are in INSPECT_ATTRIBUTES.
        exports = getattr(_ob, "__exports__", None)

        if exports:
            if name not in exports:
                raise AttributeError(f'"{name}" is an invalid attribute name (not in __exports__)')
            return _getattr_or_default(_ob, name, default, self.package_name)

        if name in INSPECT_ATTRIBUTES:
            raise AttributeError(f'"{name}" is a restricted name.')

        # Method names the sandbox does not expose
        if self._strict and name in RESTRICTED_METHOD_NAMES:
            raise AttributeError(f'"{name}" is a restricted method name.')

        # Code defined in the Sandbox namespace can access its own underscore variables
        if name.startswith("_"):
            if self._same_module(module):
                if name.startswith("__") and name not in SAFE_INTERNAL_DUNDER_READ_ATTRIBUTES:
                    raise AttributeError(
                        f'"{name}" is an invalid attribute name because it starts with "_"'
                    )
            else:
                # An SDK model's metadata is readable as a field-introspection view.
                if name == "_meta" and _is_model_options(raw_meta := getattr(_ob, "_meta", None)):
                    return _SafeModelMeta(raw_meta)

                # Nothing can read dunder attributes except those on our safe list
                if (
                    name not in SAFE_EXTERNAL_DUNDER_READ_ATTRIBUTES
                    and not _is_readable_sdk_private(_ob, name)
                ):
                    raise AttributeError(
                        f'"{name}" is an invalid attribute name because it starts with "__"'
                    )
        elif (
            is_module
            and not self._same_module(module)
            and (module not in ALLOWED_MODULES or name not in ALLOWED_MODULES[module])
            and not self._is_blessed_import(module)
        ):
            raise AttributeError(
                f'"{module}.{name}" is an invalid attribute name (not in ALLOWED_MODULES)'
            )

        # Prevent sandbox escape via __class__.__mro__, __subclasses__, etc.
        if isinstance(_ob, _SafeClass) and name != "__name__":
            raise AttributeError(f'Access to "{name}" on external __class__ is restricted')

        # The class of a class is a metaclass, which builds new classes when called.
        if name == "__class__" and (isinstance(_ob, type) or not self._same_module(module)):
            return _SafeClass.of(_ob.__class__)

        if name == "__traceback__":
            tb = getattr(_ob, "__traceback__", None)
            return _SafeTraceback(tb) if tb is not None else None

        if self._strict and name == "__dict__" and not self._same_module(module):
            raw = _getattr_or_default(_ob, name, default, self.package_name)
            if isinstance(raw, Mapping):
                return self._external_namespace(_ob, raw)
            return raw

        return _getattr_or_default(_ob, name, default, self.package_name)

    def _is_blessed_import(self, module: str) -> bool:
        """Whether this plugin is named as permitted to use this module.

        Consulted only once a module has been rejected, so a plugin that imports nothing
        unusual never reaches it.
        """
        return is_blessed_import(self.package_name, module)

    def _resolve_relative_import(self, name: str, level: int) -> str:
        """Return the absolute module name a relative import refers to.

        `from .sibling import x` arrives here as the bare name `sibling`, which matches
        neither the plugin's own package nor `ALLOWED_MODULES`. Resolving it against the
        importing module's package first is what lets the checks below see it for what it
        is: a module inside the plugin.
        """
        package = self.namespace

        if not self.source_code_path.endswith("__init__.py"):
            package = package.rpartition(".")[0]

        parts = package.split(".") if package else []

        if level > 1:
            parts = parts[: -(level - 1)]

        if not parts:
            raise ImportError(f"attempted relative import beyond top-level package: {name!r}")

        base = ".".join(parts)

        return f"{base}.{name}" if name else base

    def _safe_setattr(self, ob: Any, name: Any, value: Any) -> None:
        """`setattr`, allowed exactly where `ob.name = value` is."""
        builtins.setattr(self._writable(ob, name), name, value)

    def _safe_delattr(self, ob: Any, name: Any) -> None:
        """`delattr`, allowed exactly where `del ob.name` is."""
        builtins.delattr(self._writable(ob, name), name)

    def _writable(self, ob: Any, name: Any) -> Any:
        """`ob`, once the attribute write guard accepts writing `name` on it.

        Attribute syntax also refuses a write through a name the plugin imported, such as
        `Patient.x = 1`. setattr has no name to check, so a private name on any object the
        plugin did not define is refused outright. Both refuse any class from outside the
        plugin, whatever name reaches it.
        """
        if not isinstance(name, str):
            raise TypeError("attribute name must be a string")

        if name.startswith("__"):
            raise AttributeError(
                f'"{name}" is an invalid attribute name because it starts with "__"'
            )

        owner = ob.__module__ if isinstance(ob, type) else type(ob).__module__
        own = self._same_module(owner)

        if isinstance(ob, type) and not own:
            raise AttributeError(f"Forbidden assignment to an attribute of {ob.__name__}.")

        if name.startswith("_") and not own:
            raise AttributeError(
                f'"{name}" is an invalid attribute name because it starts with "_"'
            )

        return self._safe_write(ob, None, name)

    def _safe_dir(self, *args: Any) -> list[str]:
        """The names `dir()` lists, narrowed to the ones plugin code can read.

        Names only, and none of them are read while building the list.
        """
        if len(args) != 1:
            raise TypeError("dir() takes exactly one argument in plugin code")

        (ob,) = args

        if exports := getattr(ob, "__exports__", None):
            return sorted(exports)

        names = [
            name
            for name in builtins.dir(ob)
            if not name.startswith("_")
            and name not in INSPECT_ATTRIBUTES
            and not (self._strict and name in RESTRICTED_METHOD_NAMES)
        ]

        if isinstance(ob, types.ModuleType) and not (
            self._same_module(ob.__name__) or self._is_blessed_import(ob.__name__)
        ):
            allowed = ALLOWED_MODULES.get(ob.__name__, set())
            names = [name for name in names if name in allowed]

        return names

    def _safe_import(
        self,
        name: str,
        globals: Any = None,
        locals: Any = None,
        fromlist: Sequence[str] = (),
        level: int = 0,
    ) -> Any:
        if level:
            name = self._resolve_relative_import(name, level)
            level = 0

        if not self._same_module(name) and not self._is_blessed_import(name):
            # Disallow importing anything not explicitly allowed by ALLOWED_MODULES
            if name not in ALLOWED_MODULES:
                raise ImportError(f"{name!r} is not an allowed import.")

            if fromlist is not None:
                for item in fromlist:
                    if item not in ALLOWED_MODULES.get(name, set()):
                        raise ImportError(f"{item!r} is not an allowed import from {name!r}.")

        # evaluate the module in the sandbox if needed
        self._evaluate_module(name)

        # Resolve plugin-owned imports from the sandbox's own module registry.
        # `__import__` would execute the file from disk outside the sandbox and cache
        # that copy in sys.modules — for the parent packages of a dotted name as well
        # as the leaf — leaving the sandboxed evaluation unused.
        if self._strict and self._same_module(name):
            return self._import_sandboxed_module(name, fromlist)

        imported_module = __import__(name, globals, locals, fromlist, level)

        # If the module is part of the plugin, mark it as a plugin module
        if self._same_module(name):
            imported_module.__is_plugin__ = True  # type: ignore[attr-defined]

        return imported_module

    def _import_sandboxed_module(self, name: str, fromlist: Sequence[str]) -> types.ModuleType:
        """Resolve a plugin-owned import from sandbox-evaluated modules only.

        Reproduces the binding `__import__` would return — the named module when there
        is a `fromlist`, otherwise the root package — without handing any plugin file to
        the real import system.
        """
        module = self._published(name)

        if module is None:
            raise ImportError(f"{name!r} could not be resolved inside the sandbox.")

        if not fromlist:
            # `import a.b.c` binds the root package; the attribute walk to `c` works
            # because each package was linked to its children at registration.
            root_name = name.split(".")[0]
            root = self._published(root_name)

            if root is None:
                raise ImportError(f"{root_name!r} could not be resolved inside the sandbox.")

            return root

        # `from a.b import c` where `c` is a submodule rather than an attribute:
        # evaluate it too, so the caller finds it bound on the parent. A name that is
        # not a module on disk is an attribute — a class or constant — and is left to
        # the caller's `from` binding, which reports a missing one as an ImportError.
        # It reaches here with `hasattr` false whenever `a.b` is still initializing.
        for item in fromlist:
            if hasattr(module, item):
                continue

            submodule_name = f"{name}.{item}"

            if not self._get_module(submodule_name).exists():
                continue

            self._evaluate_module(submodule_name)

            if (submodule := self._published(submodule_name)) is not None:
                setattr(module, item, submodule)

        return module

    def execute(self, globals: dict[str, Any] | None = None) -> dict:
        """Execute the given code in a restricted sandbox.

        `globals` runs the module body in an existing namespace instead of this
        sandbox's own scope, so that a module's names become visible as they are
        defined rather than only once the body finishes.
        """
        code = self.compile_result.code

        if self.errors or code is None:
            raise RuntimeError(f"Code is invalid: {self.errors}")

        namespace = self.scope if globals is None else globals

        exec(code, namespace)

        return namespace


def sandbox_from_module(
    base_path: Path,
    module_name: str,
    evaluated_modules: EvaluatedModules | None = None,
    mode: SandboxMode = SandboxMode.STRICT,
) -> Sandbox:
    """Sandbox the code execution."""
    module_path = base_path / str(module_name.replace(".", "/") + ".py")

    if not module_path.exists():
        raise ModuleNotFoundError(f'Could not load module "{module_name}"')

    sandbox = Sandbox(
        module_path,
        namespace=module_name,
        evaluated_modules=evaluated_modules,
        mode=mode,
    )

    return sandbox
