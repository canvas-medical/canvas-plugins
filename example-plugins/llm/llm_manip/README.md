# LLM Interactions Plugin

A Canvas plugin that demonstrates how to use LLMs through the Canvas SDK for image analysis, chat conversations, and file processing using OpenAI's GPT-4o model.

## Features

- **Image Analysis**: Analyze images from URLs with structured output (animal counting example)
- **Multi-turn Chat**: Conduct conversations with the LLM using system, user, and model prompts
- **File Analysis**: Upload and analyze files (images, PDFs) with custom questions
- **Structured Output**: Define Pydantic schemas for typed LLM responses

## Components

### Protocol: `LlmManip`

A SimpleAPI handler that exposes REST endpoints for LLM operations.

**API Endpoints:**

| Method | Endpoint | Description | SDK Methods |
|--------|----------|-------------|-------------|
| POST | `/animals_count` | Analyze image URL to count animals | `set_schema`, `set_system_prompt`, `set_user_prompt`, `add_url_file`, `attempt_requests` |
| POST | `/chat` | Multi-turn chat conversation | `set_system_prompt`, `set_user_prompt`, `set_model_prompt`, `attempt_requests` |
| POST | `/file` | Analyze uploaded file content | `file_content.append`, `set_system_prompt`, `set_user_prompt`, `attempt_requests` |

### Application: `LlmFormApp`

A patient-specific application that launches a right side panel interface for:

- Submitting image URLs for analysis
- Conducting chat conversations
- Uploading files for analysis

## Configuration

### Required Secrets

Configure this secret in your Canvas plugin settings:

| Secret Name | Description |
|-------------|-------------|
| `LlmKey` | OpenAI API Key |

## Installation

1. Install the plugin via the command line: `canvas install llm_manip`
2. Configure the required secret with your OpenAI API key (`https://xxxx.canvasmedical.com/admin/plugin_io/plugin/`)
3. Access the application from a patient's chart in the drawer menu

## Usage

1. Open a patient chart
2. Launch the "LLM Interactions" application
3. Choose an interaction mode (image analysis, chat, or file upload)

### Image Analysis Example

Send a POST request to `/animals_count` with an optional image URL:

```json
{
  "url": "https://example.com/image.jpg"
}
```

Returns structured JSON with animal counts (dogs, cats, total).

### Chat Example

Send a POST request to `/chat` with conversation turns:

```json
[
  {"role": "system", "prompt": "You are a helpful medical assistant."},
  {"role": "user", "prompt": "What are common symptoms of the flu?"}
]
```

### File Analysis Example

Send a multipart form POST to `/file` with:
- `file`: The file to analyze (image or PDF)
- `input`: The question about the file

## SDK Classes Used

This plugin demonstrates the `canvas_sdk.clients.llms` module:

- **`LlmOpenai`**: OpenAI client implementation
- **`LlmSettingsGpt4`**: Configuration for GPT-4 models
- **`BaseModelLlmJson`**: Base class for structured output schemas
- **`LlmFileUrl`**: File reference by URL
- **`FileContent`**: Binary file content for upload
- **`FileType`**: Enum for file types (IMAGE, PDF)

## Structured Output

The plugin demonstrates structured output using Pydantic models:

```python
class Result(BaseModelLlmJson):
    count_dogs: int = Field(description="the number of dogs")
    count_cats: int = Field(description="the number of cats")
    count_total: int = Field(description="the number of animals")
```

## Supported LLM Providers

The SDK supports multiple LLM providers:

- **OpenAI** (`LlmOpenai`): GPT-4o and other OpenAI models
- **Anthropic** (`LlmAnthropic`): Claude models
- **Google** (`LlmGoogle`): Gemini models

## Important Note

The `CANVAS_MANIFEST.json` is used when installing your plugin. Please ensure it gets updated if you add, remove, or rename protocols.
