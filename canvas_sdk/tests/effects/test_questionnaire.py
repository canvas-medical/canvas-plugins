import json

import pytest

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.questionnaire import CreateQuestionnaire


@pytest.fixture
def valid_questionnaire_yaml() -> str:
    """Fixture that provides a valid YAML string for questionnaire creation."""
    return """
    name: Sample Questionnaire
    can_originate_in_charting: true
    form_type: QUES
    display_results_in_social_history_section: false
    code_system: LOINC
    code: '123456'
    content: System
    questions:
    - content: Question 1
        code_system: SNOMED
        code: '456789'
        responses_type: SING
        responses_code_system: SNOMED
        display_result_in_social_history_section: false
        enabled_behavior: 'all'
        enabled_conditions:
        - question_code: '456789'
            operator: '='
            value_code: 'xxxx'
        responses:
        - name: Good
            code: xxxx
            value: '0'
            code_description: ''
        - name: Bad
            code: yyyy
            value: '1'
            code_description: ''
        - name: Unknown
            code: zzzz
            value: '3'
            code_description: ''
    """


@pytest.fixture
def create_questionnaire_effect(valid_questionnaire_yaml: str) -> CreateQuestionnaire:
    """Fixture that provides a CreateQuestionnaire instance with valid YAML."""
    return CreateQuestionnaire(questionnaire_yaml=valid_questionnaire_yaml)


def test_create_questionnaire_success(
    create_questionnaire_effect: CreateQuestionnaire, valid_questionnaire_yaml: str
) -> None:
    """Test successful questionnaire creation."""
    effect = create_questionnaire_effect.apply()

    assert effect.type == EffectType.CREATE_QUESTIONNAIRE
    payload = json.loads(effect.payload)
    assert payload["data"]["questionnaire_yaml"] == valid_questionnaire_yaml


def test_values_property(
    create_questionnaire_effect: CreateQuestionnaire, valid_questionnaire_yaml: str
) -> None:
    """Test that the values property returns the correct questionnaire_yaml mapping."""
    assert create_questionnaire_effect.values == {"questionnaire_yaml": valid_questionnaire_yaml}


def test_effect_type_is_correct() -> None:
    """Test that the Meta.effect_type is set correctly."""
    assert CreateQuestionnaire.Meta.effect_type == EffectType.CREATE_QUESTIONNAIRE
