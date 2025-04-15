import importlib
import re
from collections.abc import Generator
from textwrap import dedent
from typing import Any

import pytest
from pytest_mock import MockerFixture

from plugin_runner.sandbox import (
    ALLOWED_MODULES,
    CANVAS_SUBMODULES,
    FORBIDDEN_ASSIGNMENTS,
    PROTECTED_RESOURCES,
    Sandbox,
)


def _sandbox_from_code(source_code: str, namespace: str | None = None) -> Sandbox:
    """
    Helper method to dedent the passed in source code so our tests are more readable.
    """
    return Sandbox(source_code=dedent(source_code), namespace=namespace)


# Sample code strings for testing various scenarios
VALID_CODE = """
    x = 10
    y = 20
    result = x + y
"""

CODE_WITH_RESTRICTED_IMPORTS = [
    """
        from canvas_sdk.commands.tests.schema.tests import settings
    """,
    """
        import os
        result = os.listdir('.')
    """,
    """
        from django.core.cache import caches

        cache = caches['default']
    """,
]

CODE_WITH_FORBIDDEN_FUNC_NAME = """
    builtins = {}
"""


CODE_WITH_PRIVATE_ACCESS_EXTERNAL_MODULES = [
    """
        from canvas_sdk.caching.plugins import get_cache

        cache = get_cache()
        pvt = cache._connection
    """,
    """
        from canvas_sdk.caching.plugins import get_cache

        cache = get_cache()

        pvt = cache.__dict__["_connection"]
    """,
    """
        from canvas_sdk.caching.plugins import get_cache

        cache = get_cache()
        pvt = cache._make_key("test")
    """,
    """
        from canvas_sdk.caching.plugins import get_cache

        cache = get_cache()

        name = "_" + "private_attr"
        pvt = _getattr_(cache, name)
    """,
    """
        from canvas_sdk.caching.plugins import get_cache

        cache = get_cache()
        pvt = cache.__connection
    """,
    """
        from canvas_sdk.caching.plugins import get_cache

        cache = get_cache()

        pvt = cache.__dict__["__connection"]
    """,
    """
        from canvas_sdk.caching.plugins import get_cache

        cache = get_cache()
        pvt = cache.__class__
    """,
]

CODE_WITH_ASSIGNMENTS_TO_PROTECTED_RESOURCES = [
    """
        from canvas_sdk.caching.plugins import get_cache
        cache = get_cache()
        setattr(cache, "_connection", None)
    """,
    """
        from canvas_sdk.caching.plugins import get_cache
        cache = get_cache()
        cache.set = None
    """,
    """
        import json
        json.dumps = None
    """,
    """
        from canvas_sdk.caching.base import Cache
        Cache._connection = None
    """,
]


SOURCE_CODE_MODULE = """
    import module.b
    result = module.b
"""

CODE_WITH_FORBIDDEN_ASSIGNMENTS = [
    code
    for var in FORBIDDEN_ASSIGNMENTS
    for code in [
        f"{var} = 'test'",
        f"test = {var} = 'test'",
        f"test = {var} = test2 = 'test'",
        f"(a, (b, c), (d, ({var}, f))) = (1, (2, 3), (4, (5, 6)))",
        f"(a, (b, c), (d, [{var}, f])) = (1, (2, 3), (4, [5, 6]))",
    ]
]


@pytest.fixture
def mock_allowed_modules(mocker: "MockerFixture", request: Any) -> Generator:
    """Mock the ALLOWED_MODULES."""
    mocker.patch("plugin_runner.sandbox.ALLOWED_MODULES", request.param)

    yield


@pytest.fixture
def mock_protected_resources(mocker: "MockerFixture", request: Any) -> Generator:
    """Mock the PROTECTED_RESOURCES."""
    mocker.patch("plugin_runner.sandbox.PROTECTED_RESOURCES", request.param)

    yield


def test_valid_code_execution() -> None:
    """Test execution of valid code in the sandbox."""
    sandbox = _sandbox_from_code(VALID_CODE)
    scope = sandbox.execute()
    assert scope["result"] == 30, "The code should compute result as 30."


