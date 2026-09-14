from typing import Any

from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api import APIKeyCredentials, SimpleAPIRoute
from canvas_sdk.v1.data import QuestionEnablementCondition, Questionnaire

# GET /plugin-io/api/example_sdk_effect_create_questionnaire/questionnaire?name=<name>
# Headers: "Authorization: <your value for 'api-key'>"
#
# Reads a questionnaire back through the data module: its questions in order, their responses, and
# the branching conditions that decide when each question is shown. Creating a questionnaire is
# fire and forget, so the effect cannot tell the plugin what it produced, and this is how a plugin
# confirms what was written.


class ReadQuestionnaireAPI(SimpleAPIRoute):
    """Return a questionnaire's questions, responses and branching logic."""

    PATH = "/questionnaire"

    def authenticate(self, credentials: APIKeyCredentials) -> bool:
        """Simple API key authentication."""
        return credentials.key == self.secrets["api-key"]

    def get(self) -> list[Response]:
        """Return the active questionnaire with the requested name."""
        name = self.request.query_params.get("name")

        if not name:
            return [JSONResponse({"error": "Pass ?name=<questionnaire name>"}, status_code=400)]

        questionnaire = Questionnaire.objects.filter(name=name, status="AC").first()

        if questionnaire is None:
            return [
                JSONResponse({"error": f"No active questionnaire named {name!r}"}, status_code=404)
            ]

        return [
            JSONResponse(
                {
                    "id": str(questionnaire.id),
                    "name": questionnaire.name,
                    "code_system": questionnaire.code_system,
                    "code": questionnaire.code,
                    "use_case_in_charting": questionnaire.use_case_in_charting,
                    "use_in_shx": questionnaire.use_in_shx,
                    "questions": [
                        self._question(question) for question in questionnaire.questions.all()
                    ],
                }
            )
        ]

    def _question(self, question: Any) -> dict[str, Any]:
        """Describe one question, including what has to be answered for it to appear."""
        return {
            "code": question.code,
            "code_system": question.code_system,
            "content": question.name,
            "responses_type": question.response_option_set.type,
            "use_in_shx": question.response_option_set.use_in_shx,
            "enabled_behavior": question.enable_behavior,
            "responses": [
                {"code": option.code, "name": option.name, "value": option.value}
                for option in question.response_option_set.options.order_by("ordering")
            ],
            "enabled_conditions": [
                self._condition(condition)
                for condition in QuestionEnablementCondition.objects.filter(question=question)
            ],
        }

    def _condition(self, condition: Any) -> dict[str, Any]:
        """Describe one branching condition in the caller's own terms, by code."""
        return {
            "depends_on": condition.dependent_on.code,
            "operator": condition.operator,
            "value_code": condition.answer_option.code if condition.answer_option else None,
            "value_string": condition.answer_value,
        }
