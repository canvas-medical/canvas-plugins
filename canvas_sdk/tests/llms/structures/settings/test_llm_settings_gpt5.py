from canvas_sdk.llms.structures.settings.llm_settings_gpt5 import LlmSettingsGpt5


def test_to_dict() -> None:
    """Test conversion of LlmSettingsGpt5 to dictionary format."""
    tested = LlmSettingsGpt5(
        api_key="theKey",
        model="theModel",
        reasoning_effort="medium",
        text_verbosity="low",
    )
    result = tested.to_dict()
    expected = {
        "model": "theModel",
        "reasoning": {
            "effort": "medium",
        },
        "text": {
            "verbosity": "low",
        },
    }
    assert result == expected
