import json
from http import HTTPStatus

from requests import post as requests_post

from canvas_sdk.llms.libraries.llm_base import LlmBase
from canvas_sdk.llms.structures.llm_response import LlmResponse
from canvas_sdk.llms.structures.llm_tokens import LlmTokens


class LlmGoogle(LlmBase):
    """Google Gemini LLM API client.

    Implements the LlmBase interface for Google's Generative Language API.
    """

    def to_dict(self) -> dict:
        """Convert prompts and add the necessary information to Google API request format.

        Returns:
            Dictionary formatted for Google API with contents array.
        """
        contents: list[dict] = []
        roles = {
            self.ROLE_SYSTEM: "user",
            self.ROLE_USER: "user",
            self.ROLE_MODEL: "model",
        }
        for prompt in self.prompts:
            role = roles[prompt.role]
            part = {"text": "\n".join(prompt.text)}
            # contiguous parts for the same role are merged
            if contents and contents[-1]["role"] == role:
                contents[-1]["parts"].append(part)
            else:
                contents.append({"role": role, "parts": [part]})

        return self.settings.to_dict() | {
            "contents": contents,
        }

    def request(self) -> LlmResponse:
        """Make a request to the Google Gemini API.

        Returns:
            Response containing status code, generated text, and token usage.
        """
        url = (
            "https://generativelanguage.googleapis.com/"
            "v1beta/"
            f"{self.settings.model}:generateContent?key={self.settings.api_key}"
        )
        headers = {"Content-Type": "application/json"}
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
            text = (
                content.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
            )
            usage = content.get("usageMetadata", {})
            result = LlmResponse(
                code=result.code,
                response=text,
                tokens=LlmTokens(
                    prompt=usage.get("promptTokenCount") or 0,
                    generated=(usage.get("candidatesTokenCount") or 0)
                    + (usage.get("thoughtsTokenCount") or 0),
                ),
            )

        return result


__exports__ = ("LlmGoogle",)
