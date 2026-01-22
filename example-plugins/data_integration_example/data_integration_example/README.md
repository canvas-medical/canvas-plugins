# Data Integration Example Plugin

This example plugin demonstrates how to use Data Integration effects to process documents in the Data Integration queue.

## Overview

When a document enters the Data Integration queue, this plugin:

1. Responds to the `DOCUMENT_RECEIVED` event
2. Creates and returns Data Integration effects:
   - **LinkDocumentToPatient**: Link documents to patients using patient key
   - **AssignDocumentReviewer**: Assign a reviewer (staff or team) to documents
   - **CategorizeDocument**: Categorize documents into specific document types
   - **PrefillDocumentFields**: Prefill document fields with extracted data

3. Logs document lifecycle events (for observability):
   - `DOCUMENT_LINKED_TO_PATIENT` - When document is linked to a patient
   - `DOCUMENT_CATEGORIZED` - When document type is assigned
   - `DOCUMENT_REVIEWER_ASSIGNED` - When reviewer is assigned
   - `DOCUMENT_FIELDS_UPDATED` - When document fields change
   - `DOCUMENT_REVIEWED` - When document review is completed
   - `DOCUMENT_DELETED` - When document is soft-deleted


## Available Effects

### 1. LinkDocumentToPatient

Links a document to a patient using the patient's key. The plugin is responsible for finding/matching the patient and providing their key.

```python
from canvas_sdk.effects.data_integration import LinkDocumentToPatient
from canvas_sdk.v1.data import Patient

# Fetch patient (in production, this would come from patient matching logic)
patient = Patient.objects.first()

effect = LinkDocumentToPatient(
    document_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",  # Required: IntegrationTask UUID
    patient_key=str(patient.id),                         # Required: patient's key (32-char hex string)
    annotations=[                                        # Optional: display annotations
        {"text": "AI 95%", "color": "#00AA00"},
        {"text": "Auto-linked", "color": "#2196F3"},
    ],
    source_protocol="llm_v1",                            # Optional: protocol/plugin identifier
)
```

**Fields:**
- `document_id` (str/int, required): The IntegrationTask UUID to link
- `patient_key` (str, required): The patient's key (32-character hex string, not a UUID)
- `annotations` (list[dict], optional): Display annotations with `text` and `color` fields
- `source_protocol` (str, optional): Protocol/plugin identifier for tracking

**Behavior:**
- Looks up the patient by key
- Links the document to that patient
- Creates an IntegrationTaskPrefill record with patient data and annotations
- Raises ValidationError if patient or document doesn't exist

### 2. AssignDocumentReviewer

Assigns a reviewer (staff member or team) to a document in the Data Integration queue.

```python
from canvas_sdk.effects.data_integration import AssignDocumentReviewer, Annotation, Priority, ReviewMode

effect = AssignDocumentReviewer(
    document_id="12345",         # Required: IntegrationTask ID
    reviewer_id="staff-uuid",    # Optional: Staff member key to assign as reviewer
    team_id="team-uuid",         # Optional: Team UUID to assign as reviewer
    priority=Priority.HIGH,      # Optional: Priority level (NORMAL or HIGH), defaults to NORMAL
    review_mode=ReviewMode.REVIEW_REQUIRED,  # Optional: Review mode, defaults to REVIEW_REQUIRED
    annotations=[                # Optional: display annotations
        Annotation(text="Auto-assigned", color="#FF9800"),
        Annotation(text="Data integration", color="#2196F3"),
    ],
    source_protocol="my_plugin", # Optional: protocol/plugin identifier
)
```

**Fields:**
- `document_id` (str/int, required): The IntegrationTask ID to assign a reviewer to
- `reviewer_id` (str, optional): Staff member key to assign as reviewer. At least one of `reviewer_id` or `team_id` must be provided
- `team_id` (str, optional): Team UUID to assign as reviewer. At least one of `reviewer_id` or `team_id` must be provided
- `priority` (Priority, optional): Priority level - `Priority.NORMAL` or `Priority.HIGH`, defaults to `Priority.NORMAL`
- `review_mode` (ReviewMode, optional): Review mode - `ReviewMode.REVIEW_REQUIRED`, `ReviewMode.ALREADY_REVIEWED`, or `ReviewMode.REVIEW_NOT_REQUIRED`, defaults to `ReviewMode.REVIEW_REQUIRED`
- `annotations` (list[Annotation], optional): Display annotations with `text` and `color` fields
- `source_protocol` (str, optional): Protocol/plugin identifier for tracking

**Review Modes:**
- `REVIEW_REQUIRED`: Document requires review (default)
- `ALREADY_REVIEWED`: Document has already been reviewed
- `REVIEW_NOT_REQUIRED`: Document does not require review

**Behavior:**
- Validates the document exists
- Assigns either a staff member or team as the reviewer
- Sets the priority level for the review
- Configures the review mode based on document status
- At least one of `reviewer_id` or `team_id` must be provided

### 3. CategorizeDocument

Categorizes a document in the Data Integration queue into a specific document type.

