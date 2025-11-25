from canvas_sdk.llms.structures.settings.llm_settings_gpt4 import LlmSettingsGpt4


def test_to_dict() -> None:
    """Test conversion of LlmSettingsGpt4 to dictionary format."""
    tested = LlmSettingsGpt4(
        api_key="theKey",
        model="theModel",
        temperature=2.0,
    )
    result = tested.to_dict()
    expected = {
        "model": "theModel",
        "temperature": 2.0,
    }
    assert result == expected
