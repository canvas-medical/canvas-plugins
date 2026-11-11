# Link Document to Patient Example Plugin

This example plugin demonstrates how to use the `LinkDocumentToPatient` effect to link documents in the Data Integration queue to patients using the patient's key.

## Overview

When a document enters the Data Integration queue, this plugin:

1. Responds to the `DOCUMENT_RECEIVED` event
2. Finds the matching patient (the plugin is responsible for patient matching)
3. Emits a `LinkDocumentToPatient` effect with the patient's key

## The LinkDocumentToPatient Effect

The `LinkDocumentToPatient` effect links a document to a patient using the patient's key:

```python
from canvas_sdk.effects.data_integration import LinkDocumentToPatient

effect = LinkDocumentToPatient(
    document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",  # Required: IntegrationTask UUID
    patient_key="8d84776879de49518a4bc3bb81d96dd4",      # Required: patient's key (32-char hex)
    annotations=[                                        # Optional: display annotations
        {"text": "AI 95%", "color": "#00AA00"},
        {"text": "Auto-linked", "color": "#2196F3"},
    ],
    source_protocol="llm_v1",                            # Optional: protocol/plugin identifier
)

# Apply the effect
effects = [effect.apply()]
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `document_id` | str/int | Yes | The IntegrationTask ID to link |
| `patient_key` | str | Yes | The patient's key (32-character hex string) |
| `annotations` | list[dict] | No | Display annotations with `text` and `color` fields |
| `source_protocol` | str | No | Protocol/plugin identifier for tracking |

### Annotations

Annotations are displayed in the Data Integration UI to help reviewers understand how the document was linked:

```python
annotations = [
    {"text": "AI 95%", "color": "#00AA00"},      # Green - confidence level
    {"text": "Auto-linked", "color": "#2196F3"}, # Blue - informational
]
```

Each annotation must have:
- `text` (str, required): The annotation text to display
- `color` (str, required): Hex color code for display

## How It Works

The plugin is responsible for finding/matching the patient and providing their key:

1. **Plugin Extracts Demographics**: Use an LLM or OCR system to extract patient information from the document
2. **Plugin Finds Patient**: Search for the patient in Canvas using the extracted demographics
3. **Plugin Provides Key**: Pass the patient's `patient_key` to the effect
4. **Interpreter Links Document**: The home-app interpreter looks up the patient by key and links the document

This approach simplifies the interpreter and eliminates edge cases with 0 or multiple patient matches - the plugin handles all matching logic.

## Usage Patterns

### Basic Auto-Linking

```python
class LinkDocumentHandler(BaseHandler):
    RESPONDS_TO = [EventType.Name(EventType.DOCUMENT_RECEIVED)]

    def compute(self) -> list[Effect]:
        document_id = self.event.target.id

        # Find patient (implement your matching logic)
        patient = self.find_patient_from_document(document_id)

        if not patient:
            return []

        return [
            LinkDocumentToPatient(
                document_id=document_id,
                patient_key=str(patient.id),
                annotations=[
                    {"text": "AI 95%", "color": "#00AA00"},
                    {"text": "Auto-linked", "color": "#2196F3"},
                ],
                source_protocol="my_plugin_v1",
            ).apply()
        ]
```

### Conditional Linking with Confidence Threshold

```python
MIN_CONFIDENCE = 0.85

def compute(self) -> list[Effect]:
    document_id = self.event.target.id
    result = self.extract_and_match_patient(document_id)

    if not result:
        return []

    # Only auto-link if confidence is high enough
    if result["confidence"] < MIN_CONFIDENCE:
        log.info("Confidence too low, routing to manual review")
        return []

    return [
        LinkDocumentToPatient(
            document_id=document_id,
            patient_key=result["patient_key"],
            annotations=[
                {"text": f"AI {int(result['confidence'] * 100)}%", "color": "#00AA00"},
                {"text": "Auto-linked", "color": "#2196F3"},
            ],
            source_protocol="llm_v1",
        ).apply()
    ]
```

## Error Handling

The effect validates inputs and raises `ValidationError` for:

- Missing required fields (`document_id`, `patient_key`)
- Empty or whitespace-only `patient_key`
- Annotations missing required `text` or `color` fields

At the interpreter level, `ValidationError` is raised for:

- Non-existent IntegrationTask (document_id)
- Non-existent patient (patient_key)

## Production Considerations

1. **Document Extraction**: Integrate with an LLM or OCR service to extract patient demographics from document content

2. **Patient Matching**: Implement robust patient matching logic:
   - Search by extracted demographics (name, DOB, MRN)
   - Handle fuzzy matching for name variations
   - Set confidence thresholds for auto-linking vs manual review

3. **Manual Review Workflow**: Create tasks for low-confidence matches that need human review

4. **Monitoring**: Use annotations to track extraction/matching accuracy over time

5. **Error Handling**: Implement retry logic or fallback workflows for failed matches
