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


def test_to_dict__structured_outputs_not_sent() -> None:
    """Test that structured_outputs is client-side only and never part of the request body."""
    tested = LlmSettingsAnthropic(
        api_key="theKey",
        model="theModel",
        temperature=None,
        max_tokens=8192,
        structured_outputs=True,
    )
    assert tested.to_dict() == {"model": "theModel", "max_tokens": 8192}
    assert (
        LlmSettingsAnthropic(
            api_key="k", model="m", temperature=None, max_tokens=1
        ).structured_outputs
        is False
    )
