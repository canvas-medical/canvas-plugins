from typing import Any

import pytest
from pytest_mock import MockerFixture

from plugin_runner.sandbox import (
    ALLOWED_MODULES,
    FORBIDDEN_ASSIGNMENTS,
    PROTECTED_RESOURCES,
    Sandbox,
)

# Sample code strings for testing various scenarios
VALID_CODE = """
x = 10
y = 20
result = x + y
"""

CODE_WITH_RESTRICTED_IMPORT = """
import os
result = os.listdir('.')
"""

CODE_WITH_PLUGIN_RUNNER_SETTING_IMPORT = """
import settings
result = settings.AWS_SECRET_ACCESS_KEY
"""

CODE_WITH_ALLOWED_IMPORT = """
import json
result = json.dumps({"key": "value"})
"""

CODE_WITH_FORBIDDEN_FUNC_NAME = """
builtins = {}
"""


CODE_WITH_PRIVATE_ACCESS = [
    """
class MyClass:
  _private_attr = 42

pvt = MyClass()._private_attr
""",
]

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
def mock_allowed_modules(mocker: "MockerFixture", request: Any) -> None:
    """Mock the ALLOWED_MODULES."""
    mocker.patch("plugin_runner.sandbox.ALLOWED_MODULES", request.param)


@pytest.fixture
def mock_protected_resources(mocker: "MockerFixture", request: Any) -> None:
    """Mock the PROTECTED_RESOURCES."""
    mocker.patch("plugin_runner.sandbox.PROTECTED_RESOURCES", request.param)


def test_valid_code_execution() -> None:
    """Test execution of valid code in the sandbox."""
    sandbox = Sandbox(VALID_CODE)
    scope = sandbox.execute()
    assert scope["result"] == 30, "The code should compute result as 30."


def test_disallowed_import() -> None:
    """Test that restricted imports are not allowed."""
    sandbox = Sandbox(CODE_WITH_RESTRICTED_IMPORT)
    with pytest.raises(ImportError, match="'os' is not an allowed import."):
        sandbox.execute()


def test_plugin_runner_settings_import() -> None:
    """Test that imports of plugin runner settings are not allowed."""
    sandbox = Sandbox(CODE_WITH_PLUGIN_RUNNER_SETTING_IMPORT)
    with pytest.raises(ImportError, match="'settings' is not an allowed import."):
        sandbox.execute()


def test_allowed_import() -> None:
    """Test that allowed imports (from ALLOWED_MODULES) work correctly."""
    sandbox = Sandbox(CODE_WITH_ALLOWED_IMPORT)
    scope = sandbox.execute()
    assert scope["result"] == '{"key": "value"}', "JSON encoding should work with allowed imports."


def test_forbidden_name() -> None:
    """Test that forbidden function names are blocked by Transformer."""
    sandbox = Sandbox(CODE_WITH_FORBIDDEN_FUNC_NAME)
    with pytest.raises(RuntimeError, match="Code is invalid"):
        sandbox.execute()


@pytest.mark.parametrize("code", CODE_WITH_FORBIDDEN_ASSIGNMENTS)
def test_forbidden_assignment(code: str) -> None:
    """Test that forbidden assignments are blocked by Transformer."""
    sandbox = Sandbox(code)
    with pytest.raises(RuntimeError, match="Code is invalid"):
        sandbox.execute()


def test_code_with_warnings() -> None:
    """Test that the sandbox captures warnings for restricted names or usage."""
    code_with_warning = """
_x = 5
result = _x
"""
    sandbox = Sandbox(code_with_warning)
    assert sandbox.warnings, "There should be warnings for using restricted names."
    scope = sandbox.execute()
    assert scope["result"] == 5, "Code should execute despite warnings."


def test_compile_errors() -> None:
    """Test that compile errors are detected for invalid syntax."""
    invalid_code = """
def missing_colon()
    return 42
"""
    sandbox = Sandbox(invalid_code)
    with pytest.raises(RuntimeError, match="Code is invalid"):
        sandbox.execute()


def test_sandbox_scope() -> None:
    """Verify the sandbox scope includes expected built-ins and utility functions."""
    sandbox = Sandbox(VALID_CODE)
    scope = sandbox.execute()
    assert "any" in scope["__builtins__"]
    assert scope["__builtins__"]["any"] == any, "'any' function should be accessible in sandbox."


def test_print_collector() -> None:
    """Ensure that PrintCollector is used for capturing prints."""
    code_with_print = """
print("Hello, Sandbox!")
"""
    sandbox = Sandbox(code_with_print)
    scope = sandbox.execute()
    assert "Hello, Sandbox!" in scope["_print"].txt, "Print output should be captured."


def test_sandbox_denies_module_name_import_outside_package() -> None:
    """Test that modules outside the root package cannot be imported."""
    sandbox_module_a = Sandbox(source_code=SOURCE_CODE_MODULE, namespace="other_module.a")
    with pytest.raises(ImportError, match="module.b' is not an allowed import."):
        sandbox_module_a.execute()


@pytest.mark.parametrize(
    "code",
    CODE_WITH_PRIVATE_ACCESS,
    ids=["private_attr"],
)
def test_sandbox_allows_access_to_private_attributes_same_module(code: str) -> None:
    """Test that private attribute/method access is allowed for the same module/package."""
    sandbox = Sandbox(source_code=code)
    sandbox.execute()


@pytest.mark.parametrize(
    "code",
    CODE_WITH_PRIVATE_ACCESS_EXTERNAL_MODULES,
    ids=[
        "private_attr",
        "dict_private_attr",
        "private_method",
        "private_attr_dynamic_name",
    ],
)
def test_sandbox_denies_access_to_private_attributes_of_external_modules(code: str) -> None:
    """Test that private attribute/method access is not allowed for external modules."""
    sandbox = Sandbox(source_code=code)
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
        (
            CODE_WITH_ASSIGNMENTS_TO_PROTECTED_RESOURCES[3],
            "Forbidden assignment",
            PROTECTED_RESOURCES,
            list(ALLOWED_MODULES) + ["canvas_sdk.caching.base"],
        ),
    ],
    ids=["setattr", "assign", "module", "class"],
    indirect=["mock_protected_resources", "mock_allowed_modules"],
)
def test_sandbox_denies_setattr_to_protected_resources(
    code: str, error_message: str, mock_protected_resources: None, mock_allowed_modules: None
) -> None:
    """Test that setting attributes on protected resources is not allowed."""
    sandbox = Sandbox(source_code=code)
    with pytest.raises(TypeError, match=error_message):
        sandbox.execute()
