from canvas_sdk.llms.structures.settings.llm_settings_anthropic import LlmSettingsAnthropic


def test_to_dict() -> None:
    """Test conversion of LlmSettingsAnthropic to dictionary format."""
    tested = LlmSettingsAnthropic(
        api_key="theKey",
        model="theModel",
        temperature=0.78,
        max_tokens=8192,
    )
    result = tested.to_dict()
    expected = {
        "model": "theModel",
        "temperature": 0.78,
        "max_tokens": 8192,
    }
    assert result == expected
