import importlib
import logging
import re
from pathlib import Path
from tempfile import mkdtemp
from textwrap import dedent
from unittest.mock import patch

import pytest
from django.db import models as django_models

from canvas_sdk.tests.shared import params_from_dict
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
    Sandbox,
    sandbox_from_module,
)

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
        extra_plugin_directory = temp_directory.joinpath(*extra_module_name.split(",")[:-1])
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
            from arrow import parser  # fails here
            parser.sys
        """,
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
                obj.__class__.__mro__
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


def test_type_is_inaccessible() -> None:
    """Test that type() is inaccessible."""
    sandbox = _sandbox_from_code(
        """
            from canvas_sdk.utils import Http

            client = Http()

            cache_class = type(client)
        """
    )

    with pytest.raises(NameError, match="name 'type' is not defined"):
        sandbox.execute()


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
                pvt = _getattr_(client, name)
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

    with pytest.raises(AttributeError):
        sandbox.execute()


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
                "attribute-less object",
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
