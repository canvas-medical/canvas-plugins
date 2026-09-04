import __future__
import builtins
import importlib
import logging
import re
import sys
import types
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from tempfile import mkdtemp
from textwrap import dedent
from unittest.mock import MagicMock, patch

import pytest
import requests
from django.db import models as django_models
from RestrictedPython import compile_restricted_exec

import plugin_runner.sandbox as sandbox_module
from canvas_sdk.tests.shared import params_from_dict
from canvas_sdk.utils.http import ontologies_http
from canvas_sdk.v1.data.base import (
    MAX_FIELD_SIZE,
    BulkOperationTooLarge,
    CustomModel,
    FieldValueTooLarge,
    NamespaceWriteDenied,
)
from canvas_sdk.v1.plugin_database_context import plugin_database_context
from plugin_runner.generate_allowed_imports import CANVAS_TOP_LEVEL_MODULES, find_submodules
from plugin_runner.sandbox import (
    ALLOWED_MODULES,
    PROTECTED_SCOPE_NAMES,
    EvaluatedModules,
    Sandbox,
    SandboxMode,
    collect_missing_attribute_reads,
    sandbox_from_module,
)
from settings import CUSTOMER_IDENTIFIER

CANVAS_SUBMODULE_NAMES = [
    found_module
    for found_module in find_submodules(CANVAS_TOP_LEVEL_MODULES)
    # tests are excluded from the built and distributed module in pyproject.toml
    if "tests" not in found_module and "test_" not in found_module
]


def _sandbox_from_code(
    source_code: str,
    module_name: str = "plugin_name.handlers.handler",
    extra_source_code: str | None = None,
    extra_module_name: str | None = None,
) -> Sandbox:
    """
    Helper method to ceate a Sandbox that matches production conditions.
    """
    temp_directory = Path(mkdtemp())

    plugin_directory = temp_directory.joinpath(*module_name.split(".")[:-1])
    plugin_directory.mkdir(parents=True)

    init_file = plugin_directory / "__init__.py"
    init_file.touch()

    protocol_file = plugin_directory / (module_name.split(".")[-1] + ".py")
    protocol_file.write_text(dedent(source_code))

    if extra_source_code and extra_module_name:
        extra_plugin_directory = temp_directory.joinpath(*extra_module_name.split(".")[:-1])
        extra_plugin_directory.mkdir(parents=True, exist_ok=True)

        extra_init_file = extra_plugin_directory / "__init__.py"
        extra_init_file.touch()

        extra_protocol_file = extra_plugin_directory / (extra_module_name.split(".")[-1] + ".py")
        extra_protocol_file.write_text(dedent(extra_source_code))

    return sandbox_from_module(temp_directory, module_name)


# Sample code strings for testing various scenarios
VALID_CODE = """
    x = 10
    y = 20
    result = x + y
"""


def test_valid_code_execution() -> None:
    """Test execution of valid code in the sandbox."""
    sandbox = _sandbox_from_code(VALID_CODE)
    scope = sandbox.execute()
    assert scope["result"] == 30, "The code should compute result as 30."


def test_an_attribute_that_raises_attribute_error_raises_in_the_sandbox() -> None:
    """Reading an attribute behaves as it does in Python: an AttributeError propagates.

    Django signals a missing related object this way (RelatedObjectDoesNotExist is an
    AttributeError), and plugins catch it to branch on the missing relation.
    """
    sandbox = _sandbox_from_code(
        """
        class Missing(AttributeError):
            pass

        class Thing:
            @property
            def related(self):
                raise Missing("no related object")

        try:
            Thing().related
            result = "no exception"
        except Missing:
            result = "caught"
        """
    )

    assert sandbox.execute()["result"] == "caught"


def test_a_name_an_object_does_not_define_reads_as_none() -> None:
    """Reading an attribute nothing defines gives None, as the sandbox always has, so a
    plugin that names a member its SDK version lacks still loads.
    """
    sandbox = _sandbox_from_code(
        """
        from canvas_sdk.v1.data.appointment import AppointmentProgressStatus

        class Thing:
            pass

        result = (AppointmentProgressStatus.NOT_A_MEMBER, Thing().missing)
        """
    )

    assert sandbox.execute()["result"] == (None, None)


