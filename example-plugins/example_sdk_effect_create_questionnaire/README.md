# Example SDK Effect: Create Questionnaire

This example plugin demonstrates how to use the `CREATE_QUESTIONNAIRE` effect via a SimpleAPI endpoint.

## Overview

This plugin provides a REST API endpoint that accepts JSON input describing a questionnaire, converts it to YAML format, and uses the `CreateQuestionnaire` effect to persist it in Canvas.

## Use Case

Customers need flexibility for creating questionnaires because they are constantly updating and changing questions. Rather than creating a new plugin for each questionnaire, they can use this API to dynamically create questionnaires from JSON.

## Quick Start

```bash
# 1. Install the plugin
canvas install example-plugins/example_sdk_effect_create_questionnaire

# 2. Configure the API key secret (choose any value you want)
canvas config set example_sdk_effect_create_questionnaire api-key="test123"

# 3. Test the endpoint
curl -X POST \
  https://your-canvas-instance.com/plugin-io/api/example_sdk_effect_create_questionnaire/create-questionnaire \
  -H "Authorization: test123" \
  -H "Content-Type: application/json" \
  -d @test_questionnaire.json

# 4. Verify in Canvas UI: Settings → Questionnaires → "Test questionnaire"
```

## Installation

1. Install the plugin into your Canvas instance:
   ```bash
   canvas install example-plugins/example_sdk_effect_create_questionnaire
   ```

2. Configure the `api-key` secret:

   **Option A - Via Canvas CLI:**
   ```bash
   canvas config set example_sdk_effect_create_questionnaire api-key="your-secret-value"
   ```

   **Option B - Via Canvas UI:**
   - Navigate to Settings → Plugins → example_sdk_effect_create_questionnaire
   - Click "Configure" or "Secrets"
   - Set `api-key` to your desired value
   - Click Save

   **Note:** You choose the API key value. Use something simple like `"test123"` for testing, or generate a secure key for production:
   ```bash
   canvas config set example_sdk_effect_create_questionnaire api-key="$(openssl rand -hex 32)"
   ```

## API Endpoint

**POST** `/plugin-io/api/example_sdk_effect_create_questionnaire/create-questionnaire`

### Headers
```
Authorization: <your-api-key>
```

### Request Body

```json
{
  "name": "Test questionnaire",
  "form_type": "QUES",
  "code_system": "INTERNAL",
  "code": 123,
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
        },
        {
          "name": "Single select Option 2",
          "code": "QUESTIONNAIRE_Q1_A2"
        }
      ]
    },
    {
      "content": "This is a text question",
      "code_system": "INTERNAL",
      "code": "QUESTIONNAIRE_Q2",
      "responses_code_system": "INTERNAL",
      "responses_type": "TXT",
      "responses": [
        {
          "name": "Option 1",
          "code": "QUESTIONNAIRE_Q2_A1"
        }
      ]
    },
    {
      "content": "This is a multiselect question",
      "code_system": "INTERNAL",
      "code": "QUESTIONNAIRE_Q3",
      "responses_code_system": "INTERNAL",
      "responses_type": "MULT",
      "responses": [
        {
          "name": "Multiselect Option 1",
          "code": "QUESTIONNAIRE_Q3_A1"
        },
        {
          "name": "Multiselect Option 2",
          "code": "QUESTIONNAIRE_Q3_A2"
        },
        {
          "name": "Multiselect Option 3",
          "code": "QUESTIONNAIRE_Q3_A3"
        }
      ]
    }
  ]
}
```

### Response

**Success (200):**
```json
{
  "message": "Questionnaire created successfully",
  "questionnaire_name": "Test questionnaire"
}
```

**Error (400):**
```json
{
  "error": "Missing required fields: name, code"
}
```

**Error (500):**
```json
{
  "error": "Failed to create questionnaire: <error message>"
}
```

## Field Reference

### Top-Level Fields

- `name` (string, required): Name of the questionnaire
- `form_type` (string, required): One of "QUES", "SA", "EXAM", "ROS"
- `code_system` (string, required): One of "SNOMED", "LOINC", "ICD-10", "INTERNAL", "CPT"
- `code` (string/number, required): Unique code for the questionnaire
- `can_originate_in_charting` (boolean, required): Whether the questionnaire can be initiated from charting
- `prologue` (string, optional): Text displayed at the beginning of the questionnaire
- `display_results_in_social_history_section` (boolean, optional): Whether to display completion info in Social History section

### Question Fields

- `content` (string, required): The question text
- `code_system` (string, required): Coding system for the question
- `code` (string, required): Unique code for the question
- `code_description` (string, optional): Description of the code
- `responses_code_system` (string, required): Coding system for responses
- `responses_type` (string, required): One of "SING" (single select), "MULT" (multi select), "TXT" (free text)
- `display_result_in_social_history_section` (boolean, optional): Whether to show response in Social History section

### Response Fields

- `name` (string, required): Display text for the response option (use "TXT" for free text questions)
- `code` (string, required): Unique code for the response
- `code_description` (string, optional): Description of the code
- `value` (string, optional): Numerical value for scoring

## Example cURL Request

```bash
curl -X POST https://your-canvas-instance.com/plugin-io/api/example_sdk_effect_create_questionnaire/create-questionnaire \
  -H "Authorization: your-api-key" \
  -H "Content-Type: application/json" \
  -d @questionnaire.json
```

## How It Works

1. The endpoint receives JSON input via POST request
2. Validates required fields
3. Normalizes the data structure (e.g., converts numeric codes to strings, adds default values)
4. Converts the normalized data to YAML format
5. Passes the YAML to the `CreateQuestionnaire` effect
6. The effect interpreter in Canvas yields to `YamlQuestionnaireComposer` to persist the questionnaire

## Troubleshooting

### Issue: "Unauthorized" (401 error)
**Solution:** Make sure your Authorization header matches the configured API key:
```bash
# Check configured value
canvas config get example_sdk_effect_create_questionnaire api-key

# Use the same value in your curl command
curl -H "Authorization: <value-from-above>" ...
```

### Issue: "Missing required fields" (400 error)
**Solution:** Verify your JSON includes all required fields: `name`, `form_type`, `code_system`, `code`, `can_originate_in_charting`, and `questions`.

### Issue: Questionnaire not appearing in Canvas
**Solution:**
- Check plugin logs: `canvas logs`
- Verify the CREATE_QUESTIONNAIRE effect interpreter is registered in home-app
- Check Canvas UI: Settings → Questionnaires

### Issue: JSON parsing error
**Solution:** Validate your JSON syntax:
```bash
python -m json.tool test_questionnaire.json
```

## Notes

- The `active` field from JSON input is not included in the YAML as it's not part of the questionnaire schema
- Codes are automatically converted to strings if provided as numbers
- Default empty strings are added for `code_description` and `value` fields when not provided
- This plugin leverages the questionnaire builder infrastructure by using the same YAML composer
