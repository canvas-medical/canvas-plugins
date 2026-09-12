from typing import cast

from jsonschema import ValidationError

from canvas_sdk.effects import Effect
from canvas_sdk.effects.questionnaire import CreateQuestionnaire
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api import APIKeyCredentials, SimpleAPIRoute
from canvas_sdk.questionnaires.utils import QuestionnaireConfig

# POST /plugin-io/api/example_sdk_effect_create_questionnaire/create-questionnaire
# Headers: "Authorization <your value for 'api-key'>"


class CreateQuestionnaireAPI(SimpleAPIRoute):
    """API endpoint that creates a questionnaire from JSON input.

    This endpoint accepts JSON input describing a questionnaire
    and creates a questionnaire using the Effect.
    """

    PATH = "/create-questionnaire"

    def authenticate(self, credentials: APIKeyCredentials) -> bool:
        """Simple API key authentication."""
        return credentials.key == self.secrets["api-key"]

    def post(self) -> list[Response | Effect]:
        """Create a questionnaire from JSON input.

        Expected JSON body:
        {
            "name": "Test questionnaire",
            "form_type": "QUES",
            "code_system": "INTERNAL",
            "code": "123",
            "can_originate_in_charting": true,
            "prologue": "Prologue of the test questionnaire",
            "display_results_in_social_history_section": true,
            "questions": [
                {
                    "content": "This is a single select question",
                    "code_system": "INTERNAL",
                    "code": "QUESTIONNAIRE_Q1",
                    "responses_code_system": "INTERNAL",
                    "responses_type": "SING",
                    "display_result_in_social_history_section": true,
                    "responses": [
                        {
                            "name": "Single select Option 1",
                            "code": "QUESTIONNAIRE_Q1_A1"
                        }
                    ]
                }
            ]
        }
        """
        try:
            questionnaire_data = cast(QuestionnaireConfig, self.request.json())

            effect = CreateQuestionnaire(questionnaire_config=questionnaire_data)

            return [
                effect.apply(),
                JSONResponse(
                    {
                        "message": "Questionnaire created successfully",
                        "questionnaire_name": questionnaire_data.get("name"),
                    }
                ),
            ]

        except ValidationError as e:
            return [
                JSONResponse(
                    {"error": "Invalid questionnaire configuration", "details": str(e)},
                    status_code=400,
                )
            ]

        except Exception as e:
            return [
                JSONResponse(
                    {"error": f"Failed to create questionnaire: {str(e)}"}, status_code=500
                )
            ]
