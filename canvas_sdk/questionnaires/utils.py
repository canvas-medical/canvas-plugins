from pathlib import Path
from typing import Any, TypedDict

import yaml

from canvas_sdk.utils.plugins import plugin_only


class Response(TypedDict):
    """A Response of a Questionnaire."""

    name: str
    code: str
    code_description: str
    value: str


class Question(TypedDict):
    """A Question of a Questionnaire."""

    name: str
    code_system: str
    code: str
    code_description: str
    content: str
    responses_code_system: str
    responses_type: str
    use_in_shx: bool
    responses: list[Response]


class QuestionnaireConfig(TypedDict):
    """A Questionnaire configuration."""

    name: str
    use_case_in_charting: str
    code_system: str
    code: str
    can_originate_in_charting: bool
    search_tags: str
    scoring_code_system: str
    scoring_code: str
    content: str
    prologue: str
    use_in_shx: bool
    expected_completion_time: float
    questions: list[Question]


@plugin_only
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
    """
    plugin_dir = kwargs["plugin_dir"]
    questionnaire_config_path = Path(plugin_dir / questionnaire_name.lstrip("/")).resolve()

    if not questionnaire_config_path.is_relative_to(plugin_dir):
        raise PermissionError(f"Invalid Questionnaire '{questionnaire_name}'")
    elif not questionnaire_config_path.exists():
        raise FileNotFoundError(f"Questionnaire {questionnaire_name} not found.")

    questionnaire_config = yaml.load(questionnaire_config_path.read_text(), Loader=yaml.SafeLoader)

    return questionnaire_config
