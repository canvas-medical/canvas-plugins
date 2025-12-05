from canvas_sdk.clients.llms.structures.llm_tokens import LlmTokens


def test_add() -> None:
    """Test that add method correctly sums token counts from another LlmTokens instance."""
    tested = LlmTokens(178, 37)
    tested.add(LlmTokens(100, 50))
    assert tested.prompt == 278
    assert tested.generated == 87


def test___eq__() -> None:
    """Test equality comparison between LlmTokens instances."""
    tested = LlmTokens(178, 37)
    tests = [
        (LlmTokens(178, 37), True),
        (LlmTokens(177, 37), False),
        (LlmTokens(178, 38), False),
    ]
    for other, expected in tests:
        if expected:
            assert tested == other
        else:
            assert tested != other
        assert tested is not other


def test_to_dict() -> None:
    """Test conversion of LlmTokens to dictionary format."""
    tested = LlmTokens(178, 37)
    result = tested.to_dict()
    expected = {
        "prompt": 178,
        "generated": 37,
    }
    assert result == expected
