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