@pytest.mark.parametrize(
    "code", CODE_WITH_RESTRICTED_IMPORTS, ids=["settings", "os", "django_cache"]
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


RE_ERROR_STRINGS = re.compile(
    r"""(
        'settings'\ is\ not\ an\ allowed\ import|
        cannot\ import\ name\ 'settings'|
        future\ feature\ settings\ is\ not\ defined
    )""",
    flags=re.VERBOSE,
)


@pytest.mark.parametrize("canvas_module", CANVAS_SUBMODULES)
def test_all_modules_implement_canvas_allowed_attributes(canvas_module: str) -> None:
    """
    Test that no module in ALLOWED_MODULES re-exports settings.
    """
    imported_module = importlib.import_module(canvas_module)

    assert hasattr(imported_module, "__canvas_allowed_attributes__")
    assert isinstance(imported_module.__canvas_allowed_attributes__, tuple)


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

    with pytest.raises((ImportError, SyntaxError), match=RE_ERROR_STRINGS):
        sandbox.execute()


def test_plugin_runner_re_export_1() -> None:
    """
    Test what is re-exported by our code.
    """
    sandbox = _sandbox_from_code(
        """
            import canvas_sdk.caching.plugins
            canvas_sdk.caching.plugins.get_cache_client()
        """
    )

    with pytest.raises(AttributeError):
        sandbox.execute()


def test_plugin_runner_re_export_2() -> None:
    """
    Test what is re-exported by our code.
    """
    sandbox = _sandbox_from_code(
        """
            import canvas_sdk.caching.plugins
            canvas_sdk.caching.plugins.CANVAS_SDK_CACHE_TIMEOUT_SECONDS
        """
    )

    with pytest.raises(AttributeError):
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


def test_forbidden_name() -> None:
    """Test that forbidden function names are blocked by Transformer."""
    sandbox = _sandbox_from_code(CODE_WITH_FORBIDDEN_FUNC_NAME)
    with pytest.raises(RuntimeError, match="Code is invalid"):
        sandbox.execute()


@pytest.mark.parametrize("code", CODE_WITH_FORBIDDEN_ASSIGNMENTS)
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


def test_sandbox_denies_module_name_import_outside_package() -> None:
    """Test that modules outside the root package cannot be imported."""
    sandbox_module_a = _sandbox_from_code(
        source_code=SOURCE_CODE_MODULE, namespace="other_module.a"
    )

    with pytest.raises(ImportError, match="module.b' is not an allowed import."):
        sandbox_module_a.execute()


def test_sandbox_allows_access_to_private_attributes_same_module() -> None:
    """Test that private attribute/method access is allowed for the same module/package."""
    sandbox = _sandbox_from_code("""
        class MyClass:
            _private_attr = 42

        pvt = MyClass()._private_attr
    """)

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
            from canvas_sdk.caching.plugins import get_cache

            cache = get_cache()

            cache_class = type(cache)
        """
    )

    with pytest.raises(NameError, match="name 'type' is not defined"):
        sandbox.execute()


def test_get_cache_client_is_inaccessible() -> None:
    """Test that get_cache_client from the plugins module is inaccessible."""
    sandbox = _sandbox_from_code(
        source_code="from canvas_sdk.caching.plugins import get_cache_client"
    )

    with pytest.raises(ImportError, match="is not an allowed import."):
        sandbox.execute()


@pytest.mark.parametrize(
    "code",
    CODE_WITH_PRIVATE_ACCESS_EXTERNAL_MODULES,
    ids=[
        "private_attr_connection",
        "dict_private_attr_connection",
        "private_method",
        "private_attr_dynamic_name",
        "private_attr__conection",
        "dict_private_attr__connection",
        "private_attr__class__",
    ],
)
def test_sandbox_denies_access_to_private_attributes_of_external_modules(code: str) -> None:
    """Test that private attribute/method access is not allowed for external modules."""
    sandbox = _sandbox_from_code(source_code=code)

    with pytest.raises(AttributeError):
        sandbox.execute()


@pytest.mark.parametrize(
    ("code", "error_message", "mock_protected_resources", "mock_allowed_modules"),
    [
        (
            CODE_WITH_ASSIGNMENTS_TO_PROTECTED_RESOURCES[0],
            "attribute-less object",
            PROTECTED_RESOURCES,
            ALLOWED_MODULES,
        ),
        (
            CODE_WITH_ASSIGNMENTS_TO_PROTECTED_RESOURCES[1],
            "Forbidden assignment",
            PROTECTED_RESOURCES,
            ALLOWED_MODULES,
        ),
        (
            CODE_WITH_ASSIGNMENTS_TO_PROTECTED_RESOURCES[2],
            "Forbidden assignment",
            ["json"],
            ALLOWED_MODULES,
        ),
    ],
    ids=["setattr", "assign", "module"],
    indirect=["mock_protected_resources", "mock_allowed_modules"],
)
def test_sandbox_denies_setattr_to_protected_resources(
    code: str, error_message: str, mock_protected_resources: None, mock_allowed_modules: None
) -> None:
    """Test that setting attributes on protected resources is not allowed."""
    sandbox = _sandbox_from_code(source_code=code)

    with pytest.raises(TypeError, match=error_message):
        sandbox.execute()
