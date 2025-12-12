from canvas_sdk.clients.llms.structures.settings.llm_settings_gemini import LlmSettingsGemini


def test_to_dict() -> None:
    """Test conversion of LlmSettingsGemini to dictionary format."""
    tested = LlmSettingsGemini(
        api_key="theKey",
        model="theModel",
        temperature=2.0,
    )
    result = tested.to_dict()
    expected = {
        "model": "theModel",
        "generationConfig": {"temperature": 2.0},
    }
    assert result == expected
