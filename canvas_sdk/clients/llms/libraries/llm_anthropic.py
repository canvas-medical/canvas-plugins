import base64
import json
from http import HTTPStatus

from requests import exceptions

from canvas_sdk.clients.llms.constants.file_type import FileType
from canvas_sdk.clients.llms.libraries.llm_api import LlmApi
from canvas_sdk.clients.llms.structures.file_content import FileContent
from canvas_sdk.clients.llms.structures.llm_file_url import LlmFileUrl
from canvas_sdk.clients.llms.structures.llm_response import LlmResponse
from canvas_sdk.clients.llms.structures.llm_tokens import LlmTokens


class LlmAnthropic(LlmApi):
    """Anthropic Claude LLM API client.

    Implements the LlmBase interface for Anthropic's Claude API.
    """

    def _file_url_to_content_item(self, file_url: LlmFileUrl) -> dict | None:
        """Convert a file URL to an Anthropic content item."""
        if file_url.type == FileType.PDF:
            return {"type": "document", "source": {"type": "url", "url": file_url.url}}
        elif file_url.type == FileType.IMAGE:
            return {"type": "image", "source": {"type": "url", "url": file_url.url}}
        elif file_url.type == FileType.TEXT:
            content = self.str_content_of(file_url)
            return {
                "type": "document",
                "source": {
                    "type": "text",
                    "media_type": "text/plain",
                    "data": content,
                },
            }

    @classmethod
    def _file_content_to_content_item(cls, file_content: FileContent) -> dict | None:
        """Convert file content to an Anthropic content item."""
        if file_content.mime_type.startswith("image/"):
            item_type, source_type = "image", "base64"
        elif file_content.mime_type.endswith("/pdf"):
            item_type, source_type = "document", "base64"
        elif file_content.mime_type.startswith("text/"):
            return {
                "type": "document",
                "source": {
                    "type": "text",
                    "media_type": "text/plain",
                    "data": base64.standard_b64decode(file_content.content).decode("utf-8"),
                },
            }
        else:
            return None
        return {
            "type": item_type,
            "source": {
                "type": source_type,
                "media_type": file_content.mime_type,
                "data": file_content.content.decode("utf-8"),
            },
        }

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

        # if there are files and the last message has the user's role
        if messages and messages[-1]["role"] == roles[self.ROLE_USER]:
            for file_url in self.file_urls:
                if item := self._file_url_to_content_item(file_url):
                    messages[-1]["content"].append(item)

            for file_content in self.file_contents:
                if item := self._file_content_to_content_item(file_content):
                    messages[-1]["content"].append(item)

            self.file_urls = []
            self.file_contents = []
        # structured output requested
        structured = {}
        if self.schema:
            name = self.schema.__name__
            structured = {
                "tool_choice": {"type": "tool", "name": name},
                "tools": [
                    {
                        "name": name,
                        # "description": "Provide the response using well-structured JSON.",
                        "input_schema": self.schema.model_json_schema(),
                    }
                ],
            }

        return self.settings.to_dict() | structured | {"messages": messages}

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
                output = content.get("content", [{}])[0]
                if self.schema:
                    response = json.dumps(output.get("input", {}))
                else:
                    response = output.get("text", "")

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
