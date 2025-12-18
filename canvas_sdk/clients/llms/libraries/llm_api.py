from __future__ import annotations

import base64
from abc import ABC, abstractmethod
from http import HTTPStatus

from requests import exceptions

from canvas_sdk.clients.llms.structures.base_model_llm_json import BaseModelLlmJson
from canvas_sdk.clients.llms.structures.file_content import FileContent
from canvas_sdk.clients.llms.structures.llm_file_url import LlmFileUrl
from canvas_sdk.clients.llms.structures.llm_response import LlmResponse
from canvas_sdk.clients.llms.structures.llm_tokens import LlmTokens
from canvas_sdk.clients.llms.structures.llm_turn import LlmTurn
from canvas_sdk.clients.llms.structures.settings.llm_settings import LlmSettings
from canvas_sdk.utils.http import Http


class LlmApi(ABC):
    """Base class for LLM (Large Language Model) API clients.

    Provides common functionality for managing conversation prompts and making requests
    to various LLM services. Subclasses should implement the request() method for
    specific LLM providers.

    Class Attributes:
        ROLE_SYSTEM: Constant for system role in conversations.
        ROLE_USER: Constant for user role in conversations.
        ROLE_MODEL: Constant for model/assistant role in conversations.
    """

    ROLE_SYSTEM = "system"
    ROLE_USER = "user"
    ROLE_MODEL = "model"

    def __init__(self, settings: LlmSettings):
        """Initialize the LLM client with settings.

        Args:
            settings: Configuration settings for the LLM API.
        """
        self.settings = settings
        self.prompts: list[LlmTurn] = []
        self.http = Http(self._api_base_url())
        self.file_urls: list[LlmFileUrl] = []
        self.schema: type[BaseModelLlmJson] | None = None

    def reset_prompts(self) -> None:
        """Clear all stored prompts."""
        self.prompts = []

    def add_url_file(self, url_file: LlmFileUrl) -> None:
        """Add a file to the conversation.

        The files should be added to the conversation on the next request if the last turn has the ROLE_USER role.

        Args:
            url_file: LlmFileUrl object to add to the conversation.
        """
        self.file_urls.append(url_file)

    def add_prompt(self, prompt: LlmTurn) -> None:
        """Add a conversation turn to the prompt history.

        Routes the prompt to the appropriate method based on its role.

        Args:
            prompt: The conversation turn to add.
        """
        if prompt.role == self.ROLE_SYSTEM:
            self.set_system_prompt(prompt.text)
        elif prompt.role == self.ROLE_USER:
            self.set_user_prompt(prompt.text)
        elif prompt.role == self.ROLE_MODEL:
            self.set_model_prompt(prompt.text)

    def set_system_prompt(self, text: list[str]) -> None:
        """Set or replace the system prompt.

        The system prompt is always placed at the beginning of the conversation.
        If a system prompt already exists, it is replaced.

        Args:
            text: List of text strings for the system prompt.
        """
        prompt = LlmTurn(role=self.ROLE_SYSTEM, text=text)
        if self.prompts and self.prompts[0].role == LlmApi.ROLE_SYSTEM:
            self.prompts[0] = prompt
        else:
            self.prompts.insert(0, prompt)

    def set_user_prompt(self, text: list[str]) -> None:
        """Add a user prompt to the conversation.

        Args:
            text: List of text strings for the user prompt.
        """
        self.prompts.append(LlmTurn(role=self.ROLE_USER, text=text))

    def set_model_prompt(self, text: list[str]) -> None:
        """Add a model/assistant response to the conversation.

        Args:
            text: List of text strings for the model prompt.
        """
        self.prompts.append(LlmTurn(role=self.ROLE_MODEL, text=text))

    def set_schema(self, schema: type[BaseModelLlmJson] | None) -> None:
        """Set the schema for the conversation.

        Set to None prevent a structured output.

        Using BaseModelLlmJson subclasses ensures the validity of the JSON Schema passed to the LLMs.

        """
        self.schema = None
        if schema and issubclass(schema, BaseModelLlmJson) and schema.validate_nested_models():
            self.schema = schema

    @abstractmethod
    def request(self) -> LlmResponse:
        """Make a request to the LLM API.

        Returns:
            Response from the LLM including status code, text, and token usage.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        ...

    @classmethod
    @abstractmethod
    def _api_base_url(cls) -> str:
        """Provide the API base url to the LlmApi subclass."""
        ...

    def attempt_requests(self, attempts: int) -> list[LlmResponse]:
        """Attempt multiple requests to the LLM API until success or max attempts.

        Args:
            attempts: Maximum number of request attempts to make.

        Returns:
            All responses from the LLM.
            If all attempts fail, returns an additional TOO_MANY_REQUESTS response.
        """
        result: list[LlmResponse] = []
        for _ in range(attempts):
            try:
                result.append(self.request())
                if result[-1].code == HTTPStatus.OK:
                    break
            except Exception as e:
                result.append(
                    LlmResponse(
                        code=HTTPStatus.INTERNAL_SERVER_ERROR,
                        response=f"Request attempt failed: {e}",
                        tokens=LlmTokens(prompt=0, generated=0),
                    )
                )
        else:
            result.append(
                LlmResponse(
                    code=HTTPStatus.TOO_MANY_REQUESTS,
                    response=f"Http error: max attempts ({attempts}) exceeded.",
                    tokens=LlmTokens(prompt=0, generated=0),
                )
            )
        return result

    @classmethod
    def base64_encoded_content_of(cls, file_url: LlmFileUrl) -> FileContent:
        """Download a file from a URL and return its base64-encoded content.

        Args:
            file_url: The URL and type of the file to download.

        Returns:
            FileContent with MIME type, base64-encoded content, and size, or None if the request fails.
        """
        try:
            response = Http(file_url.url).get("")

            mime_type: str = response.headers.get("Content-Type", "application/octet-stream")
            encoded_content: bytes = base64.b64encode(response.content)
            result = FileContent(
                mime_type=mime_type,
                content=encoded_content,
                size=len(response.content),
            )
        except exceptions.RequestException:
            result = FileContent(mime_type="", content=b"", size=0)

        return result


__exports__ = ("LlmApi",)
