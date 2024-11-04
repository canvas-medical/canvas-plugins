import pytest

from plugin_runner.sandbox import Sandbox

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

CODE_WITH_ALLOWED_IMPORT = """
import json
result = json.dumps({"key": "value"})
"""

CODE_WITH_FORBIDDEN_FUNC_NAME = """
builtins = {}
"""

SOURCE_CODE_MODULE_OS = """
import os
result = os.listdir('.')
"""


def test_valid_code_execution() -> None:
    """Test execution of valid code in the sandbox."""
    sandbox = Sandbox(VALID_CODE)
    scope = sandbox.execute()
    assert scope["result"] == 30, "The code should compute result as 30."


def test_disallowed_import() -> None:
    """Test that restricted imports are not allowed."""
    sandbox = Sandbox(CODE_WITH_RESTRICTED_IMPORT)
    with pytest.raises(ImportError, match="os' is not an allowed import."):
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


def test_sandbox_module_name_imports_within_package() -> None:
    """Test that modules within the same package can be imported."""
    sandbox_module_a = Sandbox(source_code=SOURCE_CODE_MODULE_OS, module_name="os.a")
    result = sandbox_module_a.execute()

    assert "os" in result


def test_sandbox_denies_module_name_import_outside_package() -> None:
    """Test that modules outside the root package cannot be imported."""
    sandbox_module_a = Sandbox(source_code=SOURCE_CODE_MODULE_OS, module_name="module.a")
    with pytest.raises(ImportError, match="os' is not an allowed import."):
        sandbox_module_a.execute()
