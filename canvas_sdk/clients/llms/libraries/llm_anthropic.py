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
from canvas_sdk.clients.llms.structures.settings.llm_settings_anthropic import LlmSettingsAnthropic

# JSON Schema keywords that structured outputs rejects with a 400.
_UNSUPPORTED_SCHEMA_KEYWORDS = (
    "minimum",
    "maximum",
    "exclusiveMinimum",
    "exclusiveMaximum",
    "multipleOf",
    "minLength",
    "maxLength",
    "maxItems",
    "uniqueItems",
    "minContains",
    "maxContains",
    "minProperties",
    "maxProperties",
)
_SUPPORTED_MIN_ITEMS = (0, 1)
_SUPPORTED_STRING_FORMATS = (
    "date-time",
    "time",
    "date",
    "duration",
    "email",
    "hostname",
    "uri",
    "ipv4",
    "ipv6",
    "uuid",
)
_THINKING_BLOCK_TYPES = ("thinking", "redacted_thinking")
# Keywords whose value is a map of subschemas, or a subschema or list of subschemas.
_SUBSCHEMA_MAP_KEYWORDS = ("properties", "$defs", "definitions")
_SUBSCHEMA_KEYWORDS = (
    "items",
    "prefixItems",
    "anyOf",
    "allOf",
    "oneOf",
    "not",
    "additionalProperties",
)


class LlmAnthropic(LlmApi):
    """Anthropic Claude LLM API client.

    Implements the LlmBase interface for Anthropic's Claude API.
    """

    @classmethod
    def _output_schema(cls, schema: dict) -> dict:
        """Return a copy of a JSON schema that structured outputs accepts.

        Unsupported constraints are removed and noted in the description instead,
        so the model still sees them.
        """
        result: dict = {}
        removed: dict = {}
        for key, value in schema.items():
            if (
                key in _UNSUPPORTED_SCHEMA_KEYWORDS
                or (key == "minItems" and value not in _SUPPORTED_MIN_ITEMS)
                or (key == "format" and value not in _SUPPORTED_STRING_FORMATS)
            ):
                removed[key] = value
            elif key in _SUBSCHEMA_MAP_KEYWORDS and isinstance(value, dict):
                result[key] = {name: cls._output_schema(sub) for name, sub in value.items()}
            elif key in _SUBSCHEMA_KEYWORDS and isinstance(value, dict):
                result[key] = cls._output_schema(value)
            elif key in _SUBSCHEMA_KEYWORDS and isinstance(value, list):
                result[key] = [cls._output_schema(sub) for sub in value]
            else:
                result[key] = value

        if removed:
            constraints = ", ".join(f"{key}: {removed[key]}" for key in sorted(removed))
            description = result.get("description")
            result["description"] = (
                f"{description} ({constraints})" if description else f"({constraints})"
            )
        return result

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
        settings = self.settings.to_dict()
        # structured output requested
        structured: dict = {}
        if self.schema and self._uses_structured_outputs():
            output_format = {
                "type": "json_schema",
                "schema": self._output_schema(self.schema.model_json_schema()),
            }
            # keep any output_config the settings set, such as effort
            structured = {
                "output_config": settings.get("output_config", {}) | {"format": output_format}
            }
        elif self.schema:
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

        return settings | structured | {"messages": messages}

    def _uses_structured_outputs(self) -> bool:
        """Whether schema requests use structured outputs rather than a forced tool call."""
        return isinstance(self.settings, LlmSettingsAnthropic) and self.settings.structured_outputs

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
                blocks = content.get("content", [{}])
                # thinking blocks can precede the answer, so skip them
                answer_blocks = [
                    block for block in blocks if block.get("type") not in _THINKING_BLOCK_TYPES
                ]
                if self.schema and self._uses_structured_outputs():
                    response = "".join(block.get("text", "") for block in answer_blocks)
                elif self.schema:
                    response = json.dumps(blocks[0].get("input", {}))
                else:
                    response = answer_blocks[0].get("text", "") if answer_blocks else ""

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
