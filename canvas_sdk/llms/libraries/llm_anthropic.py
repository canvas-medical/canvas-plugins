import json
from http import HTTPStatus

from requests import post as requests_post

from canvas_sdk.llms.libraries.llm_base import LlmBase
from canvas_sdk.llms.structures.llm_response import LlmResponse
from canvas_sdk.llms.structures.llm_tokens import LlmTokens


class LlmAnthropic(LlmBase):
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

    def request(self) -> LlmResponse:
        """Make a request to the Anthropic Claude API.

        Returns:
            Response containing status code, generated text, and token usage.
        """
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
            "x-api-key": self.settings.api_key,
        }
        data = json.dumps(self.to_dict())
        request = requests_post(
            url, headers=headers, params={}, data=data, verify=True, timeout=None
        )
        result = LlmResponse(
            code=HTTPStatus(request.status_code),
            response=request.text,
            tokens=LlmTokens(prompt=0, generated=0),
        )
        if result.code == HTTPStatus.OK.value:
            content = json.loads(request.text)
            text = content.get("content", [{}])[0].get("text", "")
            usage = content.get("usage", {})
            result = LlmResponse(
                code=result.code,
                response=text,
                tokens=LlmTokens(
                    prompt=usage.get("input_tokens") or 0,
                    generated=usage.get("output_tokens") or 0,
                ),
            )

        return result


__exports__ = ("LlmAnthropic",)
