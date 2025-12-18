from http import HTTPStatus

from canvas_sdk.clients.llms.structures.llm_response import LlmResponse
from canvas_sdk.clients.llms.structures.llm_tokens import LlmTokens


def test_named_tuple() -> None:
    """Test LlmResponse is a NamedTuple with exactly three fields."""
    tested = LlmResponse(
        code=HTTPStatus.OK,
        response="theResponse",
        tokens=LlmTokens(
            prompt=145,
            generated=475,
        ),
    )

    assert isinstance(tested, tuple)
    assert tested[0] == HTTPStatus.OK
    assert tested[1] == "theResponse"
    assert tested[2] == LlmTokens(
        prompt=145,
        generated=475,
    )
    assert len(tested) == 3


def test_to_dict() -> None:
    """Test conversion of LlmResponse to dictionary format."""
    tested = LlmResponse(
        code=HTTPStatus.OK,
        response="theResponse",
        tokens=LlmTokens(
            prompt=145,
            generated=475,
        ),
    )
    result = tested.to_dict()
    expected = {
        "code": 200,
        "response": "theResponse",
        "tokens": {
            "generated": 475,
            "prompt": 145,
        },
    }
    assert result == expected
