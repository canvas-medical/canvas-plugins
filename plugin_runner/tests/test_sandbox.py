import importlib
import re
from pathlib import Path
from tempfile import mkdtemp
from textwrap import dedent

import pytest

from canvas_sdk.tests.shared import params_from_dict
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
    module_name: str = "plugin_name.protocols.protocol",
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

    with pytest.raises((ImportError, SyntaxError), match=RE_ERROR_STRINGS):
        sandbox.execute()


@pytest.mark.parametrize("allowed_module", ALLOWED_MODULES)
def test_plugin_runner_os_allowed_module_import(allowed_module: str) -> None:
    """
    Test that no module in ALLOWED_MODULES re-exports settings.
    """
    sandbox = _sandbox_from_code(f"from {allowed_module} import os")

    with pytest.raises((ImportError, SyntaxError), match=RE_ERROR_STRINGS):
        sandbox.execute()


@pytest.mark.parametrize("allowed_module", ALLOWED_MODULES)
def test_plugin_runner_sys_allowed_module_import(allowed_module: str) -> None:
    """
    Test that no module in ALLOWED_MODULES re-exports settings.
    """
    sandbox = _sandbox_from_code(f"from {allowed_module} import sys")

    with pytest.raises((ImportError, SyntaxError), match=RE_ERROR_STRINGS):
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
        parse.quote("testing")
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
            "class_name": """
                class Thing:
                    def __init__(self):
                        super().__init__()
                        print(f'name: {self.__class__.__name__}')

                thing = Thing()
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
        }
    ),
)
def test_sandbox_allows_read_access_to_required_methods(code: str) -> None:
    """
    Some plugins introspect their class name, __dict__, etc..
    """
    sandbox = _sandbox_from_code(code)
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
            "private_attr__class__": """
                from canvas_sdk.utils import Http

                client = Http()
                pvt = client.__class__
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
    assert "Success:" in scope["result"] or "Name:" in scope["result"], f"ConfigDict usage failed: {scope.get('result')}"
