from http import HTTPStatus

from pydantic import Field

from canvas_sdk.clients.llms.constants import FileType
from canvas_sdk.clients.llms.libraries import LlmOpenai
from canvas_sdk.clients.llms.structures import BaseModelLlmJson, LlmFileUrl
from canvas_sdk.clients.llms.structures.settings import LlmSettingsGpt4
from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import JSONResponse, PlainTextResponse, Response
from canvas_sdk.handlers.simple_api import Credentials, SimpleAPI, api
from llm_manip.constants.secrets import Secrets


class Result(BaseModelLlmJson):
    """Structured response model for animal counting results."""

    count_dogs: int = Field(description="the number of dogs")
    count_cats: int = Field(description="the number of cats")
    count_total: int = Field(description="the number of animals")


class LlmResponse(BaseModelLlmJson):
    """Structured response model for LLM animal analysis with optional result."""

    comment: str = Field(description="the comment")
    result: Result | None


class LlmManip(SimpleAPI):
    """Simple API handler for LLM-based image analysis and chat operations."""

    PREFIX = None

    def authenticate(self, credentials: Credentials) -> bool:
        """Authenticate API requests.

        Args:
            credentials: The credentials provided with the request.

        Returns:
            True to allow all requests (authentication bypassed).
        """
        return True

    def _llm_client(self) -> LlmOpenai:
        """Create and configure an OpenAI LLM client with credentials from secrets.

        Returns:
            Configured LlmOpenai client instance using GPT-4o model.
        """
        return LlmOpenai(
            LlmSettingsGpt4(
                api_key=self.secrets[Secrets.llm_key],
                model="gpt-4o",
                temperature=2.0,
            )
        )

    @api.post("/animals_count")
    def animals_count(self) -> list[Response | Effect]:
        """Analyze an image URL to count animals using LLM vision capabilities.

        Accepts a JSON body with an optional 'url' field containing an image URL.
        Uses a default sample image if no URL is provided.

        Returns:
            JSON response containing the LLM's structured analysis of animals in the image.
        """
        client = self._llm_client()
        url = self.request.json().get("url")
        if not url:
            url = "https://images.unsplash.com/photo-1563460716037-460a3ad24ba9?w=125"

        client.set_schema(LlmResponse)
        client.set_system_prompt(
            ["Your task is to read the pictures provided by the user and count the animals in it."]
        )
        client.set_user_prompt(["Identify the content of the provided picture."])
        client.add_url_file(LlmFileUrl(url=url, type=FileType.IMAGE))
        responses = client.attempt_requests(attempts=2)
        content = [r.to_dict() for r in responses]
        return [JSONResponse(content, status_code=HTTPStatus(HTTPStatus.OK))]

    @api.post("/chat")
    def chat(self) -> list[Response | Effect]:
        """Process a multi-turn chat conversation with the LLM.

        Accepts a JSON array of conversation turns, each with 'role' (system/user/model)
        and 'prompt' fields.

        Returns:
            Plain text response containing the LLM's reply to the conversation.
        """
        client = self._llm_client()
        for turn in self.request.json():
            if not isinstance(turn, dict):
                continue
            if turn.get("role") == "system":
                client.set_system_prompt([turn.get("prompt", "")])
            elif turn.get("role") == "user":
                client.set_user_prompt([turn.get("prompt", "")])
            else:
                client.set_model_prompt([turn.get("prompt", "")])

        response = client.attempt_requests(attempts=1)[0]
        return [PlainTextResponse(response.response, status_code=response.code)]
