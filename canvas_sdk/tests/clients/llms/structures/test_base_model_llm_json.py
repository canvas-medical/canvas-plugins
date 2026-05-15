import builtins
import sys
import types

from pydantic import BaseModel
from pydantic.alias_generators import to_camel

from canvas_sdk.clients.llms.structures.base_model_llm_json import BaseModelLlmJson


def test_sub_class() -> None:
    """Test BaseModelLlmJson is a BaseModel with the correct config."""
    tested = BaseModelLlmJson
    assert issubclass(tested, BaseModel)

    result_extra = tested.model_config.get("extra")
    expected = "forbid"
    assert result_extra == expected

    result_alias = tested.model_config.get("alias_generator")
    assert result_alias is to_camel


def test_validate_nested_models() -> None:
    """Test the nested validation."""

    class ValidSub(BaseModelLlmJson):
        field: str
        sub: BaseModelLlmJson

    class InvalidSub(BaseModelLlmJson):
        field: str
        sub: BaseModel

    class Valid(BaseModelLlmJson):
        field: str
        sub: BaseModelLlmJson
        sub_sub: ValidSub
        sub_or_none: BaseModelLlmJson | None
        sub_optional: BaseModelLlmJson | None

    class Invalid(BaseModelLlmJson):
        field: str
        sub: BaseModelLlmJson
        sub_sub: InvalidSub
        sub_or_none: BaseModelLlmJson | None
        sub_optional: BaseModelLlmJson | None

    class InvalidField1(BaseModelLlmJson):
        field: str
        sub: BaseModel
        sub_or_none: BaseModelLlmJson | None
        sub_optional: BaseModelLlmJson | None

    class InvalidField2(BaseModelLlmJson):
        field: str
        sub: BaseModelLlmJson
        sub_or_none: BaseModel | None
        sub_optional: BaseModelLlmJson | None

    class InvalidField3(BaseModelLlmJson):
        field: str
        sub: BaseModelLlmJson
        sub_or_none: BaseModelLlmJson | None
        sub_optional: BaseModel | None

    tests = [
        (Valid, True),
        (Invalid, False),
        (InvalidField1, False),
        (InvalidField2, False),
        (InvalidField3, False),
    ]
    for idx, (tested, expected) in enumerate(tests):
        assert issubclass(tested, BaseModelLlmJson)
        result = tested.validate_nested_models()
        assert result is expected, f"---> {idx}"


def _create_deferred_annotation_module() -> types.ModuleType:
    """Create a synthetic module simulating `from __future__ import annotations`."""
    # This is intentionally using dynamic code execution to simulate the synthetic
    # module environment that the plugin sandbox creates. This is a test helper, not
    # production code.
    module_name = "__test_deferred_annotations__"
    synthetic_module = types.ModuleType(module_name)
    synthetic_module.__dict__["__name__"] = module_name
    sys.modules[module_name] = synthetic_module

    source = (
        "from __future__ import annotations\n"
        "\n"
        "from pydantic import BaseModel\n"
        "from canvas_sdk.clients.llms.structures.base_model_llm_json import BaseModelLlmJson\n"
        "\n"
        "\n"
        "class Section(BaseModelLlmJson):\n"
        "    title: str\n"
        "    content: str\n"
        "\n"
        "\n"
        "class Report(BaseModelLlmJson):\n"
        "    name: str\n"
        "    sections: list[Section]\n"
        "    optional_section: Section | None\n"
        "\n"
        "\n"
        "class InvalidReport(BaseModelLlmJson):\n"
        "    name: str\n"
        "    sections: list[BaseModel]\n"
    )
    code = compile(source, module_name, "exec")
    # Safe: static test fixture code, not user input.
    builtins.exec(code, synthetic_module.__dict__)  # noqa: S102
    return synthetic_module


def test_validate_nested_models_with_deferred_annotations() -> None:
    """Test validation works when models are defined in a module using `from __future__ import annotations`.

    Simulates the synthetic-module scenario where annotations are strings/ForwardRef
    instead of actual types.
    """
    try:
        synthetic_module = _create_deferred_annotation_module()

        Report = synthetic_module.__dict__["Report"]
        InvalidReport = synthetic_module.__dict__["InvalidReport"]

        assert Report.validate_nested_models() is True
        assert InvalidReport.validate_nested_models() is False
    finally:
        sys.modules.pop("__test_deferred_annotations__", None)
