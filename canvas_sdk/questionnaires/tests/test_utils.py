import json
from pathlib import Path

import pytest
import yaml

from canvas_sdk.effects import Effect
from canvas_sdk.events import Event, EventRequest, EventType
from canvas_sdk.questionnaires import from_yaml
from plugin_runner.plugin_runner import LOADED_PLUGINS
from settings import PLUGIN_DIRECTORY


@pytest.mark.parametrize("install_test_plugin", ["test_load_questionnaire"], indirect=True)
def test_from_yaml_valid_questionnaire(install_test_plugin: Path, load_test_plugins: None) -> None:
    """Test that the from_yaml function loads a valid questionnaire."""
    plugin = LOADED_PLUGINS[
        "test_load_questionnaire:test_load_questionnaire.protocols.my_protocol:ValidQuestionnaire"
    ]
    result: list[Effect] = plugin["class"](Event(EventRequest(type=EventType.UNKNOWN))).compute()

    assert json.loads(result[0].payload) == yaml.load(
        (
            Path(PLUGIN_DIRECTORY)
            / "test_load_questionnaire/questionnaires/example_questionnaire.yml"
        )
        .resolve()
        .read_text(),
        Loader=yaml.SafeLoader,
    )


@pytest.mark.parametrize("install_test_plugin", ["test_load_questionnaire"], indirect=True)
def test_from_yaml_invalid_questionnaire(
    install_test_plugin: Path, load_test_plugins: None
) -> None:
    """Test that the from_yaml function raises an error for invalid questionnaires."""
    plugin = LOADED_PLUGINS[
        "test_load_questionnaire:test_load_questionnaire.protocols.my_protocol:InvalidQuestionnaire"
    ]
    with pytest.raises(FileNotFoundError):
        plugin["class"](Event(EventRequest(type=EventType.UNKNOWN))).compute()


@pytest.mark.parametrize("install_test_plugin", ["test_load_questionnaire"], indirect=True)
def test_from_yaml_forbidden_questionnaire(
    install_test_plugin: Path, load_test_plugins: None
) -> None:
    """Test that the from_yaml function raises an error for a questionnaire outside plugin package."""
    plugin = LOADED_PLUGINS[
        "test_load_questionnaire:test_load_questionnaire.protocols.my_protocol:ForbiddenQuestionnaire"
    ]
    with pytest.raises(PermissionError):
        plugin["class"](Event(EventRequest(type=EventType.UNKNOWN))).compute()


def test_from_yaml_non_plugin_caller() -> None:
    """Test that the from_yaml function returns None when called outside a plugin."""
    assert from_yaml("questionnaires/example_questionnaire.yml") is None