def test_a_name_that_does_not_exist_is_logged_once_and_collected(
    caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Each missing name a plugin reads is logged once per plugin, and collected for
    `canvas validate` while it loads.
    """
    monkeypatch.setattr(sandbox_module, "_logged_missing_attributes", {})
    sandbox = _sandbox_from_code(
        """
        class Thing:
            pass

        first = Thing().missing
        second = Thing().missing
        """
    )

    with (
        caplog.at_level(logging.WARNING, logger="plugin_runner_logger"),
        collect_missing_attribute_reads() as reads,
    ):
        sandbox.execute()

    assert reads == ["Thing.missing"]
    warnings = [r.getMessage() for r in caplog.records if "Thing.missing" in r.getMessage()]
    assert len(warnings) == 1
    assert "plugin_name" in warnings[0]


def test_the_missing_name_log_keeps_a_bounded_number_of_names_per_plugin(
    caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    """However many distinct missing names a plugin reads, only the first few hundred are
    remembered and logged.
    """
    logged: dict[str, set[str]] = {}
    monkeypatch.setattr(sandbox_module, "_logged_missing_attributes", logged)
    sandbox = _sandbox_from_code(
        """
        class Thing:
            pass

        thing = Thing()
        for i in range(5000):
            getattr(thing, "n" + str(i))
        """
    )

    with caplog.at_level(logging.WARNING, logger="plugin_runner_logger"):
        sandbox.execute()

    remembered = sum(len(names) for names in logged.values())
    warnings = [r for r in caplog.records if "which does not exist" in r.getMessage()]
    assert 0 < remembered <= 500
    assert len(warnings) == remembered


def test_a_long_missing_name_is_truncated_in_the_log_and_validate_list(
    caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A missing name is logged and collected cut to about 100 characters."""
    logged: dict[str, set[str]] = {}
    monkeypatch.setattr(sandbox_module, "_logged_missing_attributes", logged)
    sandbox = _sandbox_from_code(
        """
        class Thing:
            pass

        getattr(Thing(), "a" * 100000)
        """
    )

    with (
        caplog.at_level(logging.WARNING, logger="plugin_runner_logger"),
        collect_missing_attribute_reads() as reads,
    ):
        sandbox.execute()

    assert len(reads) == 1
    assert reads[0].startswith("Thing.aaa")
    assert len(reads[0]) <= 110
    assert all(len(name) <= 110 for names in logged.values() for name in names)
    warnings = [r.getMessage() for r in caplog.records if "which does not exist" in r.getMessage()]
    assert len(warnings) == 1
    assert len(warnings[0]) < 400


def test_a_missing_name_is_logged_with_control_characters_escaped(
    caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Newlines and escape codes in a missing name are logged escaped, on one line."""
    monkeypatch.setattr(sandbox_module, "_logged_missing_attributes", {})
    sandbox = _sandbox_from_code(
        """
        class Thing:
            pass

        getattr(Thing(), "first\\nsecond\\x1b[31m")
        """
    )

    with caplog.at_level(logging.WARNING, logger="plugin_runner_logger"):
        sandbox.execute()

    warnings = [r.getMessage() for r in caplog.records if "which does not exist" in r.getMessage()]
    assert len(warnings) == 1
    assert "\n" not in warnings[0]
    assert "\x1b" not in warnings[0]
    assert "first\\nsecond\\x1b[31m" in warnings[0]


def test_a_dataclass_compares_unequal_to_another_type() -> None:
    """A dataclass's generated __eq__ returns NotImplemented for other types, including
    when the dataclass is defined in another module of the plugin.
    """
    sandbox = _sandbox_from_code(
        """
        from plugin_name.structures import Row

        result = None in [Row("a")]
        """,
        extra_source_code="""
        from dataclasses import dataclass

        @dataclass
        class Row:
            key: str
        """,
        extra_module_name="plugin_name.structures",
    )

    assert sandbox.execute()["result"] is False


def test_bytearray_and_format_are_available() -> None:
    """The bytearray and format builtins work as in Python."""
    sandbox = _sandbox_from_code(
        """
        data = bytearray(b"ab")
        data.append(99)
        result = (bytes(data), format(3.14159, ".2f"))
        """
    )

    assert sandbox.execute()["result"] == (b"abc", "3.14")


@pytest.mark.parametrize(
    "exception",
    sorted(
        name
        for name, value in vars(builtins).items()
        if not name.startswith("_") and isinstance(value, type) and issubclass(value, BaseException)
    ),
)
def test_every_builtin_exception_class_is_available(exception: str) -> None:
    """An except clause naming any builtin exception works, so an unrelated error passing
    through it stays that error.
    """
    sandbox = _sandbox_from_code(
        f"""
        try:
            raise KeyError("k")
        except {exception}:
            result = "caught"
        except KeyError:
            result = "passed through"
        """
    )

    expected = "caught" if issubclass(KeyError, getattr(builtins, exception)) else "passed through"

    assert sandbox.execute()["result"] == expected


def test_type_of_an_object_matches_its_class() -> None:
    """type(x) returns what x.__class__ returns: the class itself for the plugin's own
    objects, and a proxy carrying only the name for anything else.
    """
    sandbox = _sandbox_from_code(
        """
        class Thing:
            pass

        try:
            raise ValueError("x")
        except ValueError as error:
            error_name = type(error).__name__

        result = (error_name, type(Thing()) is Thing, type({}).__name__)
        """
    )

    assert sandbox.execute()["result"] == ("ValueError", True, "dict")


def test_setattr_and_delattr_work_like_attribute_syntax() -> None:
    """setattr() and delattr() do what `obj.name = value` and `del obj.name` do."""
    sandbox = _sandbox_from_code(
        """
        from canvas_sdk.commands import LabOrderCommand

        class Job:
            pass

        job = Job()
        setattr(job, "status", "done")
        status = job.status
        delattr(job, "status")

        command = LabOrderCommand()
        setattr(command, "comment", "fasting")

        result = (status, hasattr(job, "status"), command.comment)
        """
    )

    assert sandbox.execute()["result"] == ("done", False, "fasting")


@pytest.mark.parametrize(
    "code",
    [
        'setattr(Thing(), "__class__", Other)',
        'delattr(Thing, "__init__")',
        "setattr(Thing(), 3, 1)",
        'setattr(re, "compile", None)',
        'setattr(Patient, "objects", None)',
        'setattr(LabOrderCommand(), "originate", None)',
    ],
)
def test_setattr_and_delattr_refuse_what_attribute_syntax_refuses(code: str) -> None:
    """Dunder names, non-string names, module attributes, classes the plugin imported and
    methods of objects it did not define stay out of reach.
    """
    sandbox = _sandbox_from_code(
        f"""
        import re

        from canvas_sdk.commands import LabOrderCommand
        from canvas_sdk.v1.data import Patient

        class Thing:
            pass

        class Other:
            pass

        {code}
        """
    )

    with pytest.raises((AttributeError, TypeError)):
        sandbox.execute()


@pytest.mark.parametrize(
    "setup",
    [
        "from collections import defaultdict\nd = defaultdict(int)\n",
        "from collections import Counter\nd = Counter()\n",
        "from collections import OrderedDict\nd = OrderedDict()\n",
        "class Bag(dict):\n    pass\nd = Bag()\n",
    ],
    ids=["defaultdict", "Counter", "OrderedDict", "own dict subclass"],
)
def test_underscore_keys_work_on_any_dict(setup: str) -> None:
    """A mapping's keys are the plugin's data, so underscore keys work on every dict."""
    sandbox = _sandbox_from_code(setup + 'd["_k"] = 1\nresult = d["_k"]\n')

    assert sandbox.execute()["result"] == 1


def test_type_tests_whether_a_value_is_a_class() -> None:
    """isinstance(x, type) and issubclass(x, type) answer as in Python."""
    sandbox = _sandbox_from_code(
        """
        class Thing:
            pass

        result = (
            isinstance(Thing, type),
            isinstance(Thing(), type),
            isinstance(5, (str, type)),
            issubclass(Thing, type),
        )
        """
    )

    assert sandbox.execute()["result"] == (True, False, False, False)


@pytest.mark.parametrize(
    "code",
    [
        'type("Made", (), {})',
        "type(Thing)",
        "Thing.__class__",
        "__metaclass__",
        "type._class_of",
        "type.__call__",
    ],
)
def test_plugin_code_cannot_reach_the_type_constructor(code: str) -> None:
    """Neither the three-argument form, the class of a class, nor the metaclass the sandbox
    gives class statements lets plugin code build new types.
    """
    sandbox = _sandbox_from_code(
        f"""
        class Thing:
            pass

        made = {code}
        made("Made", (Thing,), {{}})
        """
    )

    with pytest.raises((AttributeError, RuntimeError, TypeError)):
        sandbox.execute()


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("client._base_url", f"https://fumage-{CUSTOMER_IDENTIFIER}.canvasmedical.com"),
        ('client._get_headers()["Authorization"]', "Bearer test_token"),
        ("client.base_url", f"https://fumage-{CUSTOMER_IDENTIFIER}.canvasmedical.com"),
        ('client.get_headers()["Authorization"]', "Bearer test_token"),
    ],
)
def test_fhir_client_url_and_headers_are_readable(expression: str, expected: str) -> None:
    """Plugins build their own FHIR requests from the client's URL and headers."""
    sandbox = _sandbox_from_code(
        f"""
        from canvas_sdk.clients.canvas_fhir import CanvasFhir

        client = CanvasFhir("id", "secret")
        result = {expression}
        """
    )

    with patch(
        "canvas_sdk.clients.canvas_fhir.client.CanvasFhir._get_credentials",
        return_value={"access_token": "test_token"},
    ):
        assert sandbox.execute()["result"] == expected


@pytest.mark.parametrize("name", ["_credentials", "_client_secret", "_get_credentials"])
def test_other_fhir_client_private_names_stay_refused(name: str) -> None:
    """Only the URL and headers are readable on the FHIR client."""
    sandbox = _sandbox_from_code(
        f"""
        from canvas_sdk.clients.canvas_fhir import CanvasFhir

        client = CanvasFhir("id", "secret")
        result = client.{name}
        """
    )

    with (
        patch(
            "canvas_sdk.clients.canvas_fhir.client.CanvasFhir._get_credentials",
            return_value={"access_token": "test_token"},
        ),
        pytest.raises(AttributeError, match="invalid attribute name"),
    ):
        sandbox.execute()


def test_dir_of_a_module_lists_the_names_plugin_code_can_read() -> None:
    """dir() of a module lists exactly the names the sandbox lets plugin code read on it."""
    sandbox = _sandbox_from_code(
        """
        import re

        import canvas_sdk.commands as commands

        command_names = dir(commands)
        re_names = dir(re)
        """
    )

    scope = sandbox.execute()

    assert "PrescribeCommand" in scope["command_names"]
    assert not [name for name in scope["command_names"] if name.startswith("_")]
    assert set(scope["re_names"]) == set(sandbox_module.ALLOWED_MODULES["re"]) & set(dir(re))


def test_dir_of_an_object_lists_only_public_names() -> None:
    """dir() of an object lists its names without a leading underscore."""
    sandbox = _sandbox_from_code(
        """
        class Thing:
            def __init__(self):
                self.visible = 1
                self._hidden = 2

        result = dir(Thing())
        """
    )

    assert sandbox.execute()["result"] == ["visible"]


def test_dir_of_a_wrapped_object_lists_its_exports() -> None:
    """dir() of an object the sandbox wraps lists only what the wrapper exports."""
    sandbox = _sandbox_from_code(
        """
        try:
            raise ValueError("x")
        except ValueError as error:
            result = dir(error.__traceback__)
        """
    )

    assert sandbox.execute()["result"] == ["tb_frame", "tb_lineno", "tb_next"]


def test_dir_needs_an_argument() -> None:
    """dir() with no argument would list the caller's scope, which plugin code cannot ask for."""
    sandbox = _sandbox_from_code("result = dir()")

    with pytest.raises(TypeError):
        sandbox.execute()


def test_class_ancestry_is_readable_by_name() -> None:
    """__mro__ lists a class's ancestors by name, for the plugin's own classes and others."""
    sandbox = _sandbox_from_code(
        """
        class Thing(ValueError):
            pass

        try:
            raise KeyError("k")
        except KeyError as error:
            caught = [klass.__name__ for klass in type(error).__mro__]
            via_class = [klass.__name__ for klass in error.__class__.__mro__]

        own = [klass.__name__ for klass in Thing.__mro__]
        """
    )

    scope = sandbox.execute()

    assert scope["caught"] == ["KeyError", "LookupError", "Exception", "BaseException", "object"]
    assert scope["via_class"] == scope["caught"]
    assert scope["own"] == ["Thing", "ValueError", "Exception", "BaseException", "object"]


@pytest.mark.parametrize("attribute", ["__subclasses__", "__dict__", "__init__"])
def test_ancestors_in_mro_expose_only_their_names(attribute: str) -> None:
    """Every class __mro__ hands back is a proxy carrying only its name."""
    sandbox = _sandbox_from_code(
        f"""
        class Thing:
            pass

        Thing.__mro__[-1].{attribute}
        """
    )

    with pytest.raises(AttributeError):
        sandbox.execute()


def test_docstrings_are_readable_and_copyable() -> None:
    """A decorator can copy the docstring of the function it wraps."""
    sandbox = _sandbox_from_code(
        """
        def method():
            '''Does a thing.'''

        def wrapper():
            pass

        wrapper.__doc__ = method.__doc__
        result = (wrapper.__doc__, ValueError.__doc__ is not None)
        """
    )

    assert sandbox.execute()["result"] == ("Does a thing.", True)


def test_statistics_median_is_importable() -> None:
    """Plugin code can import median from statistics."""
    sandbox = _sandbox_from_code(
        """
        from statistics import median

        result = median([3, 1, 2])
        """
    )

    assert sandbox.execute()["result"] == 2


def test_other_statistics_names_are_refused() -> None:
    """The only name plugin code can import from statistics is median."""
    sandbox = _sandbox_from_code("from statistics import mean")

    with pytest.raises(ImportError):
        sandbox.execute()


def test_ascii_is_available() -> None:
    """The ascii builtin works as in Python."""
    sandbox = _sandbox_from_code('result = ascii("café")')

    assert sandbox.execute()["result"] == "'caf\\xe9'"


def test_memoryview_is_available() -> None:
    """The memoryview builtin works as in Python."""
    sandbox = _sandbox_from_code(
        """
        view = memoryview(b"abc")
        result = (isinstance(view, memoryview), view[1:].tobytes(), view.readonly)
        """
    )

    assert sandbox.execute()["result"] == (True, b"bc", True)


def test_a_traceback_frame_reports_its_line_number() -> None:
    """Error reporting can read the line a frame was executing."""
    sandbox = _sandbox_from_code(
        """
        try:
            raise ValueError("boom")
        except ValueError as error:
            traceback = error.__traceback__
            result = (traceback.tb_lineno, traceback.tb_frame.f_lineno)
        """
    )

    # The traceback records the raising line; the frame reports the line it was on when
    # the traceback was read.
    assert sandbox.execute()["result"] == (3, 5)


def test_numbers_support_floor_ceil_trunc_and_round_methods() -> None:
    """The rounding methods on numbers work as in Python."""
    sandbox = _sandbox_from_code(
        """
        value = 2.5
        result = (value.__floor__(), value.__ceil__(), value.__trunc__(), value.__round__())
        """
    )

    assert sandbox.execute()["result"] == (2, 3, 2, 2)


def test_every_allowed_submodule_lists_its_own_names() -> None:
    """A granted name that is itself a module needs its own entry, or nothing inside it
    can be used.
    """
    missing = []

    for module_name, names in ALLOWED_MODULES.items():
        module = importlib.import_module(module_name)

        for name in names:
            value = getattr(module, name, None)

            if (
                isinstance(value, types.ModuleType)
                and f"{module_name}.{name}" not in ALLOWED_MODULES
            ):
                missing.append(f"{module_name}.{name}")

    assert missing == []


def test_rapidfuzz_scorers_are_usable() -> None:
    """The scorers in rapidfuzz.fuzz can be called through the submodule."""
    sandbox = _sandbox_from_code(
        """
        from rapidfuzz import fuzz

        result = fuzz.token_set_ratio("fuzzy wuzzy", "wuzzy fuzzy")
        """
    )

    assert sandbox.execute()["result"] == 100


def test_list_item_assignment_works_whatever_the_key_variable_is_called() -> None:
    """Assigning to a list item works even when the index variable shares a list
    method's name.
    """
    sandbox = _sandbox_from_code(
        """
        items = [0, 0, 0, 0]
        index, count, pop, copy = 0, 1, 2, 3
        items[index] = "a"
        items[count] = "b"
        items[pop] = "c"
        items[copy] = "d"
        result = items
        """
    )

    assert sandbox.execute()["result"] == ["a", "b", "c", "d"]


def test_super_reaches_a_parent_method_as_self_does() -> None:
    """super() on a plugin's own instance reads the same attributes self can."""
    sandbox = _sandbox_from_code(
        """
        class Builder:
            def _build(self, value):
                return f"built {value}"

        class PhoneBuilder(Builder):
            def _build(self, value):
                return super()._build(value).upper()

        result = PhoneBuilder()._build("x")
        """
    )

    assert sandbox.execute()["result"] == "BUILT X"


def test_super_on_an_sdk_object_reads_only_what_the_object_allows() -> None:
    """super() bound to an SDK object is held to the same rules as the object itself."""
    sandbox = _sandbox_from_code(
        """
        from canvas_sdk.utils.http import Http

        client = Http()
        super(Http, client)._session
        """
    )

    with pytest.raises(AttributeError):
        sandbox.execute()


def test_sdk_model_meta_is_readable_for_introspection() -> None:
    """Plugins can introspect an SDK model's fields through `_meta`."""
    sandbox = _sandbox_from_code(
        """
        from canvas_sdk.v1.data import LabOrder, Patient

        meta = getattr(Patient, "_meta", None)
        field = meta.get_field("first_name")

        try:
            meta.get_field("no_such_field")
            missing = "found"
        except Exception:
            missing = "raised"

        result = {
            "model_name": LabOrder._meta.model_name,
            "has_first_name": "first_name" in {f.name for f in meta.concrete_fields},
            "field": (field.name, field.null, field.get_internal_type()),
            "missing": missing,
            "related": meta.get_field("default_provider").related_model.__name__,
        }
        """
    )

    result = sandbox.execute()["result"]

    assert result["model_name"] == "laborder"
    assert result["has_first_name"] is True
    assert result["field"] == ("first_name", False, "CharField")
    assert result["missing"] == "raised"
    assert result["related"] == "Staff"


@pytest.mark.parametrize(
    "expression",
    [
        "Patient._meta.apps",
        "Patient._meta._options",
        'Patient._meta.get_field("first_name")._field',
        'Patient._meta.get_field("first_name").model',
    ],
)
def test_sdk_model_meta_exposes_only_introspection(expression: str) -> None:
    """The view of an SDK model's `_meta` offers field introspection and nothing else."""
    sandbox = _sandbox_from_code(
        f"""
        from canvas_sdk.v1.data import Patient

        {expression}
        """
    )

    with pytest.raises(AttributeError):
        sandbox.execute()


def test_getattr_with_a_default_still_returns_the_default() -> None:
    """An explicit default passed to getattr is honored, as in Python."""
    sandbox = _sandbox_from_code(
        """
        class Thing:
            pass

        result = getattr(Thing(), "absent", "fallback")
        """
    )

    assert sandbox.execute()["result"] == "fallback"


@pytest.mark.parametrize(
    "code",
    params_from_dict(
        {
            "settings": """
                from canvas_sdk.commands.tests.schema.tests import settings
            """,
            "os": """
                import os
                result = os.listdir('.')
            """,
            "django_cache": """
                from django.core.cache import caches

                cache = caches['default']
            """,
        }
    ),
)
def test_disallowed_import(code: str) -> None:
    """Test that restricted imports are not allowed."""
    sandbox = _sandbox_from_code(code)

    with pytest.raises(ImportError, match="is not an allowed import."):
        sandbox.execute()


def test_redis_import() -> None:
    """
    Test that you can't import `redis`.

    This verifies that `re` being in ALLOWED_MODULES doesn't allow
    substring matches like `redis` or `reprlib`.
    """
    sandbox = _sandbox_from_code("import redis")

    with pytest.raises(ImportError, match="'redis' is not an allowed import."):
        sandbox.execute()


def test_plugin_runner_settings_import() -> None:
    """Test that imports of plugin runner settings are not allowed."""
    sandbox = _sandbox_from_code(
        """
            import settings
            result = settings.AWS_SECRET_ACCESS_KEY
        """
    )

    with pytest.raises(ImportError, match="'settings' is not an allowed import."):
        sandbox.execute()


RECURRING_APPOINTMENTS_HANDLER_IMPORTS = """
    from canvas_sdk.effects import Effect
    from canvas_sdk.effects.note import ScheduleEvent
    from canvas_sdk.effects.note.appointment import Appointment
    from canvas_sdk.events import EventType
    from canvas_sdk.handlers.base import BaseHandler
    from canvas_sdk.v1.data import Appointment as AppointmentModel
    from canvas_sdk.v1.data import AppointmentMetadata
    from canvas_sdk.v1.data.note import NoteTypeCategories

    result = Effect
"""


def test_recurring_appointments_handler_imports_are_allowed() -> None:
    """The recurrence handler's SDK imports must all be sandbox-legal.

    `Effect` is exported by `canvas_sdk.effects`, not `canvas_sdk.effects.base`; importing it
    from the submodule is rejected by the sandbox and silently stops the handler from registering.
    """
    sandbox = _sandbox_from_code(RECURRING_APPOINTMENTS_HANDLER_IMPORTS)

    scope = sandbox.execute()

    assert scope["result"].__name__ == "Effect"


def test_effect_not_importable_from_effects_base() -> None:
    """`Effect` is only exposed by `canvas_sdk.effects`; the `canvas_sdk.effects.base` path is rejected."""
    sandbox = _sandbox_from_code("from canvas_sdk.effects.base import Effect")

    with pytest.raises(ImportError, match="is not an allowed import"):
        sandbox.execute()


def test_vars_safety() -> None:
    """
    Assert that vars() output is wrapped safely.
    """
    sandbox = _sandbox_from_code("""
        import re

        dunder_builtins = vars(re).get('__builtins__', {})
        exec_method = dunder_builtins.get('exec')

        assert exec_method is None
    """)

    sandbox.execute()


def test_vars_safety_dict_get_unbound() -> None:
    """
    Assert that dict.get(d, key) finds no underscore-prefixed key in vars() output.

    The filtered namespace never contains those keys, so no method reaches them.
    """
    sandbox = _sandbox_from_code("""
        import re

        d = vars(re)

        assert dict.get(d, '__builtins__') is None
    """)

    sandbox.execute()


def test_vars_safety_setdefault() -> None:
    """
    Assert that setdefault() cannot retrieve underscore-prefixed keys.
    """
    sandbox = _sandbox_from_code("""
        import re

        d = vars(re)
        # setdefault returns existing value if key exists
        result = d.setdefault('__builtins__', 'default')

        # Should return the default since __builtins__ was never stored
        assert result == 'default'
    """)

    sandbox.execute()


def test_vars_safety_copy() -> None:
    """
    Assert that copy() excludes underscore-prefixed keys.
    """
    sandbox = _sandbox_from_code("""
        import re

        d = vars(re)
        copied = d.copy()

        # __builtins__ should not be in the copy
        assert '__builtins__' not in copied
        assert copied.get('__builtins__') is None
    """)

    sandbox.execute()


def test_vars_safety_dict_constructor() -> None:
    """
    Assert that dict(d) excludes underscore-prefixed keys.
    """
    sandbox = _sandbox_from_code("""
        import re

        d = vars(re)
        regular_dict = dict(d)

        # __builtins__ should not be in the converted dict
        assert '__builtins__' not in regular_dict
    """)

    sandbox.execute()


def test_vars_safety_unpacking() -> None:
    """
    Assert that {**d} unpacking excludes underscore-prefixed keys.
    """
    sandbox = _sandbox_from_code("""
        import re

        d = vars(re)
        unpacked = {**d}

        # __builtins__ should not be in the unpacked dict
        assert '__builtins__' not in unpacked
    """)

    sandbox.execute()


def test_vars_safety_update() -> None:
    """
    Assert that update() excludes underscore-prefixed keys.
    """
    sandbox = _sandbox_from_code("""
        import re

        d = vars(re)
        target = {}
        target.update(d)

        # __builtins__ should not be in the target
        assert '__builtins__' not in target
    """)

    sandbox.execute()


def test_vars_safety_iteration() -> None:
    """
    Assert that iterating over vars() output doesn't yield underscore-prefixed keys.
    """
    sandbox = _sandbox_from_code("""
        import re

        d = vars(re)

        # Iteration should not yield underscore keys
        for key in d:
            assert not key.startswith('_'), f"Unexpected underscore key: {key}"

        # Also check list() and keys()
        assert '__builtins__' not in list(d)
        assert '__builtins__' not in d.keys()
    """)

    sandbox.execute()


def test_vars_safety_popitem() -> None:
    """
    Assert that popitem() excludes underscore-prefixed keys.
    """
    sandbox = _sandbox_from_code("""
        import re

        d = vars(re)

        # Pop all items and verify none are underscore-prefixed
        popped_keys = []
        try:
            while True:
                key, value = d.popitem()
                assert not key.startswith('_'), f"Unexpected underscore key from popitem: {key}"
                popped_keys.append(key)
        except KeyError:
            pass  # Dict is empty

        assert '__builtins__' not in popped_keys
    """)

    sandbox.execute()


def test_vars_safety_items_values() -> None:
    """
    Assert that items() and values() exclude underscore-prefixed keys.
    """
    sandbox = _sandbox_from_code("""
        import re

        d = vars(re)

        # items() should not include underscore keys
        keys_from_items = [key for key, value in d.items()]
        for key in keys_from_items:
            assert not key.startswith('_'), f"Unexpected underscore key from items(): {key}"

        # values() should not include more items than keys()
        # (which would indicate hidden keys)
        assert len(d.values()) == len(d.keys())
    """)

    sandbox.execute()


def test_vars_safety_getattr_dict_get() -> None:
    """
    Assert that getattr(dict, 'get')(d, key) finds no underscore-prefixed key in vars() output.
    """
    sandbox = _sandbox_from_code("""
        import re

        d = vars(re)

        try:
            get_method = getattr(dict, 'get')
            result = get_method(d, '__builtins__')
            # If we get here, result should be None or not dangerous
            assert result is None or not callable(result.get('exec', None) if isinstance(result, dict) else None)
        except TypeError:
            # Expected: descriptor doesn't apply
            pass
    """)

    sandbox.execute()


def test_mro_method_blocked() -> None:
    """
    Assert that mro() method is blocked to prevent __subclasses__ access.
    """
    sandbox = _sandbox_from_code("""
        class Target:
            pass

        # Try to access mro() - should be blocked
        Target.mro()
    """)

    with pytest.raises(AttributeError, match="is a restricted method name"):
        sandbox.execute()


def test_load_module_blocked() -> None:
    """`load_module` is a restricted method name, whatever object defines it."""
    sandbox = _sandbox_from_code("""
        class Target:
            pass

        class FakeLoader:
            def load_module(self, name):
                return None

        loader = FakeLoader()
        loader.load_module('os')
    """)

    with pytest.raises(AttributeError, match="is a restricted method name"):
        sandbox.execute()


def test_vars_on_non_allowed_module_blocked() -> None:
    """vars() on an allowed module lists the names the allowlist grants."""
    sandbox = _sandbox_from_code("""
        import re

        d = vars(re)
        assert 'compile' in d
    """)

    sandbox.execute()


def test_subclasses_via_type_dict_blocked() -> None:
    """The class of a class is a name-only proxy, so its `__dict__` is not readable."""
    sandbox = _sandbox_from_code("""
        class Target:
            pass

        type_dict = Target.__class__.__dict__
    """)

    with pytest.raises(AttributeError, match="restricted"):
        sandbox.execute()


def test_support_match() -> None:
    """Test that match is supported."""
    sandbox = _sandbox_from_code(
        """
            day = 5
            month = 12

            success = False

            match day:
                case 1 | 2 | 3 if month == 1:
                    success = False
                case 5 if month == 10:
                    success = False
                case 5 if month == 12:
                    success = True
                case _:
                    success = False

            assert success
        """
    )

    sandbox.execute()


def test_support_match_tuple() -> None:
    """Test that match is supported."""
    sandbox = _sandbox_from_code(
        """
            point = (0, 5)

            success = False

            match point:
                case (0, 0):
                    success = False
                case (0, x as non_origin):
                    success = non_origin == 5
                case (0, *extra):
                    success = False

            assert success
        """
    )

    sandbox.execute()


def test_support_ellipsis() -> None:
    """Test that Ellipsis is supported."""
    sandbox = _sandbox_from_code(
        """
            x: tuple[int, ...] = (1, 2, 3)
        """
    )

    sandbox.execute()


def test_support_type_annotations() -> None:
    """Test that type annotations work."""
    sandbox = _sandbox_from_code(
        """
            point: int = 5
            name: str = "name"

            assert point == 5
            assert name == "name"
        """
    )

    sandbox.execute()


def test_support_from_future_import_annotations() -> None:
    """Test that `from __future__ import annotations` is allowed."""
    sandbox = _sandbox_from_code(
        """
            from __future__ import annotations

            def greet(name: str) -> str:
                return f"hello {name}"

            assert greet("world") == "hello world"
        """
    )

    sandbox.execute()


def test_disallowed_future_import() -> None:
    """Test that importing non-annotations members from __future__ is not allowed."""
    sandbox = _sandbox_from_code("from __future__ import division")

    with pytest.raises(ImportError, match="is not an allowed import"):
        sandbox.execute()


def test_support_dataclasses() -> None:
    """Test that dataclasses can be created."""
    sandbox = _sandbox_from_code("""
        from dataclasses import dataclass

        @dataclass
        class InventoryItem:
            name: str
            unit_price: float
            quantity_on_hand: int = 0

            def total_cost(self) -> float:
                return self.unit_price * self.quantity_on_hand


        item = InventoryItem(name='test', unit_price=0.5, quantity_on_hand=1)

        assert item.total_cost() == 0.5
    """)

    sandbox.execute()


@pytest.mark.parametrize("canvas_module", CANVAS_SUBMODULE_NAMES)
def test_all_modules_implement_canvas_allowed_attributes(canvas_module: str) -> None:
    """
    Test that all modules under canvas_sdk have an __exports__ module attribute
    and that it is a tuple.
    """
    imported_module = importlib.import_module(canvas_module)

    assert hasattr(imported_module, "__exports__")
    assert isinstance(imported_module.__exports__, tuple)


RE_ERROR_STRINGS = re.compile(
    r"""(
        '(settings|os|sys)'\ is\ not\ an\ allowed\ import|
        cannot\ import\ name\ '(settings|os|sys)'|
        future\ feature\ (settings|os|sys)\ is\ not\ defined
    )""",
    flags=re.VERBOSE,
)


@pytest.mark.parametrize("allowed_module", ALLOWED_MODULES)
def test_plugin_runner_settings_allowed_module_import(allowed_module: str) -> None:
    """
    Test that no module in ALLOWED_MODULES re-exports settings.
    """
    sandbox = _sandbox_from_code(
        f"""
            from {allowed_module} import settings
            result = settings.AWS_SECRET_ACCESS_KEY
        """
    )

    with pytest.raises((ImportError, SyntaxError, RuntimeError), match=RE_ERROR_STRINGS):
        sandbox.execute()


@pytest.mark.parametrize("allowed_module", ALLOWED_MODULES)
def test_plugin_runner_os_allowed_module_import(allowed_module: str) -> None:
    """
    Test that no module in ALLOWED_MODULES re-exports settings.
    """
    sandbox = _sandbox_from_code(f"from {allowed_module} import os")

    with pytest.raises((ImportError, SyntaxError, RuntimeError), match=RE_ERROR_STRINGS):
        sandbox.execute()


@pytest.mark.parametrize("allowed_module", ALLOWED_MODULES)
def test_plugin_runner_sys_allowed_module_import(allowed_module: str) -> None:
    """
    Test that no module in ALLOWED_MODULES re-exports settings.
    """
    sandbox = _sandbox_from_code(f"from {allowed_module} import sys")

    with pytest.raises((ImportError, SyntaxError, RuntimeError), match=RE_ERROR_STRINGS):
        sandbox.execute()


@pytest.mark.parametrize(
    "banned_import",
    [
        "from arrow.parser import sys",
        "from arrow.parser import sys as something_else",
        "from requests.sessions import os",
        "from requests.sessions import os as something_else",
        """
            from requests import sessions  # fails here
            sessions.os
        """,
    ],
)
def test_sandbox_disallows_bad_modules(banned_import: str) -> None:
    """
    Test that os, sys, etc. are not importable.
    """
    sandbox = _sandbox_from_code(banned_import)

    with pytest.raises(ImportError):
        sandbox.execute()


@pytest.mark.parametrize(
    "banned_attribute",
    [
        """
            import jwt
            jwt.decode_complete
        """,
        """
            from arrow import parser
            parser.sys  # fails here
        """,
    ],
)
def test_sandbox_disallows_bad_attributes(banned_attribute: str) -> None:
    """
    Test that module attributes not allowlisted are denied.
    """
    sandbox = _sandbox_from_code(banned_attribute)

    with pytest.raises(AttributeError):
        sandbox.execute()


@pytest.mark.parametrize(
    "banned_attribute",
    params_from_dict(
        {
            "jwt_attribute_method": """
                import jwt
                jwt.encode = lambda x: print(x)
            """,
            "response_existing_attribute": """
                from requests import Response
                Response.text = "evil"
            """,
            "response_new_attribute": """
                from requests import Response
                Response.status_code = 500
            """,
        }
    ),
)
def test_sandbox_disallows_bad_attribute_writes(banned_attribute: str) -> None:
    """
    Test that module attributes not allowlisted are denied.
    """
    sandbox = _sandbox_from_code(banned_attribute)

    with pytest.raises(AttributeError, match="Forbidden assignment to a (non-)?module attribute:"):
        sandbox.execute()


@pytest.mark.parametrize(
    "good_attribute",
    [
        """
            from canvas_sdk.commands import StopMedicationCommand

            obj = StopMedicationCommand(note_uuid="123")
            obj.rationale = "The patient is feeling better."
        """,
    ],
)
def test_sandbox_allows_good_attribute_writes(good_attribute: str) -> None:
    """
    Test that attributes on objects created in the namespace are allowed.
    """
    sandbox = _sandbox_from_code(good_attribute)
    sandbox.execute()


def test_plugin_runner_re_export() -> None:
    """
    Test what is re-exported by our code.
    """
    sandbox = _sandbox_from_code(
        """
            import canvas_sdk.utils
            canvas_sdk.utils.ThreadPoolExecutor()
        """
    )

    with pytest.raises(AttributeError, match="invalid attribute name"):
        sandbox.execute()


def test_allowed_import() -> None:
    """Test that allowed imports (from ALLOWED_MODULES) work correctly."""
    sandbox = _sandbox_from_code(
        """
            import json
            result = json.dumps({"key": "value"})
        """
    )

    scope = sandbox.execute()
    assert scope["result"] == '{"key": "value"}', "JSON encoding should work with allowed imports."


def test_trim_function_import() -> None:
    """Test that Trim function from django.db.models.functions can be imported successfully."""
    sandbox = _sandbox_from_code(
        """
            from django.db.models.functions import Trim
            result = "Trim import successful"
        """
    )

    scope = sandbox.execute()
    assert scope["result"] == "Trim import successful", (
        "Trim import should work from django.db.models.functions."
    )


def test_coalesce_function_import() -> None:
    """Test that Coalesce function from django.db.models.functions can be imported successfully."""
    sandbox = _sandbox_from_code(
        """
            from django.db.models.functions import Coalesce
            result = "Coalesce import successful"
        """
    )

    scope = sandbox.execute()
    assert scope["result"] == "Coalesce import successful", (
        "Coalesce import should work from django.db.models.functions."
    )


def test_window_expression_import() -> None:
    """Test that Window, RowRange, and ValueRange can be imported from django.db.models."""
    sandbox = _sandbox_from_code(
        """
            from django.db.models import Window, RowRange, ValueRange
            result = "Window expression import successful"
        """
    )

    scope = sandbox.execute()
    assert scope["result"] == "Window expression import successful", (
        "Window, RowRange, and ValueRange should be importable from django.db.models."
    )


def test_window_functions_import() -> None:
    """Test that window functions can be imported from django.db.models.functions."""
    sandbox = _sandbox_from_code(
        """
            from django.db.models.functions import (
                CumeDist, DenseRank, FirstValue, Lag, LastValue,
                Lead, NthValue, Ntile, PercentRank, Rank, RowNumber,
            )
            result = "Window functions import successful"
        """
    )

    scope = sandbox.execute()
    assert scope["result"] == "Window functions import successful", (
        "All window functions should be importable from django.db.models.functions."
    )


def test_traceback_format_exc() -> None:
    """Test that traceback.format_exc can be imported and used."""
    sandbox = _sandbox_from_code(
        """
            import traceback
            try:
                raise ValueError("test error")
            except ValueError:
                result = traceback.format_exc()
        """
    )

    scope = sandbox.execute()
    assert "ValueError: test error" in scope["result"], (
        "traceback.format_exc() should return a string containing the exception."
    )


def test_traceback_restricted_attributes() -> None:
    """Test that only format_exc is accessible on the traceback module."""
    with pytest.raises(
        AttributeError,
        match=r'"traceback.extract_tb" is an invalid attribute name',
    ):
        sandbox = _sandbox_from_code(
            """
                import traceback
                traceback.extract_tb(None)
            """
        )
        sandbox.execute()


def test_extract_exc_frames() -> None:
    """Test that extract_exc_frames returns safe frame summaries."""
    sandbox = _sandbox_from_code(
        """
            try:
                raise ValueError("test error")
            except ValueError:
                frames = extract_exc_frames()
                result = {
                    "count": len(frames),
                    "has_filename": hasattr(frames[0], "filename"),
                    "has_lineno": hasattr(frames[0], "lineno"),
                    "has_name": hasattr(frames[0], "name"),
                }
        """
    )

    scope = sandbox.execute()
    assert scope["result"]["count"] > 0, "Should have at least one frame."
    assert scope["result"]["has_filename"], "Frame should expose filename."
    assert scope["result"]["has_lineno"], "Frame should expose lineno."
    assert scope["result"]["has_name"], "Frame should expose name."


def test_extract_exc_frames_no_exception() -> None:
    """Test that extract_exc_frames returns empty list when no exception is active."""
    sandbox = _sandbox_from_code(
        """
            result = extract_exc_frames()
        """
    )

    scope = sandbox.execute()
    assert scope["result"] == [], "Should return empty list when no exception is active."


def test_extract_exc_frames_restricts_locals() -> None:
    """Test that safe frame summaries do not expose locals or source lines."""
    sandbox = _sandbox_from_code(
        """
            try:
                secret = "sensitive_data"
                raise ValueError("test")
            except ValueError:
                frames = extract_exc_frames()
                try:
                    frames[0].locals
                    result = "FAIL: locals was accessible"
                except AttributeError:
                    result = "PASS: locals was blocked"
        """
    )

    scope = sandbox.execute()
    assert scope["result"] == "PASS: locals was blocked", (
        "Frame summaries must not expose local variables."
    )


def test_extract_exc_frames_restricts_line() -> None:
    """Test that safe frame summaries do not expose source code lines."""
    sandbox = _sandbox_from_code(
        """
            try:
                raise ValueError("test")
            except ValueError:
                frames = extract_exc_frames()
                try:
                    frames[0].line
                    result = "FAIL: line was accessible"
                except AttributeError:
                    result = "PASS: line was blocked"
        """
    )

    scope = sandbox.execute()
    assert scope["result"] == "PASS: line was blocked", (
        "Frame summaries must not expose source code lines."
    )


def test_traceback_traversal_pattern() -> None:
    """Test the standard tb = error.__traceback__; while tb: tb = tb.tb_next pattern."""
    sandbox = _sandbox_from_code(
        """
            try:
                raise ValueError("test error")
            except ValueError as error:
                frames = []
                tb = error.__traceback__
                while tb is not None:
                    frame = tb.tb_frame
                    frames.append({
                        'filename': frame.f_code.co_filename,
                        'function': frame.f_code.co_name,
                        'lineno': tb.tb_lineno,
                    })
                    tb = tb.tb_next
                result = frames
        """
    )

    scope = sandbox.execute()
    assert len(scope["result"]) > 0, "Should have at least one frame."
    assert "filename" in scope["result"][0], "Frame should have filename."
    assert "function" in scope["result"][0], "Frame should have function."
    assert "lineno" in scope["result"][0], "Frame should have lineno."


def test_traceback_frame_blocks_locals() -> None:
    """Test that __traceback__ frame proxy does not expose f_locals."""
    sandbox = _sandbox_from_code(
        """
            try:
                secret = "sensitive_data"
                raise ValueError("test")
            except ValueError as error:
                tb = error.__traceback__
                frame = tb.tb_frame
                try:
                    frame.f_locals
                    result = "FAIL: f_locals was accessible"
                except AttributeError:
                    result = "PASS: f_locals was blocked"
        """
    )

    scope = sandbox.execute()
    assert scope["result"] == "PASS: f_locals was blocked", "Frame proxy must not expose f_locals."


def test_traceback_frame_blocks_globals() -> None:
    """Test that __traceback__ frame proxy does not expose f_globals."""
    sandbox = _sandbox_from_code(
        """
            try:
                raise ValueError("test")
            except ValueError as error:
                tb = error.__traceback__
                frame = tb.tb_frame
                try:
                    frame.f_globals
                    result = "FAIL: f_globals was accessible"
                except AttributeError:
                    result = "PASS: f_globals was blocked"
        """
    )

    scope = sandbox.execute()
    assert scope["result"] == "PASS: f_globals was blocked", (
        "Frame proxy must not expose f_globals."
    )


def test_traceback_code_blocks_co_varnames() -> None:
    """Test that the code object proxy blocks access to co_varnames."""
    sandbox = _sandbox_from_code(
        """
            try:
                raise ValueError("test")
            except ValueError as error:
                code = error.__traceback__.tb_frame.f_code
                try:
                    code.co_varnames
                    result = "FAIL: co_varnames was accessible"
                except AttributeError:
                    result = "PASS: co_varnames was blocked"
        """
    )

    scope = sandbox.execute()
    assert scope["result"] == "PASS: co_varnames was blocked", (
        "Code object proxy must block co_varnames."
    )


def test_traceback_code_blocks_co_consts() -> None:
    """Test that the code object proxy blocks access to co_consts."""
    sandbox = _sandbox_from_code(
        """
            try:
                raise ValueError("test")
            except ValueError as error:
                code = error.__traceback__.tb_frame.f_code
                try:
                    code.co_consts
                    result = "FAIL: co_consts was accessible"
                except AttributeError:
                    result = "PASS: co_consts was blocked"
        """
    )

    scope = sandbox.execute()
    assert scope["result"] == "PASS: co_consts was blocked", (
        "Code object proxy must block co_consts."
    )


def test_traceback_none_when_no_traceback() -> None:
    """Test that __traceback__ returns None for exceptions without a traceback."""
    sandbox = _sandbox_from_code(
        """
            error = ValueError("no traceback")
            result = error.__traceback__ is None
        """
    )

    scope = sandbox.execute()
    assert scope["result"] is True, "__traceback__ should be None for unraised exceptions."


def test_multiple_functions_import() -> None:
    """Test that multiple functions from django.db.models.functions can be imported together."""
    sandbox = _sandbox_from_code(
        """
            from django.db.models.functions import Trim, Coalesce
            result = "Multiple functions import successful"
        """
    )

    scope = sandbox.execute()
    assert scope["result"] == "Multiple functions import successful", (
        "Multiple functions should be importable together."
    )


def test_prefetch_import() -> None:
    """Test that Prefetch can be imported from django.db.models and django.db.models.query."""
    sandbox = _sandbox_from_code(
        """
            from django.db.models import Prefetch
            from django.db.models.query import Prefetch
            result = "Prefetch import successful"
        """
    )
    scope = sandbox.execute()
    assert scope["result"] == "Prefetch import successful", (
        "Prefetch should be importable from django.db.models and django.db.models.query."
    )


def test_aggregations_import() -> None:
    """Test that aggregation functions can be imported from django.db.models."""
    sandbox = _sandbox_from_code(
        """
            from django.db.models import Sum, Avg, Min, Max
            result = "Aggregation functions import successful"
        """
    )
    scope = sandbox.execute()
    assert scope["result"] == "Aggregation functions import successful", (
        "Aggregation functions should be importable from django.db.models."
    )


def test_expressions_import() -> None:
    """Test that expression functions can be imported from django.db.models and django.db.models.expressions."""
    sandbox = _sandbox_from_code(
        """
            from django.db.models import Exists, OuterRef, Subquery
            from django.db.models.expressions import Exists, OuterRef, Subquery
            result = "Expressions import successful"
        """
    )

    scope = sandbox.execute()
    assert scope["result"] == "Expressions import successful", (
        "Expression functions should be importable from django.db.models and django.db.models.expressions."
    )


def test_typeguard_import_and_usage() -> None:
    """Test that TypeGuard can be imported and used in sandbox."""
    sandbox = _sandbox_from_code(
        """
            from typing import TypeGuard

            def is_string(val) -> TypeGuard[str]:
                return isinstance(val, str)

            # Test the TypeGuard function
            test_value = "hello"
            result = is_string(test_value)
        """
    )

    scope = sandbox.execute()
    assert scope["result"] is True, "TypeGuard function should correctly identify string"


def test_re_fullmatch_import_and_usage() -> None:
    """Test that re.fullmatch can be imported and used in sandbox."""
    sandbox = _sandbox_from_code(
        """
            from re import fullmatch

            result = fullmatch(r'\\d+', '12345')
        """
    )

    scope = sandbox.execute()
    assert scope["result"] is not None, "fullmatch should match an all-digit string"


def test_re_fullmatch_no_match() -> None:
    """Test that re.fullmatch correctly rejects partial matches."""
    sandbox = _sandbox_from_code(
        """
            import re

            result = re.fullmatch(r'\\d+', '123abc')
        """
    )

    scope = sandbox.execute()
    assert scope["result"] is None, "fullmatch should not match a partial digit string"


def test_type_checking_import() -> None:
    """Test that TYPE_CHECKING can be imported and used in sandbox."""
    sandbox = _sandbox_from_code(
        """
            from typing import TYPE_CHECKING

            result = TYPE_CHECKING
        """
    )

    scope = sandbox.execute()
    assert scope["result"] is False, "TYPE_CHECKING should be False at runtime"


def test_forbidden_name() -> None:
    """Test that forbidden function names are blocked by Transformer."""
    sandbox = _sandbox_from_code("builtins = {}")

    with pytest.raises(RuntimeError, match="Code is invalid"):
        sandbox.execute()


@pytest.mark.parametrize(
    "code",
    [
        code
        for var in ("__is_plugin__", "__name__", "__does_not_exist__")
        for code in [
            f"{var} = 'test'",
            f"test = {var} = 'test'",
            f"test = {var} = test2 = 'test'",
            f"(a, (b, c), (d, ({var}, f))) = (1, (2, 3), (4, (5, 6)))",
            f"(a, (b, c), (d, [{var}, f])) = (1, (2, 3), (4, [5, 6]))",
        ]
    ],
)
def test_forbidden_assignment(code: str) -> None:
    """Test that forbidden assignments are blocked by Transformer."""
    sandbox = _sandbox_from_code(code)

    with pytest.raises(RuntimeError, match="Code is invalid"):
        sandbox.execute()


GUARD_NAMES = (
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
)

# Each way Python binds a name, as a template over the name `N`.
BINDING_FORMS = {
    "assignment": "N = None",
    "annotated assignment": "N: object = None",
    "augmented assignment": "N += 1",
    "walrus": "(N := None)",
    "for target": "for N in []:\n    pass",
    "with target": "with x as N:\n    pass",
    "comprehension target": "[None for N in []]",
    "import as": "import json as N",
    "from import as": "from json import dumps as N",
    "except as": "try:\n    pass\nexcept Exception as N:\n    pass",
    "match capture": "match 1:\n    case N:\n        pass",
    "match star": "match []:\n    case [*N]:\n        pass",
    "match mapping rest": "match {}:\n    case {**N}:\n        pass",
    "def": "def N():\n    pass",
    "class": "class N:\n    pass",
    "global": "def f():\n    global N\n    N = None",
    "function argument": "def f(N):\n    pass",
    "lambda argument": "f = lambda N: None",
}


@pytest.mark.parametrize("name", GUARD_NAMES)
@pytest.mark.parametrize("form", BINDING_FORMS.values(), ids=BINDING_FORMS.keys())
def test_plugin_code_cannot_bind_a_name_the_sandbox_provides(form: str, name: str) -> None:
    """A name the sandbox puts in a plugin's scope cannot be bound by plugin code."""
    sandbox = _sandbox_from_code(form.replace("N", name))

    assert any(name in error for error in sandbox.errors), sandbox.errors

    with pytest.raises(RuntimeError, match="Code is invalid"):
        sandbox.execute()


DOUBLE_UNDERSCORE_BINDING_FORMS = {
    **{
        label: form
        for label, form in BINDING_FORMS.items()
        if label not in ("assignment", "function argument", "lambda argument")
    },
    "def inside a method": "class Thing:\n    def f(self):\n        def N():\n            pass",
}


@pytest.mark.parametrize("name", ("__name__", "__does_not_exist__"))
@pytest.mark.parametrize(
    "form", DOUBLE_UNDERSCORE_BINDING_FORMS.values(), ids=DOUBLE_UNDERSCORE_BINDING_FORMS.keys()
)
def test_plugin_code_cannot_bind_a_double_underscore_name(form: str, name: str) -> None:
    """A double-underscore name cannot be bound in any form plain assignment does not
    already refuse, so a module's `__name__` stays the one the runner gave it.
    """
    sandbox = _sandbox_from_code(form.replace("N", name))

    assert any(name in error for error in sandbox.errors), sandbox.errors

    with pytest.raises(RuntimeError, match="Code is invalid"):
        sandbox.execute()


def test_a_double_underscore_assignment_is_refused_once() -> None:
    """Plain assignment to a double-underscore name reports a single error."""
    sandbox = _sandbox_from_code("__name__ = 'other'")

    assert len(sandbox.errors) == 1, sandbox.errors


def test_double_underscore_names_bind_as_methods_arguments_and_all() -> None:
    """Methods, function arguments, and `__all__` may use double-underscore names."""
    sandbox = _sandbox_from_code(
        """
        __all__: list[str] = ["Thing"]
        __all__ += ["double"]

        class Thing:
            def __init__(self, value):
                self.value = value

            def __eq__(self, other):
                return isinstance(other, Thing) and other.value == self.value

        def double(__value):
            return __value * 2

        result = (Thing(1) == Thing(1), double(2), __all__, __name__)
        """
    )

    assert not sandbox.errors
    assert sandbox.execute()["result"] == (
        True,
        4,
        ["Thing", "double"],
        "plugin_name.handlers.handler",
    )


@pytest.mark.parametrize(
    "code",
    params_from_dict(
        {
            "module_assignment": """
                _getattr_ = None
            """,
            "positional_only_argument": """
                def handler(value, _getattr_=None, /):
                    return value
            """,
            "regular_argument": """
                def handler(value, _getattr_=None):
                    return value
            """,
            "keyword_only_argument": """
                def handler(value, *, _getattr_=None):
                    return value
            """,
            "lambda_positional_only_argument": """
                handler = lambda value, _getattr_=None, /: value
            """,
            "vararg": """
                def handler(*_getattr_):
                    return _getattr_
            """,
            "kwarg": """
                def handler(**_getattr_):
                    return _getattr_
            """,
            "function_name": """
                def _getattr_():
                    return None
            """,
            "class_name": """
                class _getattr_:
                    pass
            """,
            "import_alias": """
                import json as _getattr_
            """,
            "import_from_alias": """
                from json import loads as _getattr_
            """,
            "for_target": """
                for _getattr_ in []:
                    pass
            """,
            "with_target": """
                from contextlib import suppress

                with suppress(Exception) as _getattr_:
                    pass
            """,
            "except_target": """
                try:
                    pass
                except Exception as _getattr_:
                    pass
            """,
            "walrus": """
                result = (_getattr_ := None)
            """,
            "tuple_unpacking": """
                a, _getattr_ = 1, 2
            """,
            "comprehension_target": """
                result = [_getattr_ for _getattr_ in []]
            """,
        }
    ),
)
def test_sandbox_denies_binding_a_reserved_name(code: str) -> None:
    """Test that no syntax lets plugin code bind a name reserved for a policy hook.

    A leading underscore is otherwise only a warning, so each binding form needs
    its own case: the name check has to run for arguments, targets, aliases and
    definitions alike.
    """
    sandbox = _sandbox_from_code(code)

    with pytest.raises(RuntimeError, match="is a reserved name"):
        sandbox.execute()


@pytest.mark.parametrize("name", sorted(PROTECTED_SCOPE_NAMES))
def test_sandbox_denies_binding_every_protected_name(name: str) -> None:
    """Test that every reserved name is rejected, not just the ones with cases above."""
    sandbox = _sandbox_from_code(f"def handler(value, {name}=None, /):\n    return value\n")

    with pytest.raises(RuntimeError, match="is a reserved name"):
        sandbox.execute()


def test_protected_scope_names_covers_every_injected_guard() -> None:
    """Test that every guard the sandbox injects is a name plugins cannot bind.

    Guards are named `_like_this_`; the remaining underscore-prefixed entries in
    the scope (`__builtins__`, `__name__`, ...) are readable by plugin code.
    """
    sandbox = _sandbox_from_code("result = 1")

    injected_guards = {
        name
        for name in sandbox.scope
        if name.startswith("_") and name.endswith("_") and not name.startswith("__")
    }

    assert injected_guards
    assert injected_guards <= PROTECTED_SCOPE_NAMES


def test_plugin_annotations_are_not_stringified() -> None:
    """Test that annotations in plugin code evaluate to objects rather than strings.

    Plugin code is compiled with `dont_inherit=True` so it does not pick up the
    `from __future__ import annotations` of the module that calls `compile()`.
    Without that, `dataclass` and anything else reading `__annotations__` at
    runtime sees strings.
    """
    sandbox = _sandbox_from_code(
        """
            class Annotated:
                name: str
                count: int

            result = Annotated.__annotations__
        """
    )

    assert sandbox.execute()["result"] == {"name": str, "count": int}


def test_restricted_python_leaks_its_future_flags() -> None:
    """Test that `compile_restricted_exec` still compiles with inherited `__future__` flags.

    `Sandbox._compiled` compiles plugin code itself instead of calling
    `compile_restricted_exec` only because that wrapper hardcodes
    `dont_inherit`, so plugin code picks up the `from __future__ import
    annotations` of RestrictedPython's own `compile` module.
    """
    compiled = compile_restricted_exec("x = 1")

    assert compiled.code is not None
    assert compiled.code.co_flags & __future__.annotations.compiler_flag, (
        "compile_restricted_exec no longer leaks its __future__ flags; replace "
        "the local compile in plugin_runner.sandbox.Sandbox._compiled with it."
    )


def test_code_with_warnings() -> None:
    """Test that the sandbox captures warnings for restricted names or usage."""
    sandbox = _sandbox_from_code(
        """
            _x = 5
            result = _x
        """
    )
    assert sandbox.warnings, "There should be warnings for using restricted names."
    scope = sandbox.execute()
    assert scope["result"] == 5, "Code should execute despite warnings."


def test_compile_errors() -> None:
    """Test that compile errors are detected for invalid syntax."""
    sandbox = _sandbox_from_code(
        """
            def missing_colon()
                return 42
        """
    )

    with pytest.raises(RuntimeError, match="Code is invalid"):
        sandbox.execute()


def test_sandbox_scope() -> None:
    """Verify the sandbox scope includes expected built-ins and utility functions."""
    sandbox = _sandbox_from_code(VALID_CODE)
    scope = sandbox.execute()
    assert "any" in scope["__builtins__"]
    assert scope["__builtins__"]["any"] == any, "'any' function should be accessible in sandbox."


def test_print_collector() -> None:
    """Ensure that PrintCollector is used for capturing prints."""
    sandbox = _sandbox_from_code('print("Hello, Sandbox!")')
    scope = sandbox.execute()
    assert "Hello, Sandbox!" in scope["_print"].txt, "Print output should be captured."


def test_eval_disallowed() -> None:
    """Test that eval() is not allowed in the sandbox."""
    sandbox = _sandbox_from_code('eval("2 ** 8")')

    with pytest.raises(RuntimeError, match="Code is invalid"):
        sandbox.execute()


def test_printf_import_denied() -> None:
    """Test that imports are checked when invoked in a string format operation."""
    sandbox = _sandbox_from_code("""
        def do_import():
            from requests.sessions import os

        print(f'{do_import()}')
    """)

    with pytest.raises(ImportError, match="'requests.sessions' is not an allowed import."):
        sandbox.execute()


def test_sandbox_denies_module_name_import_outside_package() -> None:
    """Test that modules outside the root package cannot be imported."""
    sandbox = _sandbox_from_code(
        source_code="""
            import bad_module.bad
            result = bad_module.bad
        """,
        module_name="good_module.good",
        extra_source_code="""
            def thing():
                return 42

        """,
        extra_module_name="bad_module.bad",
    )

    with pytest.raises(ImportError, match="'bad_module.bad' is not an allowed import."):
        sandbox.execute()


def test_sandbox_allows_access_to_private_attributes_same_module() -> None:
    """Test that private attribute/method access is allowed for the same module/package."""
    sandbox = _sandbox_from_code("""
        class MyClass:
            _private_attr = 42

        pvt = MyClass()._private_attr
    """)

    sandbox.execute()


@pytest.mark.parametrize(
    "code",
    params_from_dict(
        {
            "secrets": """
                import secrets

                token = secrets.token_urlsafe(16) + secrets.token_hex(8)
                raw = secrets.token_bytes(8)
                number = secrets.randbelow(10)
                pick = secrets.choice(["a", "b"])
                same = secrets.compare_digest("a", "a")
            """,
            "re_I": """
                import re

                matched = re.search("abc", "ABC", re.I)
            """,
            "base64_urlsafe": """
                import base64

                decoded = base64.urlsafe_b64decode(base64.urlsafe_b64encode(b"a?b/c"))
            """,
            "bisect": """
                import bisect

                values = [1, 3, 5]
                index = bisect.bisect_left(values, 3) + bisect.bisect_right(values, 3)
                bisect.insort(values, 4)
            """,
            "django_length": """
                from django.db.models.functions import Length
            """,
            "django_database_error": """
                from django.db import DatabaseError
            """,
        }
    ),
)
def test_sandbox_allows_safe_standard_library_and_django_names(code: str) -> None:
    """Names plugins reach for that read no files and open no connections."""
    sandbox = _sandbox_from_code(code)
    sandbox.execute()


@pytest.mark.parametrize(
    "code",
    params_from_dict(
        {
            "read_underscore_key_from_dict": """
                d = {"_key": "value"}
                result = d["_key"]
                assert result == "value"
            """,
            "read_underscore_key_from_typed_dict": """
                from typing import TypedDict

                class MyConfig(TypedDict):
                    _internal: str
                    public: str

                config: MyConfig = {"_internal": "secret", "public": "visible"}
                result = config["_internal"]
                assert result == "secret"
            """,
            "read_underscore_key_from_dict_in_method": """
                class MyClass:
                    def compute(self):
                        d = {"_internal": 42}
                        return d["_internal"]

                result = MyClass().compute()
                assert result == 42
            """,
        }
    ),
)
def test_sandbox_allows_underscore_item_access_on_plugin_objects(code: str) -> None:
    """Test that underscore key access is allowed on objects defined within the plugin."""
    sandbox = _sandbox_from_code(code)
    sandbox.execute()


@pytest.mark.parametrize(
    "code",
    params_from_dict(
        {
            "write_underscore_key_to_dict": """
                d = {}
                d["_key"] = "value"
                assert d["_key"] == "value"
            """,
            "update_underscore_key_in_dict": """
                d = {"_key": "old"}
                d["_key"] = "new"
                assert d["_key"] == "new"
            """,
            "write_underscore_key_in_method": """
                class MyClass:
                    def build(self):
                        d = {}
                        d["_internal"] = 42
                        return d["_internal"]

                assert MyClass().build() == 42
            """,
        }
    ),
)
def test_sandbox_allows_underscore_item_write_on_plugin_dicts(code: str) -> None:
    """Test that writing underscore keys to plugin-created dicts is allowed."""
    sandbox = _sandbox_from_code(code)
    sandbox.execute()


@pytest.mark.parametrize(
    "code",
    params_from_dict(
        {
            "dict_get_returns_none": """
                from canvas_sdk.utils.http import Http

                d = Http().__dict__
                assert d.get("_session") is None
            """,
            "dict_iteration_excludes_private_keys": """
                from canvas_sdk.utils.http import Http

                d = Http().__dict__
                private_keys = [k for k in d if k.startswith("_")]
                assert len(private_keys) == 0, f"unexpected private keys: {private_keys}"
            """,
            "vars_get_returns_none": """
                from canvas_sdk.utils.http import Http

                d = vars(Http())
                assert d.get("_session") is None
            """,
            "vars_iteration_excludes_private_keys": """
                from canvas_sdk.utils.http import Http

                d = vars(Http())
                private_keys = [k for k in d if k.startswith("_")]
                assert len(private_keys) == 0, f"unexpected private keys: {private_keys}"
            """,
            "dict_values_excludes_private": """
                from canvas_sdk.utils.http import Http

                d = Http().__dict__
                for v in d.values():
                    assert not hasattr(v, 'headers'), "session object returned by values()"
            """,
            "dict_items_excludes_private": """
                from canvas_sdk.utils.http import Http

                d = Http().__dict__
                for k, v in d.items():
                    assert not k.startswith("_"), f"unexpected private key: {k}"
            """,
            "dict_contains_private_key_false": """
                from canvas_sdk.utils.http import Http

                d = Http().__dict__
                assert "_session" not in d
            """,
            "dict_len_excludes_private": """
                from canvas_sdk.utils.http import Http

                client = Http()
                d = client.__dict__
                all_keys = vars(client)
                assert len(d) == len(all_keys)
                assert "_session" not in d
            """,
        }
    ),
)
def test_sandbox_filters_private_attrs_from_external_dict_and_vars(code: str) -> None:
    """Test that __dict__ and vars() on external objects exclude underscore-prefixed keys."""
    sandbox = _sandbox_from_code(code)
    sandbox.execute()


@pytest.mark.parametrize(
    "code",
    params_from_dict(
        {
            "plugin_dict_unfiltered": """
                class MyClass:
                    _private = 42

                obj = MyClass()
                d = obj.__dict__
                assert "_private" not in d or True  # __dict__ may or may not have class attrs
            """,
            "plugin_vars_unfiltered": """
                class MyClass:
                    def __init__(self):
                        self._private = 42

                obj = MyClass()
                d = vars(obj)
                assert d["_private"] == 42
            """,
        }
    ),
)
def test_sandbox_allows_unfiltered_dict_and_vars_on_plugin_objects(code: str) -> None:
    """Test that __dict__ and vars() on plugin-defined objects include private attributes."""
    sandbox = _sandbox_from_code(code)
    sandbox.execute()


def test_urllib() -> None:
    """Test that urllib.parse (and modules like it) work, but only with the allowed attributes."""
    sandbox = _sandbox_from_code("""
        from urllib import parse
        parse.unquote(parse.quote("testing"))
    """)
    sandbox.execute()

    with pytest.raises(
        AttributeError,
        match=r'"urllib.parse.unquote_plus" is an invalid attribute name',
    ):
        sandbox = _sandbox_from_code("""
            from urllib import parse
            parse.unquote_plus("testing")
        """)
        sandbox.execute()


@pytest.mark.parametrize(
    "code",
    params_from_dict(
        {
            "class_name_via_self": """
                class Thing:
                    def __init__(self):
                        super().__init__()
                        print(f'name: {self.__class__.__name__}')

                thing = Thing()
            """,
            "class_name_via_instance": """
                class Thing:
                    pass

                thing = Thing()
                assert thing.__class__.__name__ == "Thing"
            """,
            "class_name_via_external_instance": """
                from canvas_sdk.commands import StopMedicationCommand

                obj = StopMedicationCommand(note_uuid="123")
                assert obj.__class__.__name__ == "StopMedicationCommand"
            """,
            "model_dict": """
                from canvas_sdk.commands import StopMedicationCommand

                obj = StopMedicationCommand(note_uuid="123")

                print(f'{obj.__dict__}')
                print(f'{vars(obj)}')

                obj.__dict__.get('note_uuid')
                obj.__dict__.items()

                vars(obj).get('note_uuid')
                vars(obj).items()
            """,
            "annotations_on_plugin_class": """
                class MyClass:
                    name: str
                    age: int

                assert MyClass.__annotations__ == {"name": str, "age": int}
            """,
            "annotations_on_external_class": """
                from canvas_sdk.commands import StopMedicationCommand

                annots = StopMedicationCommand.__annotations__
                assert isinstance(annots, dict)
            """,
            "typing_args_on_generic": """
                from typing import List
                tp = List[str]
                assert tp.__args__ == (str,)
            """,
            "typing_origin_on_generic": """
                from typing import List
                tp = List[str]
                assert tp.__origin__ is list
            """,
            "typing_args_via_getattr": """
                from typing import Dict
                tp = Dict[str, int]
                args = getattr(tp, '__args__', ())
                assert args == (str, int)
            """,
            "typing_origin_via_getattr": """
                from typing import Dict
                tp = Dict[str, int]
                origin = getattr(tp, '__origin__', None)
                assert origin is dict
            """,
            "typing_args_fallback_on_plain_type": """
                result = getattr(str, '__args__', 'fallback')
                assert result == 'fallback'
            """,
            "enum_members": """
                from enum import StrEnum

                class Color(StrEnum):
                    RED = "red"
                    GREEN = "green"

                members = Color.__members__
                assert "RED" in members
                assert "GREEN" in members
            """,
        }
    ),
)
def test_sandbox_allows_read_access_to_required_methods(code: str) -> None:
    """
    Some plugins introspect their class name, __dict__, etc..
    """
    sandbox = _sandbox_from_code(code)
    sandbox.execute()


@pytest.mark.parametrize(
    "code",
    params_from_dict(
        {
            "mro": """
                from canvas_sdk.commands import StopMedicationCommand

                obj = StopMedicationCommand(note_uuid="123")
                obj.__class__.__mro__[-1].__subclasses__()
            """,
            "subclasses": """
                from canvas_sdk.commands import StopMedicationCommand

                obj = StopMedicationCommand(note_uuid="123")
                obj.__class__.__subclasses__()
            """,
            "setattr": """
                from canvas_sdk.commands import StopMedicationCommand

                obj = StopMedicationCommand(note_uuid="123")
                obj.__class__.evil = "hacked"
            """,
            "dict": """
                from canvas_sdk.commands import StopMedicationCommand

                obj = StopMedicationCommand(note_uuid="123")
                obj.__class__.__dict__
            """,
            "reinit": """
                from canvas_sdk.commands import StopMedicationCommand

                obj = StopMedicationCommand(note_uuid="123")
                obj.__class__.__init__("evil")
            """,
        }
    ),
)
def test_sandbox_denies_traversal_via_external_safe_class(code: str) -> None:
    """The safe __class__ proxy should only expose __name__, nothing else."""
    sandbox = _sandbox_from_code(source_code=code)

    with pytest.raises(AttributeError):
        sandbox.execute()


def test_sandbox_allows_write_access_to_id() -> None:
    """
    Some plugins write to a variable called `id` (which is the name of a Python builtin method).
    """
    sandbox = _sandbox_from_code("id = 5")
    sandbox.execute()


def test_sandbox_dictionary_and_list_access() -> None:
    """
    Test dictionary and list read and write.
    """
    sandbox = _sandbox_from_code("""
        a = [{'b': 'c'}, {'d': 'e'}, {'f': [0, 1, 2]}]
        a[0]['b']
        a[1]['d'] = 'g'
        a[2]['f'][1]
        a[2]['f'][2] = 3
        a[2] = True
        assert a[-1] == True

        b = [0, 1, 2, 3, 4, 5]
        assert b[0:3] == [0, 1, 2]
    """)
    sandbox.execute()


def test_aug_assign() -> None:
    """
    Test that augmented assignment (AugAssign) works correctly.
    """
    sandbox = _sandbox_from_code("""
        a = 2
        a += 1
        assert a == 3

        a -= 1
        assert a == 2

        a *= -10
        assert a == -20

        a /= 2
        assert a == -10

        a_list = [0, 1, 2]
        a_list += [3]
        assert a_list == [0, 1, 2, 3]
    """)

    sandbox.execute()


def test_safe_getattr() -> None:
    """
    Test that getattr works correctly and is safe.
    """
    sandbox = _sandbox_from_code("""
        class A:
            def __init__(self):
                self.a = 'test'
                self._a = 'also works'


        a = A()

        assert getattr(a, 'a') == 'test'
        assert getattr(a, '_a') == 'also works'
    """)

    sandbox.execute()


def test_stripe_import() -> None:
    """
    Test that we can import StripeClient.
    """
    sandbox = _sandbox_from_code("""
        from canvas_sdk.clients.third_party import StripeClient

        stripe = StripeClient("")

        assert stripe is not None
    """)

    sandbox.execute()


def test_safe_getattr_fails_when_needed() -> None:
    """
    Test that getattr does not allow access to private attributes from outside the plugin.
    """
    sandbox = _sandbox_from_code("""
        from canvas_sdk.utils import Http

        client = Http()

        pvt = getattr(client, '_session')
    """)

    with pytest.raises(AttributeError, match="invalid attribute name"):
        sandbox.execute()


def test_sandbox_allows_access_to_sub_modules() -> None:
    """
    Ensure we can import from allowed sub-modules.
    """
    sandbox = _sandbox_from_code("""
        import canvas_sdk.handlers.base
        from canvas_sdk.handlers.simple_api import BasicAuthMixin
    """)

    sandbox.execute()


def test_type_of_an_sdk_object_exposes_only_its_name() -> None:
    """type() of an SDK object is a proxy carrying the class name and nothing else."""
    sandbox = _sandbox_from_code(
        """
            from canvas_sdk.utils import Http

            client = Http()

            cache_class = type(client)
            name = cache_class.__name__
            cache_class.__init__
        """
    )

    with pytest.raises(AttributeError, match="restricted"):
        sandbox.execute()

    assert sandbox.scope["name"] == "Http"


@pytest.mark.parametrize(
    "code",
    params_from_dict(
        {
            "private_attr_connection": """
                from canvas_sdk.utils import Http

                client = Http()
                pvt = client._session
            """,
            "dict_private_attr_connection": """
                from canvas_sdk.utils import Http

                client = Http()

                pvt = client.__dict__["_session"]
            """,
            "vars_private_attr_connection": """
                from canvas_sdk.utils import Http

                client = Http()

                pvt = vars(client)["_session"]
            """,
            "private_method": """
                from canvas_sdk.utils import Http

                client = Http()
                pvt = client.__setattr__("test", "test")
            """,
            "private_attr_dynamic_name": """
                from canvas_sdk.utils import Http

                client = Http()

                name = "_" + "_session"
                pvt = getattr(client, name)
            """,
            "private_attr_session": """
                from canvas_sdk.utils import Http

                client = Http()
                pvt = client._session
            """,
            "ontologies_base_url": """
                from canvas_sdk.utils.http import ontologies_http

                ontologies_http._base_url = 'evil'
            """,
            "ontologies_base_url_dict": """
                from canvas_sdk.utils.http import ontologies_http

                ontologies_http.__dict__['_base_url'] = 'evil'
            """,
            "ontologies_base_url_vars": """
                from canvas_sdk.utils.http import ontologies_http

                vars(ontologies_http)['_base_url'] = 'evil'
            """,
            "ontologies_session": """
                from canvas_sdk.utils.http import ontologies_http

                ontologies_http._session
            """,
        }
    ),
)
def test_sandbox_denies_access_to_private_attributes_of_external_modules(code: str) -> None:
    """Test that private attribute/method access is not allowed for external modules."""
    sandbox = _sandbox_from_code(source_code=code)

    with pytest.raises((AttributeError, KeyError)):
        sandbox.execute()


@pytest.mark.parametrize(
    "code",
    params_from_dict(
        {
            "unbound_http_get": """
                from canvas_sdk.utils.http import Http, ontologies_http

                Http.get(ontologies_http, "/")
            """,
            "ontologies_delete": """
                from canvas_sdk.utils.http import ontologies_http

                ontologies_http.delete
            """,
            "science_batch_requests": """
                from canvas_sdk.utils.http import science_http

                science_http.batch_requests
            """,
            "pdf_delete": """
                from canvas_sdk.utils.pdf import pdf_generator

                pdf_generator.delete
            """,
            "pharmacy_http_client_by_value": """
                from canvas_sdk.utils.http import pharmacy_http

                clients = [v for v in vars(pharmacy_http).values()]
                clients[0]
            """,
            "portal_http_client_by_value": """
                from canvas_sdk.utils.patient_portal import patient_portal_http

                clients = list(patient_portal_http.__dict__.values())
                clients[0]
            """,
        }
    ),
)
@patch("requests.Session.get")
@patch("requests.Session.delete")
def test_sandbox_keeps_service_client_internals_out_of_reach(
    mock_delete: MagicMock, mock_get: MagicMock, code: str
) -> None:
    """Plugin code reaches only a service client's exported methods."""
    sandbox = _sandbox_from_code(source_code=code)

    with pytest.raises((AttributeError, IndexError)):
        sandbox.execute()

    mock_get.assert_not_called()
    mock_delete.assert_not_called()


@pytest.mark.parametrize(
    "code",
    params_from_dict(
        {
            "logger_attribute": """
                from logger import log

                log.logger
            """,
            "logger_handlers": """
                from logger import log

                log.logger.handlers
            """,
            "logger_by_getattr": """
                from logger import log

                getattr(log, "logger")
            """,
            "logger_dict": """
                from logger import log

                log.__dict__
            """,
            "logger_by_value": """
                from logger import log

                list(vars(log).values())[0]
            """,
        }
    ),
)
def test_sandbox_plugin_logger_exposes_only_its_logging_methods(code: str) -> None:
    """Plugin code reaches only the logging methods on the exported `log`."""
    sandbox = _sandbox_from_code(source_code=code)

    with pytest.raises((AttributeError, IndexError)):
        sandbox.execute()


@pytest.mark.parametrize(
    "code",
    params_from_dict(
        {
            "vars_module_to_settings": """
                import canvas_sdk.v1.data as d

                vars(vars(d)["utils"])["settings"]
            """,
            "vars_json_to_codecs": """
                import json

                vars(json)["codecs"]
            """,
            "dict_json_to_codecs": """
                import json

                json.__dict__["codecs"]
            """,
            "dict_get_json_to_codecs": """
                import json

                assert json.__dict__.get("codecs") is None
                raise KeyError("codecs")
            """,
            "vars_values_reach_unlisted_module": """
                import json

                [v for v in vars(json).values() if getattr(v, "__name__", "") == "codecs"][0]
            """,
        }
    ),
)
def test_sandbox_vars_and_dict_on_modules_stop_at_the_allowlist(code: str) -> None:
    """vars() and __dict__ on an outside module reach only the names an import could."""
    sandbox = _sandbox_from_code(source_code=code)

    with pytest.raises((KeyError, IndexError)):
        sandbox.execute()


def test_sandbox_vars_on_modules_keeps_the_allowed_names() -> None:
    """Listing an allowed module still works: it yields what the allowlist grants."""
    sandbox = _sandbox_from_code(
        source_code="""
            import json
            import canvas_sdk.v1.data as data

            json_names = sorted(vars(json))
            dict_names = sorted(json.__dict__)
            has_patient = "Patient" in vars(data)
            models = [name for name, obj in vars(data).items() if hasattr(obj, "objects")]
        """
    )

    scope = sandbox.execute()

    assert scope["json_names"] == ["JSONDecodeError", "dump", "dumps", "load", "loads"]
    assert scope["dict_names"] == scope["json_names"]
    assert scope["has_patient"] is True
    assert "Patient" in scope["models"]


def test_sandbox_llm_json_models_with_deferred_annotations_validate() -> None:
    """Nested-model validation sees the types of a plugin's deferred annotations.

    The models live in a module the handler imports, which is how the loader publishes a
    plugin module before pydantic resolves the module's annotations against it.
    """
    sandbox = _sandbox_from_code(
        source_code="""
            from plugin_name.handlers.models import InvalidReport, Report

            valid = Report.validate_nested_models()
            invalid = InvalidReport.validate_nested_models()
        """,
        extra_source_code="""
            from __future__ import annotations

            from pydantic import BaseModel
            from canvas_sdk.clients.llms.structures import BaseModelLlmJson

            class Section(BaseModelLlmJson):
                title: str

            class Report(BaseModelLlmJson):
                sections: list[Section]
                optional_section: Section | None

            class InvalidReport(BaseModelLlmJson):
                sections: list[BaseModel]
        """,
        extra_module_name="plugin_name.handlers.models",
    )

    scope = sandbox.execute()

    assert scope["valid"] is True
    assert scope["invalid"] is False


def test_sandbox_vars_on_an_object_with_exports_lists_only_its_exports() -> None:
    """An object that declares __exports__ shows nothing else through vars()."""
    sandbox = _sandbox_from_code(
        source_code="""
            from logger import log

            names = sorted(vars(log))
        """
    )

    scope = sandbox.execute()

    assert scope["names"] == []


@pytest.mark.parametrize(
    ("imports", "expression"),
    [
        ("import requests", "requests.exceptions.RequestException"),
        ("import requests", "requests.exceptions.Timeout"),
        ("import requests", "requests.exceptions.HTTPError"),
        ("import requests", "requests.exceptions.ConnectionError"),
        ("import requests", "requests.exceptions.JSONDecodeError"),
        ("from requests.exceptions import Timeout", "Timeout"),
        ("import requests", "requests.HTTPError"),
        ("import requests", "requests.Timeout"),
        ("import requests", "requests.Request"),
        ("import re", "re.escape('a.b')"),
        ("import re", "re.finditer('a', 'aa')"),
        ("import re", "re.S | re.M | re.MULTILINE"),
        ("import uuid", "uuid.uuid5(uuid.NAMESPACE_URL, 'x')"),
        ("import urllib.parse", "urllib.parse.urlparse('https://a/b')"),
        ("import urllib.parse", "urllib.parse.parse_qs('a=1')"),
        ("import arrow", "arrow.parser.ParserError"),
        ("import arrow", "arrow.parser.ParserMatchError"),
        ("import arrow", "arrow.Arrow"),
        ("import hashlib", "hashlib.sha1(b'x').hexdigest()"),
        ("import json", "json.dump"),
        ("import json", "json.load"),
        ("import random", "random.random() + random.choice([1]) + random.sample([1], 1)[0]"),
        ("import random", "random.Random(1).random()"),
        ("import time", "time.monotonic() + time.perf_counter()"),
        ("import operator", "operator.or_(1, 2)"),
    ],
)
def test_sandbox_allows_harmless_names_plugins_read_at_request_time(
    imports: str, expression: str
) -> None:
    """Names plugin helper functions read at request time that grant nothing new."""
    sandbox = _sandbox_from_code(
        source_code="""
            from plugin_name.handlers.helper import use

            result = use()
        """,
        extra_source_code=f"""
            {imports}

            def use():
                return {expression}
        """,
        extra_module_name="plugin_name.handlers.helper",
    )

    sandbox.execute()


@pytest.mark.parametrize(
    ("module", "allowed"),
    [
        (
            "requests.exceptions",
            ["ConnectionError", "HTTPError", "JSONDecodeError", "RequestException", "Timeout"],
        ),
        ("arrow.parser", ["ParserError", "ParserMatchError"]),
    ],
)
def test_sandbox_allowlisted_submodules_expose_only_their_granted_names(
    module: str, allowed: list[str]
) -> None:
    """A submodule reachable as an attribute leads nowhere past the names it grants."""
    sandbox = _sandbox_from_code(
        source_code=f"""
            import {module.split(".")[0]}

            target = {module}
            names = sorted(vars(target))
            dict_names = sorted(target.__dict__)
            builtins_entry = target.__dict__.get("__builtins__")
        """
    )

    scope = sandbox.execute()

    assert scope["names"] == allowed
    assert scope["dict_names"] == allowed
    assert scope["builtins_entry"] is None

    for attribute in ("sys", "os", "__builtins__", "__loader__", "__spec__"):
        probe = _sandbox_from_code(
            source_code=f"""
                import {module.split(".")[0]}

                {module}.{attribute}
            """
        )

        with pytest.raises(AttributeError):
            probe.execute()


def test_sandbox_reads_attributes_of_the_plugins_own_modules() -> None:
    """`from pkg import module as m; m.NAME` reads the plugin's own module, which the
    import allowlist does not cover and does not need to.
    """
    sandbox = _sandbox_from_code(
        source_code="""
            from plugin_name.handlers import helper as h
            import plugin_name.handlers.helper

            value = h.PAP_TEST
            dotted = plugin_name.handlers.helper.PAP_TEST
        """,
        extra_source_code="""
            PAP_TEST = "pap"
        """,
        extra_module_name="plugin_name.handlers.helper",
    )

    scope = sandbox.execute()

    assert scope["value"] == "pap"
    assert scope["dotted"] == "pap"


def test_sandbox_vars_on_the_plugins_own_module_is_unfiltered() -> None:
    """A plugin's own modules are its own; vars() on them is the real namespace."""
    sandbox = _sandbox_from_code(
        source_code="""
            from plugin_name.handlers import helper

            names = vars(helper)
        """,
        extra_source_code="""
            _private = 1
            public = 2
        """,
        extra_module_name="plugin_name.handlers.helper",
    )

    scope = sandbox.execute()

    assert scope["names"]["_private"] == 1
    assert scope["names"]["public"] == 2


def test_sandbox_plugin_logger_still_logs(caplog: pytest.LogCaptureFixture) -> None:
    """Every logging method plugins use keeps working."""
    sandbox = _sandbox_from_code(
        source_code="""
            from logger import log

            log.debug("d")
            log.info("i %s", 1)
            log.warning("w")
            log.error("e")
            log.critical("c %s", 2)
            try:
                raise ValueError("boom")
            except ValueError:
                log.exception("x")
        """
    )

    with caplog.at_level(logging.INFO, logger="plugin_runner_logger"):
        sandbox.execute()

    assert "i 1" in caplog.text
    assert "c 2" in caplog.text
    assert "boom" in caplog.text


@pytest.mark.parametrize("mode", [SandboxMode.STRICT, SandboxMode.LEGACY_PERMISSIVE])
@patch("requests.Session.get")
def test_sandbox_timeout_override_inside_a_function_applies_to_get_json(
    mock_get: MagicMock, mode: SandboxMode
) -> None:
    """The shape Hyperscribe uses: lower the timeout in a helper, then call get_json."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"ok": True}

    sandbox = _sandbox_from_code(
        source_code="""
            from canvas_sdk.utils.http import ontologies_http

            def lookup(url):
                ontologies_http._MAX_REQUEST_TIMEOUT_SECONDS = 7
                return ontologies_http.get_json(url).json()

            result = lookup("/fdb/x")
        """
    )
    sandbox.mode = mode

    try:
        scope = sandbox.execute()
    finally:
        del ontologies_http._MAX_REQUEST_TIMEOUT_SECONDS

    assert scope["result"] == {"ok": True}
    assert mock_get.call_args.kwargs["timeout"] == 7


@patch("requests.Session.get")
def test_sandbox_service_client_errors_are_plain_request_exceptions(mock_get: MagicMock) -> None:
    """A failed service request surfaces in plugin code as a plain RequestException."""
    request = requests.Request("GET", "https://ontologies.canvasmedical.com/x").prepare()
    request.headers["Authorization"] = "service-credential"
    mock_get.side_effect = requests.Timeout("timed out", request=request)

    sandbox = _sandbox_from_code(
        source_code="""
            from canvas_sdk.utils.http import ontologies_http

            ontologies_http._MAX_REQUEST_TIMEOUT_SECONDS = 0.0001
            try:
                ontologies_http.get_json("/x")
            except Exception as e:
                attached_request = e.request
        """
    )

    scope = sandbox.execute()

    assert scope["attached_request"] is None


@pytest.mark.parametrize(
    "code",
    params_from_dict(
        {
            "ontologies_http": """
                from canvas_sdk.utils.http import ontologies_http

                ontologies_http._MAX_REQUEST_TIMEOUT_SECONDS = 120
            """,
            "science_http": """
                from canvas_sdk.utils.http import science_http

                science_http._MAX_REQUEST_TIMEOUT_SECONDS = 120
            """,
        }
    ),
)
def test_sandbox_allows_max_timeout_override_with_deprecation_warning(
    code: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Overriding _MAX_REQUEST_TIMEOUT_SECONDS on http clients should be allowed but log a warning."""
    sandbox = _sandbox_from_code(source_code=code)

    with caplog.at_level(logging.WARNING, logger="plugin_runner_logger"):
        sandbox.execute()

    assert "deprecated" in caplog.text.lower()
    assert "_MAX_REQUEST_TIMEOUT_SECONDS" in caplog.text


@pytest.mark.parametrize(
    ("code", "error_message"),
    params_from_dict(
        {
            "setattr": (
                """
                    from canvas_sdk.utils import Http
                    client = Http()
                    setattr(client, "_session", None)
                """,
                'invalid attribute name because it starts with "_"',
            ),
            "assign": (
                """
                    from canvas_sdk.utils import Http
                    client = Http()
                    client.get = None
                """,
                "Forbidden assignment",
            ),
            "module": (
                """
                    import json
                    json.dumps = None
                """,
                "Forbidden assignment",
            ),
            "tricky-module": (
                """
                    import json
                    other_name = json
                    other_name.dumps = None
                    assert json.dumps is not None
                """,
                "Forbidden assignment",
            ),
            "http": (
                """
                    from canvas_sdk.utils import Http
                    Http._session = None
                """,
                "Forbidden assignment",
            ),
        }
    ),
)
def test_sandbox_denies_setattr_to_protected_resources(
    code: str,
    error_message: str,
) -> None:
    """Test that setting attributes on protected resources is not allowed."""
    sandbox = _sandbox_from_code(source_code=code)

    with pytest.raises((AttributeError, TypeError), match=error_message):
        sandbox.execute()


@pytest.mark.parametrize(
    "configdict_code",
    [
        """
            from pydantic import BaseModel, ConfigDict

            class MyModel(BaseModel):
                model_config = ConfigDict(
                    extra='ignore',
                )
                name: str

            # Test that it works
            instance = MyModel(name="test", unwanted_field="ignored")
            result = f"Success: {instance.name}"
        """,
        """
            from pydantic import BaseModel, ConfigDict

            class StrictModel(BaseModel):
                model_config = ConfigDict(
                    extra='forbid',
                    str_strip_whitespace=True,
                    validate_assignment=True,
                )
                name: str
                age: int

            # Test that it works
            instance = StrictModel(name="  test  ", age=25)
            result = f"Name: '{instance.name}', Age: {instance.age}"
        """,
    ],
)
def test_sandbox_allows_configdict_import_and_usage(configdict_code: str) -> None:
    """Test that ConfigDict can be imported and used in sandbox."""
    sandbox = _sandbox_from_code(configdict_code)
    scope = sandbox.execute()

    # Check that the code executed successfully and produced expected results
    assert "result" in scope, "ConfigDict test code did not execute properly"
    assert "Success:" in scope["result"] or "Name:" in scope["result"], (
        f"ConfigDict usage failed: {scope.get('result')}"
    )


def test_importlib_reload_does_not_strip_sandbox_protections() -> None:
    """An updated helper module keeps the sandbox's import rules after a reload.

    The helper is first loaded into sys.modules, then changed on disk to import a
    module from inside a function. Re-evaluating the plugin must still refuse that
    import when the function runs.
    """
    import sys as _sys

    temp_directory = Path(mkdtemp())

    # Create plugin_name/protocols/ with __init__.py
    protocols_dir = temp_directory / "plugin_name" / "protocols"
    protocols_dir.mkdir(parents=True)
    (protocols_dir / "__init__.py").touch()

    # Create plugin_name/__init__.py
    (temp_directory / "plugin_name" / "__init__.py").touch()

    # Create an initial (safe) version of the helper module
    helpers_file = temp_directory / "plugin_name" / "helpers.py"
    helpers_file.write_text(
        dedent("""
        def do_something():
            return "safe"
    """)
    )

    # Simulate a prior load: add the temp directory to sys.path and import the module
    _sys.path.insert(0, str(temp_directory))
    try:
        # Import the safe version so it lands in sys.modules
        if "plugin_name" in _sys.modules:
            del _sys.modules["plugin_name"]
        if "plugin_name.helpers" in _sys.modules:
            del _sys.modules["plugin_name.helpers"]

        import plugin_name.helpers  # noqa: F811

        assert plugin_name.helpers.do_something() == "safe"

        # Update the helper on disk
        helpers_file.write_text(
            dedent("""
            def do_something():
                import os
                return os.getcwd()
        """)
        )

        # Create the main protocol that imports and calls the updated helper
        protocol_file = protocols_dir / "protocol.py"
        protocol_file.write_text(
            dedent("""
            from plugin_name.helpers import do_something
            result = do_something()
        """)
        )

        sandbox = sandbox_from_module(temp_directory, "plugin_name.protocols.protocol")

        with pytest.raises(ImportError, match="is not an allowed import"):
            sandbox.execute()
    finally:
        _sys.path.remove(str(temp_directory))
        # Clean up sys.modules
        for mod_name in list(_sys.modules):
            if mod_name.startswith("plugin_name"):
                del _sys.modules[mod_name]


def test_updated_module_code_is_loaded() -> None:
    """
    Test that when a same-package module's code changes on disk, the new version
    is loaded by the sandbox (not the stale cached version from sys.modules).
    """
    import sys as _sys

    temp_directory = Path(mkdtemp())

    # Create plugin_name/protocols/ with __init__.py
    protocols_dir = temp_directory / "plugin_name3" / "protocols"
    protocols_dir.mkdir(parents=True)
    (protocols_dir / "__init__.py").touch()
    (temp_directory / "plugin_name3" / "__init__.py").touch()

    # Create an initial version of the helper module
    helpers_file = temp_directory / "plugin_name3" / "helpers.py"
    helpers_file.write_text(
        dedent("""
        def get_version():
            return "v1"
    """)
    )

    _sys.path.insert(0, str(temp_directory))
    try:
        # Import the v1 module so it lands in sys.modules
        import plugin_name3.helpers  # noqa: F811

        assert plugin_name3.helpers.get_version() == "v1"

        # Update the module on disk to v2
        helpers_file.write_text(
            dedent("""
            def get_version():
                return "v2"
        """)
        )

        # Create a protocol that imports the helper
        protocol_file = protocols_dir / "protocol.py"
        protocol_file.write_text(
            dedent("""
            from plugin_name3.helpers import get_version
            result = get_version()
        """)
        )

        sandbox = sandbox_from_module(temp_directory, "plugin_name3.protocols.protocol")
        scope = sandbox.execute()

        # Should get the updated v2, not the stale v1
        assert scope["result"] == "v2"
    finally:
        _sys.path.remove(str(temp_directory))
        for mod_name in list(_sys.modules):
            if mod_name.startswith("plugin_name3"):
                del _sys.modules[mod_name]


@pytest.mark.parametrize(
    "code",
    params_from_dict(
        {
            "function_def": """
                def sneaky():
                    import os
                    return os.listdir('.')

                result = sneaky()
            """,
            "classmethod": """
                class Exploit:
                    @classmethod
                    def run(cls):
                        import os
                        return os.listdir('.')

                result = Exploit.run()
            """,
            "staticmethod": """
                class Exploit:
                    @staticmethod
                    def run():
                        import os
                        return os.listdir('.')

                result = Exploit.run()
            """,
            "lambda_import": """
                result = (lambda: __import__('os').listdir('.'))()
            """,
            "nested_function": """
                def outer():
                    def inner():
                        import os
                        return os.listdir('.')
                    return inner()

                result = outer()
            """,
            "classmethod_from_import": """
                class Exploit:
                    @classmethod
                    def run(cls):
                        from os import listdir
                        return listdir('.')

                result = Exploit.run()
            """,
        }
    ),
)
def test_deferred_import_denied(code: str) -> None:
    """Test that deferred imports (inside functions, classmethods, etc.) are still blocked."""
    sandbox = _sandbox_from_code(code)

    with pytest.raises(ImportError, match="is not an allowed import"):
        sandbox.execute()


def test_uncalled_method_import_blocked_at_runtime() -> None:
    """A forbidden import inside an uncalled method is blocked at runtime
    by ``_safe_import`` preserved in the sandbox scope.

    ``sandbox.execute()`` only invokes ``_safe_import`` for imports that
    actually run at module load time.  A method that is *defined* but never
    *called* during exec slips through exec itself.  However, because the
    sandbox scope retains ``_safe_import`` as ``__import__``, the forbidden
    import is caught when the method is actually called at runtime.
    """
    source = dedent("""
        class Exploit:
            def sneaky(self):
                import os
                return os.listdir('.')
    """)

    # The sandbox exec does NOT catch this — sneaky() is never called during exec.
    sandbox = _sandbox_from_code(source)
    scope = sandbox.execute()

    # But calling the method at runtime DOES trigger _safe_import.
    exploit = scope["Exploit"]()
    with pytest.raises(ImportError, match="'os' is not an allowed import"):
        exploit.sneaky()


def _make_plugin_tree(tmp_path: Path, plugin_name: str, tree: dict[str, str]) -> Path:
    """Create a plugin directory tree from a dict of {relative_path: source_code}."""
    base = tmp_path / plugin_name
    for rel_path, source in tree.items():
        file_path = base / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(dedent(source))
    return tmp_path


def test_manager_raw_blocked() -> None:
    """Test that Manager.raw() is blocked to prevent arbitrary SQL execution."""
    sandbox = _sandbox_from_code("""
        from canvas_sdk.v1.data.patient import Patient

        Patient.objects.raw("SELECT 1")
    """)

    with pytest.raises(PermissionError, match="raw\\(\\) queries are not allowed"):
        sandbox.execute()


# ---------------------------------------------------------------------------
# Bulk QuerySet operation wrapper tests
# ---------------------------------------------------------------------------


class _BulkTestModel(CustomModel):
    """A model for testing bulk operation wrappers."""

    class Meta:
        app_label = "test"
        managed = False

    text_field = django_models.TextField(null=True)


# --- Permission denied ---


def test_bulk_create_denied_in_read_only_context() -> None:
    """bulk_create() should raise NamespaceWriteDenied in a read-only namespace context."""
    with (
        plugin_database_context("test_plugin", namespace="ns", access_level="read"),
        pytest.raises(NamespaceWriteDenied, match="read-only"),
    ):
        _BulkTestModel.objects.bulk_create([_BulkTestModel()])  # type: ignore[attr-defined]


def test_bulk_update_denied_in_read_only_context() -> None:
    """bulk_update() should raise NamespaceWriteDenied in a read-only namespace context."""
    with (
        plugin_database_context("test_plugin", namespace="ns", access_level="read"),
        pytest.raises(NamespaceWriteDenied, match="read-only"),
    ):
        _BulkTestModel.objects.bulk_update([_BulkTestModel()], fields=["text_field"])  # type: ignore[attr-defined]


def test_queryset_delete_denied_in_read_only_context() -> None:
    """QuerySet.delete() should raise NamespaceWriteDenied in a read-only namespace context."""
    with (
        plugin_database_context("test_plugin", namespace="ns", access_level="read"),
        pytest.raises(NamespaceWriteDenied, match="read-only"),
    ):
        _BulkTestModel.objects.all().delete()  # type: ignore[attr-defined]


def test_queryset_update_denied_in_read_only_context() -> None:
    """QuerySet.update() should raise NamespaceWriteDenied in a read-only namespace context."""
    with (
        plugin_database_context("test_plugin", namespace="ns", access_level="read"),
        pytest.raises(NamespaceWriteDenied, match="read-only"),
    ):
        _BulkTestModel.objects.all().update(text_field="new")  # type: ignore[attr-defined]


# --- Size limits ---


def test_bulk_create_exceeds_size_limit() -> None:
    """bulk_create() should raise BulkOperationTooLarge when exceeding MAX_BULK_SIZE."""
    test_limit = 3
    objs = [_BulkTestModel() for _ in range(test_limit + 1)]
    with (
        patch("canvas_sdk.MAX_BULK_SIZE", test_limit),
        plugin_database_context("test_plugin", namespace="ns", access_level="read_write"),
        pytest.raises(BulkOperationTooLarge, match=f"{test_limit + 1:,}"),
    ):
        _BulkTestModel.objects.bulk_create(objs)  # type: ignore[attr-defined]


def test_bulk_update_exceeds_size_limit() -> None:
    """bulk_update() should raise BulkOperationTooLarge when exceeding MAX_BULK_SIZE."""
    test_limit = 3
    objs = [_BulkTestModel() for _ in range(test_limit + 1)]
    with (
        patch("canvas_sdk.MAX_BULK_SIZE", test_limit),
        plugin_database_context("test_plugin", namespace="ns", access_level="read_write"),
        pytest.raises(BulkOperationTooLarge, match=f"{test_limit + 1:,}"),
    ):
        _BulkTestModel.objects.bulk_update(objs, fields=["text_field"])  # type: ignore[attr-defined]


# --- Field size validation ---


def test_bulk_create_field_size_validation() -> None:
    """bulk_create() should raise FieldValueTooLarge for oversized fields."""
    obj = _BulkTestModel(text_field="x" * (MAX_FIELD_SIZE + 1))
    with (
        plugin_database_context("test_plugin", namespace="ns", access_level="read_write"),
        pytest.raises(FieldValueTooLarge, match="text_field"),
    ):
        _BulkTestModel.objects.bulk_create([obj])  # type: ignore[attr-defined]


def test_bulk_update_field_size_validation() -> None:
    """bulk_update() should raise FieldValueTooLarge for oversized fields."""
    obj = _BulkTestModel(text_field="x" * (MAX_FIELD_SIZE + 1))
    with (
        plugin_database_context("test_plugin", namespace="ns", access_level="read_write"),
        pytest.raises(FieldValueTooLarge, match="text_field"),
    ):
        _BulkTestModel.objects.bulk_update([obj], fields=["text_field"])  # type: ignore[attr-defined]


# --- Allowed operations ---


def test_bulk_create_allowed_in_read_write_context() -> None:
    """bulk_create() should succeed in a read_write context within limits."""
    objs = [_BulkTestModel()]
    with (
        plugin_database_context("test_plugin", namespace="ns", access_level="read_write"),
        patch("canvas_sdk._original_bulk_create", return_value=objs) as mock,
    ):
        result = _BulkTestModel.objects.bulk_create(objs)  # type: ignore[attr-defined]
        mock.assert_called_once()
        assert result == objs


def test_bulk_update_allowed_in_read_write_context() -> None:
    """bulk_update() should succeed in a read_write context within limits."""
    objs = [_BulkTestModel()]
    with (
        plugin_database_context("test_plugin", namespace="ns", access_level="read_write"),
        patch("canvas_sdk._original_bulk_update", return_value=1) as mock,
    ):
        result = _BulkTestModel.objects.bulk_update(objs, fields=["text_field"])  # type: ignore[attr-defined]
        mock.assert_called_once()
        assert result == 1


def test_queryset_delete_allowed_in_read_write_context() -> None:
    """QuerySet.delete() should succeed in a read_write context."""
    with (
        plugin_database_context("test_plugin", namespace="ns", access_level="read_write"),
        patch("canvas_sdk._original_qs_delete", return_value=(0, {})) as mock,
    ):
        result = _BulkTestModel.objects.all().delete()  # type: ignore[attr-defined]
        mock.assert_called_once()
        assert result == (0, {})


def test_queryset_update_allowed_in_read_write_context() -> None:
    """QuerySet.update() should succeed in a read_write context."""
    with (
        plugin_database_context("test_plugin", namespace="ns", access_level="read_write"),
        patch("canvas_sdk._original_qs_update", return_value=0) as mock,
    ):
        result = _BulkTestModel.objects.all().update(text_field="new")  # type: ignore[attr-defined]
        mock.assert_called_once()
        assert result == 0


# ---------------------------------------------------------------------------
# Import containment: strict vs. legacy-permissive sandbox modes
# ---------------------------------------------------------------------------


IMPORT_PLUGIN_TREE = {
    "__init__.py": "package_value = 'package'\n",
    "handlers/__init__.py": "",
    "handlers/handler.py": """
        from import_plugin.helper import helper_value

        result = helper_value
    """,
    "helper.py": """
        helper_value = 'helper'


        def read_cwd():
            import os

            return os.getcwd()
    """,
}


@contextmanager
def _importable_plugin(tmp_path: Path, plugin_name: str, tree: dict[str, str]) -> Iterator[Path]:
    """Build a plugin tree whose parent is on `sys.path`, as it is in production.

    `plugin_runner` appends the plugin directory to `sys.path`, which is what makes
    the real import system able to load plugin files at all.
    """
    base_path = _make_plugin_tree(tmp_path, plugin_name, tree)
    sys.path.insert(0, str(base_path))

    try:
        yield base_path
    finally:
        sys.path.remove(str(base_path))

        for module_name in [
            module_name
            for module_name in sys.modules
            if module_name == plugin_name or module_name.startswith(f"{plugin_name}.")
        ]:
            del sys.modules[module_name]


def _builtin_names(module: types.ModuleType) -> set[str]:
    """Return the names available as builtins to code defined in `module`."""
    raw = module.__dict__.get("__builtins__", {})

    return set(raw if isinstance(raw, dict) else vars(raw))


def test_strict_import_publishes_sandboxed_submodule(tmp_path: Path) -> None:
    """A plugin submodule reached by import is the sandbox-built module.

    `__import__` executes the file from disk outside the sandbox and caches that copy
    in `sys.modules`, so every function the module defines would resolve names against
    the real builtins at call time.
    """
    with _importable_plugin(tmp_path, "import_plugin", IMPORT_PLUGIN_TREE) as base_path:
        sandbox_from_module(base_path, "import_plugin.handlers.handler").execute()

        names = _builtin_names(sys.modules["import_plugin.helper"])

        assert "exec" not in names
        assert "open" not in names
        assert "eval" not in names


def test_strict_import_publishes_sandboxed_parent_package(tmp_path: Path) -> None:
    """Ancestor packages of an imported module are sandbox-built too.

    Evaluating only the leaf leaves `__import__` to load every parent `__init__.py`
    from disk with real builtins.
    """
    with _importable_plugin(tmp_path, "import_plugin", IMPORT_PLUGIN_TREE) as base_path:
        sandbox_from_module(base_path, "import_plugin.handlers.handler").execute()

        assert "exec" not in _builtin_names(sys.modules["import_plugin"])
        assert sys.modules["import_plugin"].package_value == "package"


def test_strict_import_blocks_deferred_import_in_plugin_module(tmp_path: Path) -> None:
    """A deferred import inside an imported plugin module still goes through the sandbox."""
    with _importable_plugin(tmp_path, "import_plugin", IMPORT_PLUGIN_TREE) as base_path:
        sandbox_from_module(base_path, "import_plugin.handlers.handler").execute()

        with pytest.raises(ImportError, match="'os' is not an allowed import."):
            sys.modules["import_plugin.helper"].read_cwd()


def test_strict_import_of_dotted_name_evaluates_the_whole_chain(tmp_path: Path) -> None:
    """`import a.b.c` sandbox-evaluates and publishes every package along the way."""
    tree = {
        "__init__.py": "",
        "handlers/__init__.py": "",
        "handlers/handler.py": """
            import walk_plugin.nested.leaf

            result = 'imported'
        """,
        "nested/__init__.py": "",
        "nested/leaf.py": "leaf_value = 'leaf'\n",
    }

    with _importable_plugin(tmp_path, "walk_plugin", tree) as base_path:
        scope = sandbox_from_module(base_path, "walk_plugin.handlers.handler").execute()

        assert scope["result"] == "imported"

        for module_name in ("walk_plugin", "walk_plugin.nested", "walk_plugin.nested.leaf"):
            assert "exec" not in _builtin_names(sys.modules[module_name])

        # Each package is linked to its child, the way the real import system would.
        assert sys.modules["walk_plugin"].nested is sys.modules["walk_plugin.nested"]
        assert sys.modules["walk_plugin.nested"].leaf is sys.modules["walk_plugin.nested.leaf"]


def test_strict_import_of_name_from_nested_plugin_module(tmp_path: Path) -> None:
    """`from a.b.c import name` resolves against the sandbox-built module."""
    tree = {
        "__init__.py": "",
        "handlers/__init__.py": "",
        "handlers/handler.py": """
            from fromlist_plugin.nested.leaf import leaf_value

            result = leaf_value
        """,
        "nested/__init__.py": "",
        "nested/leaf.py": "leaf_value = 'leaf'\n",
    }

    with _importable_plugin(tmp_path, "fromlist_plugin", tree) as base_path:
        scope = sandbox_from_module(base_path, "fromlist_plugin.handlers.handler").execute()

        assert scope["result"] == "leaf"


def test_strict_mode_is_the_default() -> None:
    """A sandbox built without an explicit mode is fully contained."""
    sandbox = _sandbox_from_code("result = 1")

    assert sandbox.mode is SandboxMode.STRICT


def test_nested_sandboxes_inherit_the_mode(tmp_path: Path) -> None:
    """The mode propagates to the sandboxes built for imported plugin modules."""
    with _importable_plugin(tmp_path, "import_plugin", IMPORT_PLUGIN_TREE) as base_path:
        sandbox_from_module(
            base_path,
            "import_plugin.handlers.handler",
            mode=SandboxMode.LEGACY_PERMISSIVE,
        ).execute()

        # A strict nested sandbox would have published its own module object here.
        assert "exec" in _builtin_names(sys.modules["import_plugin.helper"])


def test_legacy_permissive_allows_dangerous_method_names() -> None:
    """`RESTRICTED_METHOD_NAMES` is enforced only by the strict mode."""
    code = """
        from canvas_sdk.v1.data.patient import Patient

        result = Patient.mro
    """

    with pytest.raises(AttributeError, match="restricted method name"):
        _sandbox_from_code(code).execute()

    permissive = _sandbox_from_code(code)
    permissive.mode = SandboxMode.LEGACY_PERMISSIVE

    assert permissive.execute()["result"] is not None


def test_strict_import_supports_a_package_importing_itself(tmp_path: Path) -> None:
    """A package whose `__init__.py` imports its own submodule loads under strict rules.

    The real import system publishes a module before executing its body, so a circular
    import resolves to the partially-initialized module. Publishing only afterwards
    makes `from pkg import sub` inside `pkg/__init__.py` fail to resolve.
    """
    tree = {
        "__init__.py": """
            from circular_plugin import helpers

            __all__ = ["helpers"]
        """,
        "helpers/__init__.py": "helper_value = 'helper'\n",
        "handlers/__init__.py": "",
        "handlers/handler.py": """
            from circular_plugin.helpers import helper_value

            result = helper_value
        """,
    }

    with _importable_plugin(tmp_path, "circular_plugin", tree) as base_path:
        scope = sandbox_from_module(base_path, "circular_plugin.handlers.handler").execute()

        assert scope["result"] == "helper"


def test_strict_import_reports_the_real_error_on_every_handler(tmp_path: Path) -> None:
    """A module that fails to execute reports the same cause to each importer.

    Modules are marked evaluated before they run, so leaving the mark in place after a
    failure makes the next importer skip evaluation and report the module as missing
    instead of reporting why it failed.
    """
    tree = {
        "__init__.py": "",
        "broken/__init__.py": "",
        "broken/mailer.py": "import smtplib\n",
        "handlers/__init__.py": "",
        "handlers/first.py": "from poison_plugin.broken.mailer import smtplib\n",
        "handlers/second.py": "from poison_plugin.broken.mailer import smtplib\n",
    }

    with _importable_plugin(tmp_path, "poison_plugin", tree) as base_path:
        evaluated: EvaluatedModules = {}

        for handler in ("first", "second"):
            sandbox = sandbox_from_module(base_path, f"poison_plugin.handlers.{handler}", evaluated)

            with pytest.raises(ImportError, match="'smtplib' is not an allowed import."):
                sandbox.execute()


def test_strict_import_does_not_publish_a_module_that_failed(tmp_path: Path) -> None:
    """A module whose body raised is not left visible in `sys.modules`."""
    tree = {
        "__init__.py": "",
        "handlers/__init__.py": "",
        "handlers/handler.py": "from halfbuilt_plugin.bad import value\n",
        "bad.py": "import smtplib\n\nvalue = 1\n",
    }

    with _importable_plugin(tmp_path, "halfbuilt_plugin", tree) as base_path:
        sandbox = sandbox_from_module(base_path, "halfbuilt_plugin.handlers.handler")

        with pytest.raises(ImportError):
            sandbox.execute()

        assert "halfbuilt_plugin.bad" not in sys.modules


def test_strict_import_resolves_relative_imports(tmp_path: Path) -> None:
    """A relative import inside a plugin resolves against the importing module's package.

    `from .sibling import x` reaches `_safe_import` as the bare name `sibling`, which is
    neither the plugin's package nor an allowed module, so leaving `level` unapplied
    rejects a plugin's own module as a forbidden import.
    """
    tree = {
        "__init__.py": """
            from relative_plugin import protocols

            __all__ = ["protocols"]
        """,
        "protocols/__init__.py": """
            from .api import api_value

            __all__ = ["api_value"]
        """,
        "protocols/api.py": "api_value = 'api'\n",
        "handlers/__init__.py": "",
        "handlers/handler.py": """
            from relative_plugin.protocols.api import api_value

            result = api_value
        """,
    }

    with _importable_plugin(tmp_path, "relative_plugin", tree) as base_path:
        scope = sandbox_from_module(base_path, "relative_plugin.handlers.handler").execute()

        assert scope["result"] == "api"


def test_strict_import_resolves_parent_relative_imports(tmp_path: Path) -> None:
    """A `from ..pkg import x` import resolves against the grandparent package."""
    tree = {
        "__init__.py": "",
        "shared/__init__.py": "shared_value = 'shared'\n",
        "handlers/__init__.py": "",
        "handlers/handler.py": """
            from ..shared import shared_value

            result = shared_value
        """,
    }

    with _importable_plugin(tmp_path, "parent_relative_plugin", tree) as base_path:
        scope = sandbox_from_module(base_path, "parent_relative_plugin.handlers.handler").execute()

        assert scope["result"] == "shared"


def test_strict_import_rejects_relative_import_past_the_plugin_root(tmp_path: Path) -> None:
    """Walking past the top-level package with `..` is refused, not resolved outward."""
    tree = {
        "__init__.py": "",
        "handlers/__init__.py": "",
        "handlers/handler.py": "from ... import something\n",
    }

    with _importable_plugin(tmp_path, "upward_relative_plugin", tree) as base_path:
        sandbox = sandbox_from_module(base_path, "upward_relative_plugin.handlers.handler")

        with pytest.raises(ImportError, match="beyond top-level package"):
            sandbox.execute()


def test_strict_import_of_a_class_from_a_package(tmp_path: Path) -> None:
    """`from pkg import SomeClass` works when the name is an attribute, not a submodule.

    A name in the `fromlist` that has no module file is a class or constant. Probing for
    it as a submodule raises FileNotFoundError on the path that does not exist.
    """
    tree = {
        "__init__.py": "",
        # `child` imports `BaseModel` back out of this package while this package is
        # still executing, so the name has to be visible mid-initialization.
        "models/__init__.py": """
            class BaseModel:
                label = 'base'


            from attr_plugin.models.child import Child
        """,
        "models/child.py": """
            from attr_plugin.models import BaseModel


            class Child(BaseModel):
                label = 'child'
        """,
        "handlers/__init__.py": "",
        "handlers/handler.py": """
            from attr_plugin.models import BaseModel, Child

            result = f"{BaseModel.label}/{Child.label}"
        """,
    }

    with _importable_plugin(tmp_path, "attr_plugin", tree) as base_path:
        scope = sandbox_from_module(base_path, "attr_plugin.handlers.handler").execute()

        assert scope["result"] == "base/child"


def test_strict_import_of_a_missing_name_raises_import_error(tmp_path: Path) -> None:
    """A name that is neither a submodule nor an attribute is an ImportError."""
    tree = {
        "__init__.py": "",
        "models/__init__.py": "value = 1\n",
        "handlers/__init__.py": "",
        "handlers/handler.py": "from missing_name_plugin.models import NotThere\n",
    }

    with _importable_plugin(tmp_path, "missing_name_plugin", tree) as base_path:
        sandbox = sandbox_from_module(base_path, "missing_name_plugin.handlers.handler")

        with pytest.raises(ImportError, match="cannot import name 'NotThere'"):
            sandbox.execute()


@pytest.mark.parametrize(
    "code,expected",
    params_from_dict(
        {
            "positional": ('result = "hello {}".format("world")', "hello world"),
            "numbered": ('result = "{0}-{1}".format("a", "b")', "a-b"),
            "repeated": ('result = "{0}{0}".format("a")', "aa"),
            "named": ('result = "{who}!".format(who="you")', "you!"),
            "spec": ('result = "{:>6.2f}".format(3.14159)', "  3.14"),
            "conversion": ("result = \"{!r}\".format('x')", "'x'"),
            "format_map": ('result = "{a}/{b}".format_map({"a": 1, "b": 2})', "1/2"),
        }
    ),
)
def test_str_format_substitutes_normally(code: str, expected: str) -> None:
    """Formatting a value is allowed; it is the traversal that is not."""
    assert _sandbox_from_code(code).execute()["result"] == expected


@pytest.mark.parametrize(
    "template",
    params_from_dict(
        {
            "attribute": '"{0.__class__}"',
            "chained_attribute": '"{0.__class__.__init__.__globals__}"',
            "item": '"{0[0]}"',
            "named_attribute": '"{value.__class__}"',
        }
    ),
)
def test_str_format_cannot_traverse_into_its_arguments(template: str) -> None:
    """The format mini-language does its own lookups, which the guards do not see.

    `"{0.__class__.__init__.__globals__}".format(x)` reaches the real builtins without
    `_safe_getattr` or `_safe_getitem` ever being consulted.
    """
    sandbox = _sandbox_from_code(f"result = {template}.format([1], value=[1])")

    with pytest.raises(NotImplementedError, match="inside a format string is not allowed"):
        sandbox.execute()


def test_str_format_through_the_type_is_refused() -> None:
    """`str.format(template, ...)` would reach the real method, so it stays blocked."""
    sandbox = _sandbox_from_code('result = str.format("{0.__class__}", "x")')

    with pytest.raises(NotImplementedError, match="through the `str` type"):
        sandbox.execute()


def test_a_blessed_import_works_under_the_current_rules(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A plugin named in the blessing list may import and use its extra module.

    The plugin keeps the current rule set and gains only that import, rather than being
    put on the deprecated rules wholesale.
    """
    tree = {
        "__init__.py": "",
        "handlers/__init__.py": "",
        "handlers/handler.py": """
            import sqlite3

            from blessed_plugin.helpers import kind

            result = kind(sqlite3)
        """,
        "helpers.py": "def kind(module):\n    return module.paramstyle\n",
    }

    monkeypatch.setattr(
        sandbox_module, "is_blessed_import", lambda plugin, module: module == "sqlite3"
    )

    with _importable_plugin(tmp_path, "blessed_plugin", tree) as base_path:
        scope = sandbox_from_module(base_path, "blessed_plugin.handlers.handler").execute()

        assert scope["result"] == "qmark"


def test_an_unblessed_import_is_still_refused(tmp_path: Path) -> None:
    """Without a blessing the module stays outside the plugin's reach."""
    tree = {
        "__init__.py": "",
        "handlers/__init__.py": "",
        "handlers/handler.py": "import sqlite3\n",
    }

    with _importable_plugin(tmp_path, "unblessed_plugin", tree) as base_path:
        sandbox = sandbox_from_module(base_path, "unblessed_plugin.handlers.handler")

        with pytest.raises(ImportError, match="'sqlite3' is not an allowed import."):
            sandbox.execute()


@pytest.mark.parametrize(
    "code,expected",
    params_from_dict(
        {
            "zlib_roundtrip": (
                "import zlib\n\nresult = zlib.decompress(zlib.compress(b'hello'))",
                b"hello",
            ),
            "zlib_from_import": (
                "from zlib import compress, decompress\n\nresult = decompress(compress(b'hi'))",
                b"hi",
            ),
            "elementtree_dotted": (
                "import xml.etree.ElementTree as ET\n\n"
                "result = ET.fromstring('<r><a>x</a></r>').find('a').text",
                "x",
            ),
            "elementtree_from_package": (
                "from xml.etree import ElementTree\n\n"
                "result = ElementTree.fromstring('<r>y</r>').text",
                "y",
            ),
            "elementtree_from_module": (
                "from xml.etree.ElementTree import fromstring\n\n"
                "result = fromstring('<r>z</r>').text",
                "z",
            ),
        }
    ),
)
def test_compression_and_xml_parsing_are_allowed(code: str, expected: object) -> None:
    """Neither reaches a file, a socket or a subprocess, so both are within the sandbox."""
    assert _sandbox_from_code(code).execute()["result"] == expected


def test_xml_parsing_does_not_resolve_external_entities() -> None:
    """The reason XML parsing is allowed: it reads nothing off the machine.

    Internal entities expand, which can be made expensive, but a plugin can already
    spend arbitrary time in a loop. An external entity would be a capability, and is
    refused by the parser rather than by the sandbox — so this pins that behavior.
    """
    document = (
        '<?xml version="1.0"?><!DOCTYPE r [ <!ENTITY x SYSTEM "file:///etc/passwd"> ]><r>&x;</r>'
    )
    sandbox = _sandbox_from_code(
        f"import xml.etree.ElementTree as ET\n\nresult = ET.fromstring({document!r})"
    )

    with pytest.raises(Exception, match="undefined entity"):
        sandbox.execute()


def test_deferred_plugin_import_survives_losing_the_global_module_entry(tmp_path: Path) -> None:
    """A handler's deferred import resolves against the load that built it.

    A reload that is refused keeps the previous version's handlers serving after the
    plugin's `sys.modules` entries have been dropped, so those handlers must not depend
    on the process-wide table to find their own modules.
    """
    tree = {
        "__init__.py": "",
        "handlers/__init__.py": "",
        "helpers.py": "value = 'v1'\n",
        "handlers/handler.py": """
            from survives_plugin import helpers


            def later():
                from survives_plugin.helpers import value

                return value


            result = later
        """,
    }

    with _importable_plugin(tmp_path, "survives_plugin", tree) as base_path:
        scope = sandbox_from_module(base_path, "survives_plugin.handlers.handler").execute()

        for module_name in [m for m in sys.modules if m.startswith("survives_plugin")]:
            del sys.modules[module_name]

        assert scope["result"]() == "v1"


@pytest.mark.parametrize(
    "expression",
    params_from_dict({"vars": "vars(Effect)", "dunder_dict": "Effect.__dict__"}),
)
def test_a_class_namespace_from_outside_the_plugin_has_no_private_names(expression: str) -> None:
    """A class's namespace is a mappingproxy, so it is filtered like any other mapping."""
    sandbox = _sandbox_from_code(
        f"""
            from canvas_sdk.effects import Effect

            namespace = {expression}
            result = [key for key in namespace if key.startswith("_")]
        """
    )

    assert sandbox.execute()["result"] == []
