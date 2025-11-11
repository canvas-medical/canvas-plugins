import yaml

from canvas_sdk.effects.questionnaire import CreateQuestionnaire
from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api import APIKeyCredentials, SimpleAPIRoute

# POST /plugin-io/api/example_sdk_effect_create_questionnaire/create-questionnaire
# Headers: "Authorization <your value for 'api-key'>"


class CreateQuestionnaireAPI(SimpleAPIRoute):
    """API endpoint that creates a questionnaire from JSON input.

    This endpoint accepts JSON input describing a questionnaire and converts it
    to YAML format before passing it to the CREATE_QUESTIONNAIRE effect.
    """

    PATH = "/create-questionnaire"

    def authenticate(self, credentials: APIKeyCredentials) -> bool:
        """Simple API key authentication."""
        return credentials.key == self.secrets["api-key"]

    def post(self) -> list[Response]:
        """Create a questionnaire from JSON input.

        Expected JSON body:
        {
            "name": "Test questionnaire",
            "form_type": "QUES",
            "code_system": "INTERNAL",
            "code": 123,
            "active": true,
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
            # Get JSON body from request
            questionnaire_data = self.request.json()

            # Validate required fields
            required_fields = ["name", "form_type", "code_system", "code", "can_originate_in_charting", "questions"]
            missing_fields = [field for field in required_fields if field not in questionnaire_data]

            if missing_fields:
                return [JSONResponse(
                    {"error": f"Missing required fields: {', '.join(missing_fields)}"},
                    status_code=400
                )]

            # Normalize the data structure for YAML conversion
            normalized_data = self._normalize_questionnaire_data(questionnaire_data)

            # Convert to YAML
            questionnaire_yaml = yaml.dump(normalized_data, default_flow_style=False, sort_keys=False)

            # Create the questionnaire using the effect
            effect = CreateQuestionnaire(questionnaire_yaml=questionnaire_yaml)

            return [
                effect.apply(),
                JSONResponse({
                    "message": "Questionnaire created successfully",
                    "questionnaire_name": questionnaire_data.get("name")
                })
            ]

        except Exception as e:
            return [JSONResponse(
                {"error": f"Failed to create questionnaire: {str(e)}"},
                status_code=500
            )]

    def _normalize_questionnaire_data(self, data: dict) -> dict:
        """Normalize questionnaire data to match the expected YAML schema.

        This handles:
        - Converting code to string if it's an integer
        - Adding default values for optional fields
        - Filtering out fields not in the YAML schema (like 'active')
        """
        normalized = {
            "name": data["name"],
            "form_type": data["form_type"],
            "code_system": data["code_system"],
            "code": str(data["code"]),  # Ensure code is a string
            "can_originate_in_charting": data["can_originate_in_charting"],
            "questions": []
        }

        # Add optional top-level fields if present
        if "prologue" in data:
            normalized["prologue"] = data["prologue"]

        if "display_results_in_social_history_section" in data:
            normalized["display_results_in_social_history_section"] = data["display_results_in_social_history_section"]

        # Normalize questions
        for question in data["questions"]:
            normalized_question = {
                "content": question["content"],
                "code_system": question["code_system"],
                "code": question["code"],
                "code_description": question.get("code_description", ""),
                "responses_code_system": question["responses_code_system"],
                "responses_type": question["responses_type"]
            }

            # Add optional question-level fields
            if "display_result_in_social_history_section" in question:
                normalized_question["display_result_in_social_history_section"] = question["display_result_in_social_history_section"]

            # Add branching logic fields if present (must come before responses)
            if "enabled_behavior" in question:
                normalized_question["enabled_behavior"] = question["enabled_behavior"]

            if "enabled_conditions" in question and question["enabled_conditions"]:
                normalized_question["enabled_conditions"] = question["enabled_conditions"]

            # Normalize responses (add responses array last)
            normalized_responses = []
            for response in question["responses"]:
                normalized_response = {
                    "name": response["name"],
                    "code": response["code"],
                    "code_description": response.get("code_description", ""),
                    "value": response.get("value", "")
                }
                normalized_responses.append(normalized_response)

            normalized_question["responses"] = normalized_responses
            normalized["questions"].append(normalized_question)

        return normalized
