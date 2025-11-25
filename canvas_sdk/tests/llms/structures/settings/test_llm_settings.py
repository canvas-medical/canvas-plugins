from canvas_sdk.llms.structures.settings.llm_settings import LlmSettings


def test_to_dict() -> None:
    """Test conversion of LlmSettings to dictionary format excludes API key."""
    tested = LlmSettings(
        api_key="theKey",
        model="theModel",
    )
    result = tested.to_dict()
    expected = {
        "model": "theModel",
    }
    assert result == expected
