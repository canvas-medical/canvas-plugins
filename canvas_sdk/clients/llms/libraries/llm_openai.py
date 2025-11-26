from __future__ import annotations

import json
from http import HTTPStatus

from requests import exceptions

from canvas_sdk.clients.llms.libraries.llm_base import LlmBase
from canvas_sdk.clients.llms.structures.llm_response import LlmResponse
from canvas_sdk.clients.llms.structures.llm_tokens import LlmTokens
from canvas_sdk.utils.http import Http


class LlmOpenai(LlmBase):
    """OpenAI LLM API client.

    Implements the LlmBase interface for OpenAI's API.
    """

    def to_dict(self) -> dict:
        """Convert prompts and add the necessary information to OpenAI API request format.

        Returns:
            Dictionary formatted for OpenAI API with instructions and input messages.
        """
        roles = {
            self.ROLE_SYSTEM: "developer",
            self.ROLE_USER: "user",
            self.ROLE_MODEL: "assistant",
        }
        messages: list[dict] = [
            {
                "role": roles[prompt.role],
                "content": [
                    {
                        "type": "input_text" if prompt.role == self.ROLE_USER else "output_text",
                        "text": "\n".join(prompt.text),
                    }
                ],
            }
            for prompt in self.prompts
            if prompt.role != self.ROLE_SYSTEM
        ]

        system_prompt = "\n".join(
            ["\n".join(prompt.text) for prompt in self.prompts if prompt.role == self.ROLE_SYSTEM]
        )
        return self.settings.to_dict() | {
            "instructions": system_prompt,
            "input": messages,
        }

    def request(self) -> LlmResponse:
        """Make a request to the OpenAI API.

        Returns:
            Response containing status code, generated text, and token usage.
        """
        url = "https://us.api.openai.com/v1/responses"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.settings.api_key}",
        }
        data = json.dumps(self.to_dict())

        tokens = LlmTokens(prompt=0, generated=0)
        try:
            request = Http(url).post("", headers=headers, data=data)
            code = request.status_code
            response = request.text
            if code == HTTPStatus.OK.value:
                content = json.loads(request.text)
                response = ""
                for output in content.get("output", [{}]):
                    if output.get("type", "") == "message":
                        response += output.get("content", [{}])[0].get("text", "")
                usage = content.get("usage", {})
                tokens = LlmTokens(
                    prompt=usage.get("input_tokens") or 0,
                    generated=usage.get("output_tokens") or 0,
                )
        except exceptions.RequestException as e:
            code = HTTPStatus.BAD_REQUEST
            response = f"Request failed: {e}"
            if hasattr(e, "response") and e.response is not None:
                code = e.response.status_code
                response = e.response.text

        return LlmResponse(
            code=HTTPStatus(code),
            response=response,
            tokens=tokens,
        )


__exports__ = ("LlmOpenai",)
