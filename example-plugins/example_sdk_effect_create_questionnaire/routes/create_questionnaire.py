from typing import Any, cast

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

    def authenticate(self, credentials: APIKeyCredentials) -> bool:  # type: ignore[override]
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
            questionnaire_data: dict[str, Any] = cast(dict[str, Any], self.request.json())

            # Construct QuestionnaireConfig
            questionnaire_config: QuestionnaireConfig = {
                "name": questionnaire_data["name"],
                "form_type": questionnaire_data["form_type"],
                "code_system": questionnaire_data["code_system"],
                "code": str(questionnaire_data["code"]),  # Convert to string
                "can_originate_in_charting": questionnaire_data["can_originate_in_charting"],
                "questions": questionnaire_data["questions"],
            }

            # Add optional fields if present
            if "prologue" in questionnaire_data:
                questionnaire_config["prologue"] = questionnaire_data["prologue"]
            if "display_results_in_social_history_section" in questionnaire_data:
                questionnaire_config["display_results_in_social_history_section"] = questionnaire_data["display_results_in_social_history_section"]

            effect = CreateQuestionnaire(questionnaire_config=questionnaire_config)

            return [
                effect.apply(),
                JSONResponse({
                    "message": "Questionnaire created successfully",
                    "questionnaire_name": questionnaire_data.get("name")
                })
            ]

        except ValidationError as e:
            return [JSONResponse(
                {
                    "error": "Invalid questionnaire configuration",
                    "details": str(e)
                },
                status_code=400
            )]

        except Exception as e:
            return [JSONResponse(
                {"error": f"Failed to create questionnaire: {str(e)}"},
                status_code=500
            )]
