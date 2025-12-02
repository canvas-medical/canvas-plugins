import functools
import json
from collections.abc import Generator
from pathlib import Path
from typing import Any, NotRequired, TypedDict

import yaml
from jsonschema import Draft7Validator, validators

from canvas_sdk.utils.plugins import plugin_context


class Response(TypedDict):
    """A Response of a Questionnaire."""

    name: str
    code: str
    value: NotRequired[str]
    code_description: NotRequired[str]


class EnabledCondition(TypedDict):
    """An enablement condition for branching logic in a Question."""

    question_code: str
    operator: str
    value_code: NotRequired[str | None]
    value_string: NotRequired[str | None]


class Question(TypedDict):
    """A Question of a Questionnaire."""

    code_system: str
    code: str
    content: str
    responses_code_system: str
    responses_type: str
    responses: list[Response]
    code_description: NotRequired[str]
    display_result_in_social_history_section: NotRequired[bool]
    enabled_behavior: NotRequired[str]
    enabled_conditions: NotRequired[list[EnabledCondition]]


class QuestionnaireConfig(TypedDict):
    """A Questionnaire configuration."""

    name: str
    form_type: str
    code_system: str
    code: str
    can_originate_in_charting: bool
    questions: list[Question]
    prologue: NotRequired[str]
    display_results_in_social_history_section: NotRequired[bool]


def extend_with_defaults(validator_class: type[Draft7Validator]) -> type[Draft7Validator]:
    """Extend a Draft7Validator with default values for properties."""
    validate_properties = validator_class.VALIDATORS["properties"]
    validate_items = validator_class.VALIDATORS["items"]

    def set_defaults(
        validator: Draft7Validator,
        properties: dict[str, Any],
        instance: dict[str, Any],
        schema: dict[str, Any],
    ) -> Generator[Any, None, None]:
        for property, subschema in properties.items():
            if "default" in subschema:
                instance.setdefault(property, subschema["default"])

        yield from validate_properties(
            validator,
            properties,
            instance,
            schema,
        )

    def set_items_defaults(
        validator: Draft7Validator,
        items: dict[str, Any] | list[dict[str, Any]],
        instance: list[Any],
        schema: dict[str, Any],
    ) -> Generator[Any, None, None]:
        # Apply defaults to items in arrays
        if isinstance(items, dict) and "properties" in items:
            for item in instance:
                if isinstance(item, dict):
                    for property, subschema in items["properties"].items():
                        if "default" in subschema:
                            item.setdefault(property, subschema["default"])

        yield from validate_items(
            validator,
            items,
            instance,
            schema,
        )

    return validators.extend(
        validator_class,
        {"properties": set_defaults, "items": set_items_defaults},
    )


ExtendedDraft7Validator = extend_with_defaults(Draft7Validator)


def validate_yaml(yaml_content: str) -> QuestionnaireConfig:
    """Validate a YAML string against the Questionnaire schema."""
    questionnaire_config = yaml.load(yaml_content, Loader=yaml.SafeLoader)
    ExtendedDraft7Validator(json_schema()).validate(questionnaire_config)
    return questionnaire_config


@plugin_context
def from_yaml(questionnaire_name: str, **kwargs: Any) -> QuestionnaireConfig | None:
    """Load a Questionnaire configuration from a YAML file.

    Args:
        questionnaire_name (str): The path to the questionnaire file, relative to the plugin package.
            If the path starts with a forward slash ("/"), it will be stripped during resolution.
        kwargs (Any): Additional keyword arguments.

    Returns:
        QuestionnaireConfig: The loaded Questionnaire configuration.

    Raises:
        FileNotFoundError: If the questionnaire file does not exist within the plugin's directory
            or if the resolved path is invalid.
        PermissionError: If the resolved path is outside the plugin's directory.
        ValidationError: If the questionnaire file does not conform to the JSON schema.
    """
    plugin_dir = kwargs.get("plugin_dir")
    if not plugin_dir:
        raise ValueError("plugin_dir is required when loading from file")

    questionnaire_config_path = Path(plugin_dir / questionnaire_name.lstrip("/")).resolve()

    if not questionnaire_config_path.is_relative_to(plugin_dir):
        raise PermissionError(f"Invalid Questionnaire '{questionnaire_name}'")
    elif not questionnaire_config_path.exists():
        raise FileNotFoundError(f"Questionnaire {questionnaire_name} not found.")

    yaml_content = questionnaire_config_path.read_text()
    return validate_yaml(yaml_content)


@functools.cache
def json_schema() -> dict[str, Any]:
    """Reads the JSON schema for a Questionnaire Config."""
    schema = json.loads(
        (Path(__file__).resolve().parent.parent.parent / "schemas/questionnaire.json").read_text()
    )

    return schema


def to_yaml(questionnaire_config: QuestionnaireConfig) -> str:
    """
    Convert a QuestionnaireConfig to YAML string.
    """
    return yaml.dump(
        questionnaire_config,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True
    )

__exports__ = (
    "Draft7Validator",
    "EnabledCondition",
    "ExtendedDraft7Validator",
    "Question",
    "QuestionnaireConfig",
    "Response",
    "from_yaml",
    "to_yaml",
    "validate_yaml",
)
