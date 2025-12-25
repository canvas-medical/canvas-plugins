# Link Document to Patient Example Plugin

This example plugin demonstrates how to use the `LINK_DOCUMENT_TO_PATIENT` effect to automatically link documents in the Data Integration queue to patients based on patient demographics.

## Overview

When a document enters the Data Integration queue, this plugin:

1. Responds to the `DOCUMENT_RECEIVED` event
2. Extracts patient demographics (first name, last name, date of birth) from the document
3. Emits a `LinkDocumentToPatient` effect to link the document to the matching patient

## The LinkDocumentToPatient Effect

The `LinkDocumentToPatient` effect links a document to a patient based on demographics:

```python
from datetime import date
from canvas_sdk.effects.data_integration import LinkDocumentToPatient

effect = LinkDocumentToPatient(
    first_name="John",           # Required: patient's first name
    last_name="Doe",             # Required: patient's last name
    date_of_birth=date(1990, 5, 15),  # Required: patient's DOB
    document_id="12345",         # Required: IntegrationTask ID
    confidence_scores={          # Optional: confidence scores for monitoring
        "first_name": 0.95,
        "last_name": 0.90,
        "date_of_birth": 0.85,
    },
)

# Apply the effect
effects = [effect.apply()]
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `first_name` | str | Yes | Patient's first name (non-empty) |
| `last_name` | str | Yes | Patient's last name (non-empty) |
| `date_of_birth` | date | Yes | Patient's date of birth |
| `document_id` | str/int | Yes | The IntegrationTask ID to link |
| `confidence_scores` | dict | No | Confidence scores for each field (0.0-1.0) |

### Confidence Scores

The optional `confidence_scores` dict can include scores for:
- `first_name`
- `last_name`
- `date_of_birth`

These scores are logged for monitoring/debugging and represent the extraction confidence for each demographic field.

## Matching Logic

When the effect is processed:

1. **Patient Lookup**: Filters patients by:
   - First name (case-insensitive, trimmed)
   - Last name (case-insensitive, trimmed)
   - Date of birth (exact date match)
   - Active status (excludes inactive patients)

2. **Single Match**: If exactly one patient matches, the document is linked

3. **Zero Matches**: A `ValidationError` is raised with details about the demographics searched

4. **Multiple Matches**: A `ValidationError` is raised listing the matching patient IDs

## Usage Patterns

### Basic Auto-Linking

```python
class LinkDocumentHandler(BaseHandler):
    RESPONDS_TO = [EventType.Name(EventType.DOCUMENT_RECEIVED)]

    def compute(self) -> list[Effect]:
        document_id = self.event.target.id

        # Extract demographics from document (implement your extraction logic)
        demographics = self.extract_demographics(document_id)

        return [
            LinkDocumentToPatient(
                first_name=demographics["first_name"],
                last_name=demographics["last_name"],
                date_of_birth=demographics["date_of_birth"],
                document_id=document_id,
            ).apply()
        ]
```

### Conditional Linking with Confidence Threshold

```python
MIN_CONFIDENCE = 0.85

def compute(self) -> list[Effect]:
    document_id = self.event.target.id
    extraction = self.extract_with_llm(document_id)

    # Only auto-link if confidence is high enough
    avg_confidence = sum(extraction["confidence_scores"].values()) / 3
    if avg_confidence < MIN_CONFIDENCE:
        log.info("Confidence too low, routing to manual review")
        return []

    return [
        LinkDocumentToPatient(
            first_name=extraction["first_name"],
            last_name=extraction["last_name"],
            date_of_birth=extraction["date_of_birth"],
            document_id=document_id,
            confidence_scores=extraction["confidence_scores"],
        ).apply()
    ]
```

## Error Handling

The effect validates inputs and raises `ValidationError` for:

- Empty or whitespace-only first/last names
- Missing required fields
- Invalid date formats
- Invalid confidence score keys
- Confidence scores outside 0.0-1.0 range

At the interpreter level, `ValidationError` is raised for:

- Non-existent IntegrationTask (document_id)
- No matching patients found
- Multiple matching patients found

## Production Considerations

1. **Document Extraction**: Integrate with an LLM or OCR service to extract demographics from document content

2. **Confidence Thresholds**: Set appropriate thresholds based on your accuracy requirements

3. **Manual Review Workflow**: Create tasks for low-confidence extractions that need human review

4. **Monitoring**: Use the logged confidence scores to track extraction accuracy over time

5. **Error Handling**: Implement retry logic or fallback workflows for failed matches
