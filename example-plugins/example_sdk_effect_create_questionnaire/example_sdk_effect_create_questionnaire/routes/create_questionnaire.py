from typing import Any

from canvas_sdk.effects import Effect
from canvas_sdk.effects.questionnaire import CreateQuestionnaire
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api import APIKeyCredentials, SimpleAPIRoute
from canvas_sdk.questionnaires.utils import (
    EnabledCondition,
    Question,
    QuestionnaireConfig,
)
from canvas_sdk.questionnaires.utils import (
    Response as QuestionnaireResponse,
)

# POST /plugin-io/api/example_sdk_effect_create_questionnaire/create-questionnaire
# Headers: "Authorization: <your value for 'api-key'>"
#
# Body: a screening definition in the caller's own shape, which this plugin translates into a
# QuestionnaireConfig. That translation is the point of the example: the questionnaire is built in
# Python, so the caller never has to know Canvas's schema, and the questions can be assembled from
# whatever the caller already has.
#
#   {
#     "title": "Depression screening",
#     "code": "44249-1",
#     "items": [
#       {"prompt": "Little interest or pleasure in doing things?",
#        "choices": ["Not at all", "Several days", "More than half the days"]},
#       {"prompt": "Describe anything else you would like us to know", "type": "text"}
#     ],
#     "follow_up": {"prompt": "How long has this been going on?", "when_answer": "Several days"}
#   }

# The response type each caller "type" maps to. Omitting it means a single select, which is the
# common case. SING and MULT carry the caller's choices; TXT and DATE take a single placeholder
# option, because the answer is typed or picked rather than chosen from a list.
RESPONSE_TYPES = {None: "SING", "single": "SING", "multi": "MULT", "text": "TXT", "date": "DATE"}
PLACEHOLDER_TYPES = {"TXT", "DATE"}


class CreateQuestionnaireAPI(SimpleAPIRoute):
    """Build a questionnaire from a caller's screening definition and create it in Canvas."""

    PATH = "/create-questionnaire"

    def authenticate(self, credentials: APIKeyCredentials) -> bool:
        """Simple API key authentication."""
        return credentials.key == self.secrets["api-key"]

    def post(self) -> list[Response | Effect]:
        """Translate the request body into a questionnaire and emit the effect."""
        try:
            config = self._build_config(self.request.json())
        except KeyError as error:
            return [JSONResponse({"error": f"Missing field {error}"}, status_code=400)]
        except ValueError as error:
            return [JSONResponse({"error": str(error)}, status_code=400)]

        return [
            JSONResponse({"created": config["name"], "questions": len(config["questions"])}),
            CreateQuestionnaire(questionnaire=config).apply(),
        ]

    def _build_config(self, body: dict[str, Any]) -> QuestionnaireConfig:
        """Assemble the questionnaire from the caller's definition."""
        questions = [
            self._build_question(index, item) for index, item in enumerate(body["items"], start=1)
        ]

        # A follow-up is only shown when an earlier question was answered a particular way, which is
        # what enabled_conditions expresses. Referencing a question or response code that is not in
        # this questionnaire is rejected when the effect is applied, rather than silently dropped.
        if follow_up := body.get("follow_up"):
            questions.append(self._build_follow_up(len(questions) + 1, follow_up, questions))

        return {
            "name": body["title"],
            "form_type": "QUES",
            "code_system": "LOINC",
            "code": body["code"],
            "can_originate_in_charting": True,
            "questions": questions,
        }

    def _build_question(self, index: int, item: dict[str, Any]) -> Question:
        """Turn one caller item into a question, choosing the response type from its shape."""
        code = f"Q{index}"
        requested = item.get("type")

        if requested not in RESPONSE_TYPES:
            raise ValueError(
                f"Unknown question type {requested!r}. Use one of: "
                f"{', '.join(sorted(t for t in RESPONSE_TYPES if t))}."
            )

        responses_type = RESPONSE_TYPES[requested]

        if responses_type in PLACEHOLDER_TYPES:
            return {
                "content": item["prompt"],
                "code_system": "INTERNAL",
                "code": code,
                "responses_code_system": "INTERNAL",
                "responses_type": responses_type,
                # Typed and picked answers still need one option to hang the response on.
                "responses": [{"name": responses_type, "code": f"{code}A1"}],
            }

        return {
            "content": item["prompt"],
            "code_system": "INTERNAL",
            "code": code,
            "responses_code_system": "INTERNAL",
            "responses_type": responses_type,
            # Scoring each choice by its position is the sort of thing that is tedious to maintain
            # in a static file and trivial to compute here.
            "responses": [
                self._build_response(code, position, choice)
                for position, choice in enumerate(item["choices"])
            ],
        }

    def _build_response(
        self, question_code: str, position: int, choice: str
    ) -> QuestionnaireResponse:
        """Build one selectable response, scored by its position."""
        return {
            "name": choice,
            "code": f"{question_code}A{position + 1}",
            "value": str(position),
        }

    def _build_follow_up(
        self, index: int, follow_up: dict[str, Any], questions: list[Question]
    ) -> Question:
        """Build a free-text question shown only when an earlier answer matches."""
        trigger = self._find_response(questions, follow_up["when_answer"])
        code = f"Q{index}"

        condition: EnabledCondition = {
            "question_code": trigger[0],
            "operator": "=",
            "value_code": trigger[1],
        }

        return {
            "content": follow_up["prompt"],
            "code_system": "INTERNAL",
            "code": code,
            "responses_code_system": "INTERNAL",
            "responses_type": RESPONSE_TYPES["text"],
            "responses": [{"name": "TXT", "code": f"{code}A1"}],
            "enabled_behavior": "all",
            "enabled_conditions": [condition],
        }

    def _find_response(self, questions: list[Question], answer: str) -> tuple[str, str]:
        """Return the (question code, response code) pair whose response text matches."""
        for question in questions:
            for response in question["responses"]:
                if response["name"] == answer:
                    return question["code"], response["code"]

        raise ValueError(f"No response named {answer!r} to trigger the follow-up question.")
