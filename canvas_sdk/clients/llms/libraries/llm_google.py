import json
from http import HTTPStatus

from requests import exceptions

from canvas_sdk.clients.llms.libraries.llm_api import LlmApi
from canvas_sdk.clients.llms.structures.llm_response import LlmResponse
from canvas_sdk.clients.llms.structures.llm_tokens import LlmTokens


class LlmGoogle(LlmApi):
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

    @classmethod
    def _api_base_url(cls) -> str:
        return "https://generativelanguage.googleapis.com"

    def request(self) -> LlmResponse:
        """Make a request to the Google Gemini API.

        Returns:
            Response containing status code, generated text, and token usage.
        """
        headers = {"Content-Type": "application/json"}
        data = json.dumps(self.to_dict())

        tokens = LlmTokens(prompt=0, generated=0)
        try:
            request = self.http.post(
                f"/v1beta/{self.settings.model}:generateContent?key={self.settings.api_key}",
                headers=headers,
                data=data,
            )
            code = request.status_code
            response = request.text
            if code == HTTPStatus.OK.value:
                content = json.loads(request.text)
                response = (
                    content.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "")
                )
                usage = content.get("usageMetadata", {})
                tokens = LlmTokens(
                    prompt=usage.get("promptTokenCount") or 0,
                    generated=(usage.get("candidatesTokenCount") or 0)
                    + (usage.get("thoughtsTokenCount") or 0),
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


__exports__ = ("LlmGoogle",)
