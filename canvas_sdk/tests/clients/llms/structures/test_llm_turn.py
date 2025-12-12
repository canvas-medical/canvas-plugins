import pytest

from canvas_sdk.clients.llms.structures.llm_turn import LlmTurn


def test_to_dict() -> None:
    """Test conversion of LlmTurn to dictionary format."""
    tested = LlmTurn(role="theRole", text=["text1", "text2"])
    expected = {"role": "theRole", "text": ["text1", "text2"]}
    assert tested.to_dict() == expected


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        pytest.param([], [], id="empty"),
        pytest.param(
            [
                {"role": "role1", "text": ["text1"]},
                {"role": "role2", "text": ["text2"]},
                {"role": "role3", "text": ["text3"]},
            ],
            [
                LlmTurn(role="role1", text=["text1"]),
                LlmTurn(role="role2", text=["text2"]),
                LlmTurn(role="role3", text=["text3"]),
            ],
            id="not-empty",
        ),
    ],
)
def test_load_from_json(data: list[dict], expected: list[LlmTurn]) -> None:
    """Test loading LlmTurn instances from a list of dictionaries."""
    tested = LlmTurn
    result = tested.load_from_dict(data)
    assert result == expected
