import pytest

from canvas_sdk.clients.llms.structures.llm_tokens import LlmTokens


def test_add() -> None:
    """Test that add method correctly sums token counts from another LlmTokens instance."""
    tested = LlmTokens(178, 37)
    tested.add(LlmTokens(100, 50))
    assert tested.prompt == 278
    assert tested.generated == 87


@pytest.mark.parametrize(
    ("other", "expected"),
    [
        pytest.param(LlmTokens(178, 37), True, id="identical"),
        pytest.param(LlmTokens(177, 37), False, id="prompt-different"),
        pytest.param(LlmTokens(178, 38), False, id="generated-different"),
    ],
)
def test___eq__(other: LlmTokens, expected: bool) -> None:
    """Test equality comparison between LlmTokens instances."""
    tested = LlmTokens(178, 37)
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
