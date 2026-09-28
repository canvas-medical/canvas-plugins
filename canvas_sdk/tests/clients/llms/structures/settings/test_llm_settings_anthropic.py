from canvas_sdk.clients.llms.structures.settings.llm_settings_anthropic import LlmSettingsAnthropic


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


def test_to_dict__without_temperature() -> None:
    """Test that temperature is omitted when unset, for models that reject sampling parameters."""
    tested = LlmSettingsAnthropic(
        api_key="theKey",
        model="theModel",
        temperature=None,
        max_tokens=8192,
    )
    result = tested.to_dict()
    expected = {
        "model": "theModel",
        "max_tokens": 8192,
    }
    assert result == expected
