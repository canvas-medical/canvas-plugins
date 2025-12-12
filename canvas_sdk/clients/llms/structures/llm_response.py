from http import HTTPStatus
from typing import NamedTuple

from canvas_sdk.clients.llms.structures.llm_tokens import LlmTokens


class LlmResponse(NamedTuple):
    """Response from an LLM API call.

    Attributes:
        code: HTTP status code of the response.
        response: Text content returned by the LLM.
        tokens: Token usage information for the request.
    """

    code: HTTPStatus
    response: str
    tokens: LlmTokens

    def to_dict(self) -> dict:
        """Convert the response to a dictionary representation.

        Returns:
            Dictionary containing the response data with serialized code, response text, and tokens.
        """
        return {
            "code": self.code.value,
            "response": self.response,
            "tokens": self.tokens.to_dict(),
        }


__exports__ = ("LlmResponse",)
