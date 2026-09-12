import json

import pytest
import yaml
from jsonschema import ValidationError

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.questionnaire import CreateQuestionnaire
from canvas_sdk.questionnaires.utils import QuestionnaireConfig, validate_yaml


@pytest.fixture
def valid_questionnaire_yaml() -> str:
    """Fixture that provides a valid YAML string for questionnaire creation."""
    return """
name: Sample Questionnaire
can_originate_in_charting: true
form_type: QUES
code_system: LOINC
code: '123456'
questions:
  - content: Question 1
    code_system: SNOMED
    code: '456789'
    responses_type: SING
    responses_code_system: SNOMED
    responses:
      - name: Good
        code: xxxx
        value: '0'
        code_description: ''
      - name: Bad
        code: yyyy
        value: '1'
        code_description: ''
    """


@pytest.fixture
def valid_questionnaire_config(valid_questionnaire_yaml: str) -> QuestionnaireConfig:
    """Fixture providing validated QuestionnaireConfig."""
    return validate_yaml(valid_questionnaire_yaml)


@pytest.fixture
def create_questionnaire_effect(
    valid_questionnaire_config: QuestionnaireConfig,
) -> CreateQuestionnaire:
    """Fixture that provides a CreateQuestionnaire instance."""
    return CreateQuestionnaire(questionnaire_config=valid_questionnaire_config)


def test_create_questionnaire_success(
    create_questionnaire_effect: CreateQuestionnaire,
    valid_questionnaire_config: QuestionnaireConfig,
) -> None:
    """Test successful questionnaire creation with validated config."""
    effect = create_questionnaire_effect.apply()

    assert effect.type == EffectType.CREATE_QUESTIONNAIRE

    payload = json.loads(effect.payload)
    assert "questionnaire_yaml" in payload

    parsed = yaml.load(payload["questionnaire_yaml"], Loader=yaml.SafeLoader)
    assert parsed["name"] == valid_questionnaire_config["name"]
    assert parsed["form_type"] == valid_questionnaire_config["form_type"]


def test_values_property_converts_to_yaml(
    create_questionnaire_effect: CreateQuestionnaire,
) -> None:
    """Test that values property converts config to YAML string."""
    values = create_questionnaire_effect.values

    assert "questionnaire_yaml" in values
    assert isinstance(values["questionnaire_yaml"], str)

    parsed = yaml.load(values["questionnaire_yaml"], Loader=yaml.SafeLoader)
    assert parsed["name"] == "Sample Questionnaire"


def test_effect_type_is_correct() -> None:
    """Test that the Meta.effect_type is set correctly."""
    assert CreateQuestionnaire.Meta.effect_type == EffectType.CREATE_QUESTIONNAIRE


def test_validate_yaml_rejects_invalid_yaml() -> None:
    """Test that validate_yaml rejects invalid YAML."""
    invalid_yaml = "name: Test"

    with pytest.raises(ValidationError):
        validate_yaml(invalid_yaml)


def test_validate_yaml_with_yaml_content(valid_questionnaire_yaml: str) -> None:
    """Test complete workflow: YAML string → config → effect."""
    config = validate_yaml(valid_questionnaire_yaml)
    effect = CreateQuestionnaire(questionnaire_config=config)
    result = effect.apply()

    assert result.type == EffectType.CREATE_QUESTIONNAIRE


def test_programmatic_construction_with_validate_yaml() -> None:
    """Test programmatic config construction workflow - use validate_yaml for validation."""
    import yaml as yaml_lib

    config_dict = {
        "name": "Programmatic Test",
        "form_type": "QUES",
        "code_system": "INTERNAL",
        "code": "TEST_001",
        "can_originate_in_charting": True,
        "prologue": "",
        "display_results_in_social_history_section": False,
        "questions": [
            {
                "content": "Test Question",
                "code_system": "INTERNAL",
                "code": "Q1",
                "code_description": "",
                "responses_code_system": "INTERNAL",
                "responses_type": "SING",
                "display_result_in_social_history_section": False,
                "responses": [
                    {"name": "Yes", "code": "A1", "code_description": "", "value": ""},
                    {"name": "No", "code": "A2", "code_description": "", "value": ""},
                ],
            }
        ],
    }

    yaml_string = yaml_lib.dump(config_dict)
    validated_config = validate_yaml(yaml_string)
    effect = CreateQuestionnaire(questionnaire_config=validated_config)
    result = effect.apply()

    assert result.type == EffectType.CREATE_QUESTIONNAIRE