```python
from canvas_sdk.effects.categorize_document import (
    CategorizeDocument,
    DocumentType,
    ConfidenceScores,
    AnnotationItem,
)

document_type: DocumentType = {
    "key": "lab-report-key",
    "name": "Lab Report",
    "report_type": "LAB",
    "template_type": "lab_template",  # Optional
}

confidence_scores: ConfidenceScores = {
    "document_id": 0.90,
    "document_type": {
        "key": 0.90,
        "name": 0.95,
        "report_type": 0.85,
    },
}

annotations: list[AnnotationItem] = [
    {"text": "AI 90%", "color": "#00AA00"},
    {"text": "Data integration", "color": "#2196F3"},
]

effect = CategorizeDocument(
    document_id="12345",
    document_type=document_type,
    confidence_scores=confidence_scores,
    annotations=annotations,
    source_protocol="data_integration_example_v1",
)
```

**Fields:**
- `document_id` (str/int, required): The IntegrationTask ID to categorize
- `document_type` (DocumentType, required): The document type to assign, containing:
  - `key` (str): Unique key for the document type
  - `name` (str): Display name
  - `report_type` (str): Report type code (e.g., "LAB", "RADIOLOGY")
  - `template_type` (str, optional): Template type identifier
- `confidence_scores` (ConfidenceScores, optional): Confidence scores for monitoring
- `annotations` (list[AnnotationItem], optional): Display annotations
- `source_protocol` (str, optional): Protocol/plugin identifier

**Behavior:**
- Validates the document exists
- Assigns the document type to the document
- Stores confidence scores and annotations for display

### 4. PrefillDocumentFields

Prefills document fields with extracted data (e.g., from OCR or LLM processing).

```python
from canvas_sdk.effects.data_integration import PrefillDocumentFields

templates = [
    {
        "template_id": 620,
        "template_name": "Thyroid Profile With Tsh",
        "fields": {
            "11580-8": {  # LOINC code for TSH
                "value": "2.35",
                "unit": "uIU/mL",
                "reference_range": "0.45 - 4.50 uIU/mL",
                "annotations": [{"text": "AI 92%", "color": "#4CAF50"}],
            },
            "3026-2": {  # LOINC code for T4
                "value": "7.8",
                "unit": "ug/dL",
                "reference_range": "4.5 - 12.0 ug/dL",
                "annotations": [{"text": "AI 89%", "color": "#4CAF50"}],
            },
        },
    }
]

annotations = [
    {"text": "1 template matched", "color": "#2196F3"},
    {"text": "2 fields extracted", "color": "#00BCD4"},
]

effect = PrefillDocumentFields(
    document_id="12345",
    templates=templates,
    annotations=annotations,
)
```

**Fields:**
- `document_id` (str/int, required): The IntegrationTask ID to prefill
- `templates` (list[dict], required): List of templates with fields to prefill:
  - `template_id` (int): Template identifier
  - `template_name` (str): Template display name
  - `fields` (dict): Field data keyed by LOINC code or field label:
    - `value` (str, required): The extracted value
    - `unit` (str, optional): Unit of measurement
    - `reference_range` (str, optional): Reference range
    - `abnormal` (bool, optional): Whether value is abnormal
    - `annotations` (list[dict], optional): Field-level annotations
- `annotations` (list[dict], optional): Top-level annotations for the prefill

**Behavior:**
- Validates the document exists
- Creates or updates IntegrationTaskPrefill record
- Stores templates with extracted field values
- Supports both LOINC codes and field labels as keys


## How It Works

1. When a document is received (`DOCUMENT_RECEIVED` event), the `DataIntegrationHandler` is triggered
2. The handler creates effects for:
   - **LinkDocumentToPatient**: Fetches first available patient (in production, would use patient matching)
   - **AssignDocumentReviewer**: Fetches first available staff/team for assignment
   - **CategorizeDocument**: Uses `available_document_types` from event context
   - **PrefillDocumentFields**: Creates sample lab result prefill data
3. Returns a list of effects to apply
4. Document lifecycle events are logged for observability

## Implementation Notes

This is an **example plugin** that demonstrates the structure and usage of Data Integration effects. In a production implementation, you would:

1. **Match Patient** (for `LinkDocumentToPatient`):
   - Fetch the document content
   - Use an LLM or OCR system to extract patient demographics from the document
   - Use the extracted demographics to find matching patients in the system
   - Once matched, pass the patient's `patient_key` to the effect
   - Implement retry logic or manual review workflows for ambiguous matches

2. **Categorize Documents** (for `CategorizeDocument`):
   - Analyze the document content
   - Use an LLM or classification model to determine document type
   - Return confidence scores for monitoring/debugging

3. **Extract Fields** (for `PrefillDocumentFields`):
   - Use OCR or LLM to extract structured data from documents
   - Match extracted fields to template fields using LOINC codes or labels
   - Include confidence scores at the field level

4. **Assign Reviewers** (for `AssignDocumentReviewer`):
   - Determine appropriate reviewer based on document type, specialty, or workload
   - Assign to staff member or team based on routing rules
   - Set priority level based on document urgency
   - Configure review mode based on document status

## Annotations

All effects support annotations for display in the UI:

```python
annotations = [
    {"text": "AI 95%", "color": "#4CAF50"},
    {"text": "Auto-linked", "color": "#2196F3"},
    {"text": "Verify", "color": "#FF9800"},
    {"text": "Low confidence", "color": "#F44336"},
]
```

## Testing

To test this plugin:

1. Ensure the plugin is registered in your Canvas instance
2. Send a `DOCUMENT_RECEIVED` event with a document
3. Verify the appropriate effects are applied
4. Check the logs for document lifecycle event handling
