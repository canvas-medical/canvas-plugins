import json
from http import HTTPStatus

from requests import exceptions

from canvas_sdk.clients.llms.libraries.llm_api import LlmApi
from canvas_sdk.clients.llms.structures.llm_response import LlmResponse
from canvas_sdk.clients.llms.structures.llm_tokens import LlmTokens


class LlmAnthropic(LlmApi):
    """Anthropic Claude LLM API client.

    Implements the LlmBase interface for Anthropic's Claude API.
    """

    def to_dict(self) -> dict:
        """Convert prompts and add the necessary information to Anthropic API request format.

        Returns:
            Dictionary formatted for Anthropic API with messages array.
        """
        messages: list[dict] = []

        roles = {
            self.ROLE_SYSTEM: "user",
            self.ROLE_USER: "user",
            self.ROLE_MODEL: "assistant",
        }
        for prompt in self.prompts:
            role = roles[prompt.role]
            part = {"type": "text", "text": "\n".join(prompt.text)}
            # contiguous parts for the same role are merged
            if messages and messages[-1]["role"] == role:
                messages[-1]["content"].append(part)
            else:
                messages.append({"role": role, "content": [part]})

        return self.settings.to_dict() | {
            "messages": messages,
        }

    @classmethod
    def _api_base_url(cls) -> str:
        return "https://api.anthropic.com"

    def request(self) -> LlmResponse:
        """Make a request to the Anthropic Claude API.

        Returns:
            Response containing status code, generated text, and token usage.
        """
        headers = {
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
            "x-api-key": self.settings.api_key,
        }
        data = json.dumps(self.to_dict())

        tokens = LlmTokens(prompt=0, generated=0)
        try:
            request = self.http.post("/v1/messages", headers=headers, data=data)
            code = request.status_code
            response = request.text
            if code == HTTPStatus.OK.value:
                content = json.loads(request.text)
                response = content.get("content", [{}])[0].get("text", "")
                usage = content.get("usage", {})
                tokens = LlmTokens(
                    prompt=usage.get("input_tokens") or 0,
                    generated=usage.get("output_tokens") or 0,
                )
        except exceptions.RequestException as e:
            code = HTTPStatus.BAD_REQUEST
            response = f"Request failed: {e}"
            if message := getattr(e, "response", None):
                code = message.status_code
                response = message.text

        return LlmResponse(
            code=HTTPStatus(code),
            response=response,
            tokens=tokens,
        )


__exports__ = ("LlmAnthropic",)
