ai_note_titles
==============

## Description

Plugin that renames Notes when locked using OpenAI and the contents of the Note.

## Configuration

This example plugin defines the following "secrets" in the manifest file:

```
    "secrets": [
        "OPENAI_API_KEY"
    ],
```
Once defined in the `MANIFEST.json`, set the secrets for your plugin in the Admin UI of your Canvas EMR. [Read more](https://docs.canvasmedical.com/sdk/secrets/)

### OPENAI_API_KEY
[OpenAI API Key](https://platform.openai.com/docs/api-reference/authentication)
