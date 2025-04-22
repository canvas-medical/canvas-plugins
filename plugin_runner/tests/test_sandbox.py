import importlib
import re
from pathlib import Path
from tempfile import mkdtemp
from textwrap import dedent

import pytest

from plugin_runner.sandbox import (
    ALLOWED_MODULES,
    CANVAS_SUBMODULE_NAMES,
    FORBIDDEN_ASSIGNMENTS,
    Sandbox,
    sandbox_from_module,
)


def _sandbox_from_code(source_code: str) -> Sandbox:
    """
    Helper method to ceate a Sandbox that matches production conditions.
    """
    temp_directory = Path(mkdtemp())

    plugin_directory = temp_directory / "plugin_name" / "protocols"
    plugin_directory.mkdir(parents=True)

    init_file = plugin_directory / "__init__.py"
    init_file.touch()

    protocol_file = plugin_directory / "protocol.py"
    protocol_file.write_text(dedent(source_code))

    return sandbox_from_module(temp_directory, "plugin_name.protocols.protocol")


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
        from canvas_sdk.utils import Http

        client = Http()
        pvt = client._session
    """,
    """
        from canvas_sdk.utils import Http

        client = Http()

        pvt = client.__dict__["_session"]
    """,
    """
        from canvas_sdk.utils import Http

        client = Http()
        pvt = client.__setattr__("test", "test")
    """,
    """
        from canvas_sdk.utils import Http

        client = Http()

        name = "_" + "_session"
        pvt = _getattr_(client, name)
    """,
    """
        from canvas_sdk.utils import Http

        client = Http()
        pvt = client.__connection
    """,
    """
        from canvas_sdk.utils import Http

        client = Http()

        pvt = client.__dict__["__connection"]
    """,
    """
        from canvas_sdk.utils import Http

        client = Http()
        pvt = client.__class__
    """,
]

CODE_WITH_ASSIGNMENTS_TO_PROTECTED_RESOURCES = [
    """
        from canvas_sdk.utils import Http
        client = Http()
        setattr(client, "_session", None)
    """,
    """
        from canvas_sdk.utils import Http
        client = Http()
        client.get = None
    """,
    """
        import json
        json.dumps = None
    """,
    """
        from canvas_sdk.utils import Http
        Cache._session = None
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


@pytest.mark.parametrize("canvas_module", CANVAS_SUBMODULE_NAMES)
def test_all_modules_implement_canvas_allowed_attributes(canvas_module: str) -> None:
    """
    Test that all modules under cavas_sdk have an __exports__ module attribute
    and that it is a tuple.
    """
    imported_module = importlib.import_module(canvas_module)

    assert hasattr(imported_module, "__exports__")
    assert isinstance(imported_module.__exports__, tuple)


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


BANNED_IMPORTS = [
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
]


@pytest.mark.parametrize("banned_import", BANNED_IMPORTS)
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
    [
        """
            import jwt
            jwt.encode = lambda x: print(x)
        """,
        """
            from requests import Response
            Response.status_code = 500
        """,
    ],
)
def test_sandbox_disallows_bad_attribute_writes(banned_attribute: str) -> None:
    """
    Test that module attributes not allowlisted are denied.
    """
    sandbox = _sandbox_from_code(banned_attribute)

    with pytest.raises(TypeError, match="Forbidden assignment to a (non-)?module attribute:"):
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
    # TODO rewrite
    sandbox_module_a = _sandbox_from_code(source_code=SOURCE_CODE_MODULE)

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
            from canvas_sdk.utils import Http

            client = Http()

            cache_class = type(client)
        """
    )

    with pytest.raises(NameError, match="name 'type' is not defined"):
        sandbox.execute()


@pytest.mark.parametrize(
    "code",
    CODE_WITH_PRIVATE_ACCESS_EXTERNAL_MODULES,
    ids=[
        "private_attr_connection",
        "dict_private_attr_connection",
        "private_method",
        "private_attr_dynamic_name",
        "private_attr__session",
        "dict_private_attr__session",
        "private_attr__class__",
    ],
)
def test_sandbox_denies_access_to_private_attributes_of_external_modules(code: str) -> None:
    """Test that private attribute/method access is not allowed for external modules."""
    sandbox = _sandbox_from_code(source_code=code)

    with pytest.raises(AttributeError):
        sandbox.execute()


@pytest.mark.parametrize(
    ("code", "error_message"),
    [
        (
            CODE_WITH_ASSIGNMENTS_TO_PROTECTED_RESOURCES[0],
            "attribute-less object",
        ),
        (
            CODE_WITH_ASSIGNMENTS_TO_PROTECTED_RESOURCES[1],
            "Forbidden assignment",
        ),
        (
            CODE_WITH_ASSIGNMENTS_TO_PROTECTED_RESOURCES[2],
            "Forbidden assignment",
        ),
    ],
    ids=["setattr", "assign", "module"],
)
def test_sandbox_denies_setattr_to_protected_resources(
    code: str,
    error_message: str,
) -> None:
    """Test that setting attributes on protected resources is not allowed."""
    sandbox = _sandbox_from_code(source_code=code)

    with pytest.raises(TypeError, match=error_message):
        sandbox.execute()
